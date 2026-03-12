import os
import sys

# Permitir importar módulos desde el directorio raíz (como 'mldsa')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base64
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from typing import Annotated

from mldsa.mldsa import keygen, hash_sign, hash_verify

app = FastAPI()

# Procesar orígenes permitidos desde el .env (soporta múltiples separados por coma)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "")
ALLOWED_ORIGINS = [origin.strip() for origin in FRONTEND_URL.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_JWKS_URL = os.environ.get("SUPABASE_JWKS_URL", "")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

security = HTTPBearer()
jwks_client = jwt.PyJWKClient(SUPABASE_JWKS_URL, cache_keys=True)

async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Security(security)]) -> dict:
    if ENVIRONMENT == "test":
        return {"sub": "test-user-123", "aud": "authenticated"}
    
    token = credentials.credentials
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated"
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Invalid audience")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        print(f"Error interno en auth: {str(e)}") # Para ver el error real en la consola de tu servidor
        raise HTTPException(status_code=500, detail="Internal authentication error")

@app.post("/api/generate")
async def generate_keys(token_payload: dict = Depends(get_current_user)):
    try:
        user_id = token_payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing subject claim")
        pk, sk = keygen()
        
        pk_b64 = base64.b64encode(pk).decode('utf-8')
        sk_b64 = base64.b64encode(sk).decode('utf-8')
        
        data = {
            "user_id": user_id,
            "public_key": pk_b64,
            "private_key": sk_b64
        }
        
        # Inserción o actualización en Supabase
        if supabase:
            supabase.table("crypto_identities").upsert(data).execute()
        
        return {"status": "success", "message": "Keys generated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sign")
async def sign_document(
    file: UploadFile = File(...),
    token_payload: dict = Depends(get_current_user)
):
    try:
        user_id = token_payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing subject claim")
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")
            
        response = supabase.table("crypto_identities").select("private_key").eq("user_id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Private key not found for user")
            
        sk_b64 = response.data[0]["private_key"]
        sk_bytes = base64.b64decode(sk_b64)
        
        pdf_bytes = await file.read()
        
        signature_bytes = hash_sign(sk=sk_bytes, M=pdf_bytes, ph_algo="SHA-256", ctx=b"Q-Proof")
        signature_b64 = base64.b64encode(signature_bytes).decode('utf-8')
        
        return {"signature_b64": signature_b64}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/verify")
async def verify_document(
    file: UploadFile = File(...),
    signature_b64: str = Form(...),
    author_id: str = Form(...),
    token_payload: dict = Depends(get_current_user)
):
    try:
        user_id = token_payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token missing subject claim")
        if not supabase:
            raise HTTPException(status_code=500, detail="Supabase client not initialized")
            
        response = supabase.table("crypto_identities").select("public_key").eq("user_id", author_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Public key not found for author")
            
        pk_b64 = response.data[0]["public_key"]
        pk_bytes = base64.b64decode(pk_b64)
        
        signature_bytes = base64.b64decode(signature_b64)
        pdf_bytes = await file.read()
        
        is_valid = hash_verify(pk=pk_bytes, M=pdf_bytes, sigma=signature_bytes, ph_algo="SHA-256", ctx=b"Q-Proof")
        
        return {"is_valid": is_valid}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
