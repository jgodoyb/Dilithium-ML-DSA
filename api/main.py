import os
import base64
import jwt
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from typing import Annotated

from mldsa.mldsa import keygen, hash_sign, hash_verify

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

security = HTTPBearer()

async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Security(security)]) -> str:
    if ENVIRONMENT == "test":
        return "test-user-123"
    
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"], 
            options={"verify_aud": False}
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub claim")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/api/generate")
async def generate_keys(user_id: str = Depends(get_current_user)):
    try:
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
    user_id: str = Depends(get_current_user)
):
    try:
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
    user_id: str = Depends(get_current_user)
):
    try:
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
