# src/examples/ejemplo_uso.py
import sys
import os

# Asegurar que el proyecto sea importable desde la carpeta examples
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ruta_raiz not in sys.path:
    sys.path.insert(0, ruta_raiz)

# ¡Mira qué importación más limpia gracias a tu arquitectura!
import mldsa

def main():
    print("="*60)
    print(" 🛡️ SISTEMA DE FIRMA POST-CUÁNTICA ML-DSA (FIPS 204) 🛡️")
    print("="*60)

    # ---------------------------------------------------------
    # 1. GENERACIÓN DE CLAVES
    # ---------------------------------------------------------
    print("\n[1] Alice está generando sus claves post-cuánticas...")
    # Alice ejecuta el KeyGen. El sistema usa aleatoriedad del S.O.
    pk_alice, sk_alice = mldsa.keygen()
    print(f"    ✓ Claves generadas con éxito.")
    print(f"    -> Tamaño Clave Pública: {len(pk_alice)} bytes")
    print(f"    -> Tamaño Clave Privada: {len(sk_alice)} bytes")

    # ---------------------------------------------------------
    # 2. FIRMA DE UN MENSAJE CORTO (Firma Pura)
    # ---------------------------------------------------------
    mensaje = b"Autorizo la transferencia de 50.000 EUR a la cuenta de Bob."
    contexto_bancario = b"Operaciones Bancarias 2026"
    
    print("\n[2] Alice firma una orden de transferencia bancaria...")
    print(f"    Mensaje: '{mensaje.decode('utf-8')}'")
    
    firma_transferencia = mldsa.sign(sk_alice, mensaje, ctx=contexto_bancario)
    print(f"    ✓ Firma generada. Tamaño: {len(firma_transferencia)} bytes")

    # Bob recibe el mensaje y la firma, y procede a verificar
    print("\n[3] El Banco (Bob) verifica la firma de Alice...")
    es_valida = mldsa.verify(pk_alice, mensaje, firma_transferencia, ctx=contexto_bancario)
    
    if es_valida:
        print("    ✅ VERIFICACIÓN EXITOSA: La orden es auténtica y proviene de Alice.")
    else:
        print("    ❌ ALERTA: La firma es inválida.")

    # ---------------------------------------------------------
    # 3. FIRMA DE UN DOCUMENTO GIGANTE (Pre-Hash / HashML-DSA)
    # ---------------------------------------------------------
    print("\n[4] Alice necesita firmar un contrato PDF de 500 MB...")
    # En lugar de cargar 500MB en la memoria de la firma, simulamos el archivo
    simulacion_pdf_gigante = b"%PDF-1.4... [500 Megabytes de datos legales] ...%%EOF"
    contexto_legal = b"Contratos Inmobiliarios"
    
    print("    Usando la variante HashML-DSA con SHA-256 para mayor eficiencia.")
    firma_pdf = mldsa.hash_sign(sk_alice, simulacion_pdf_gigante, ph_algo="SHA-256", ctx=contexto_legal)
    print(f"    ✓ Firma del PDF generada.")

    # El notario verifica el PDF
    print("\n[5] El Notario verifica la firma del contrato PDF...")
    es_pdf_valido = mldsa.hash_verify(pk_alice, simulacion_pdf_gigante, firma_pdf, ph_algo="SHA-256", ctx=contexto_legal)
    
    if es_pdf_valido:
        print("    ✅ VERIFICACIÓN EXITOSA: El contrato es auténtico y no ha sido alterado.")

    # ---------------------------------------------------------
    # 4. SIMULACIÓN DE UN ATAQUE HACKER
    # ---------------------------------------------------------
    print("\n[6] 🚨 Un atacante intercepta la transferencia bancaria e intenta cambiar el importe...")
    mensaje_hackeado = b"Autorizo la transferencia de 99.000 EUR a la cuenta de Eve."
    
    print(f"    Mensaje alterado: '{mensaje_hackeado.decode('utf-8')}'")
    print("    El Banco verifica la firma original de Alice contra el mensaje alterado...")
    
    es_valida_hack = mldsa.verify(pk_alice, mensaje_hackeado, firma_transferencia, ctx=contexto_bancario)
    
    if not es_valida_hack:
        print("    🛡️ ATAQUE BLOQUEADO: La criptografía detectó la manipulación. Transacción denegada.")
    else:
        print("    ❌ ERROR CRÍTICO: El ataque tuvo éxito.")
        
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()