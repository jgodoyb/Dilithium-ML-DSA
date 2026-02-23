# Q-Proof System

Bienvenido a **Q-Proof System**, una aplicación de vanguardia diseñada para la firma digital de documentos y la verificación de identidad utilizando criptografía **Post-Cuántica**. 

Este sistema implementa el estándar **ML-DSA (FIPS 204)**, garantizando que las firmas digitales producidas sean resistentes incluso a ataques de futuros ordenadores cuánticos.

## ✨ Características Principales

*   **Criptografía Post-Cuántica Integrada:** Implementación nativa en Python del algoritmo de firma digital ML-DSA basado en retículos (Lattice-based cryptography).
*   **Gestión Segura de Identidades:** Registro de usuarios, inicio de sesión seguro y gestión de perfiles.
*   **Almacenamiento Local Seguro de Claves:** 
    *   Las claves privadas **nunca** se almacenan en texto plano. 
    *   Se cifran localmente utilizando **AES-128 (modo CBC a través de Fernet)**.
    *   La clave de cifrado se deriva de la contraseña del usuario utilizando el estándar robusto **PBKDF2-HMAC-SHA256** con más de 260,000 iteraciones (recomendación OWASP 2024).
*   **Recuperación Segura de Cuenta:** Sistema de recuperación de claves basado en tokens vía correo electrónico (OTP), utilizando una copia de seguridad cifrada con una clave derivada del e-mail del usuario.
*   **Interfaz de Usuario Moderna:** Interfaz web interactiva y accesible, construida sobre **Streamlit** (requiere versión >=1.30.0).

---

## 🔒 Arquitectura de Seguridad

La seguridad de datos en reposo es una prioridad en Q-Proof System. El esquema de base de datos protege fuertemente todas las credenciales:

1.  **Contraseñas:** No se guardan. Se genera y almacena un Hash irreversíble usando SHA-256 junto con una **Sal (Salt)** aleatoria de 16 bytes.
2.  **Claves Privadas (Firma):** Se cifran con la contraseña del usuario. Si la base de datos es extraída ilegítimamente, las claves privadas son inútiles sin conocer las contraseñas exactas de cada usuario.
3.  **Claves Públicas:** Almacenadas en formato Base64 para facilitar su distribución y utilización en los procesos de verificación pública.

---

## 🚀 Instalación y Ejecución

### 1. Requisitos Previos

Asegúrate de tener instalado **Python 3.10** o superior en tu sistema.

### 2. Instalación de Dependencias

Se recomienda la creación de un entorno virtual (venv o conda) antes de instalar las dependencias.

```bash
# Clonar o descargar el repositorio e ir a la carpeta principal
cd "Q-Proof System"

# Instalar los paquetes requeridos
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación Web

La aplicación de interfaz de usuario está desarrollada en Streamlit. Para levantar el servidor y abrir la aplicación en tu navegador, ejecuta el siguiente comando desde el directorio principal del proyecto:

```bash
streamlit run app_web.py
```

Esto abrirá por defecto una ventana en tu navegador en `http://localhost:8501`.

---

## 📁 Estructura del Proyecto

*   `app_web.py`: Punto de entrada principal que inicializa e invoca el servidor Streamlit.
*   `qproof_es.db`: Base de datos SQLite (generada automáticamente) que almacena de forma segura los usuarios, credenciales hasheadas y las claves privadas cifradas.
*   `requirements.txt`: Archivo con las dependencias necesarias de bibliotecas Python (`streamlit`, `cryptography`, etc.).
*   `web/`:
    *   `main.py`: Rutas y lógica general de las pantallas en la interfaz de Streamlit.
    *   `auth.py`: Lógica para autenticación de usuarios y generación de material criptográfico (manejo de Sal y derivación de base de datos).
    *   `crypto.py`: Operaciones centralizadas de encriptación (Derivación PBKDF2, Hashes, Validaciones de contraseñas de alta entropía).
    *   `db.py`: Conexión de SQLite e inicialización del esquema de la base de datos segura.
    *   `email_sender.py`: Lógica para el envío de códigos OTP y correos de recuperación.
    *   `views.py`, `config.py`, etc.: Vistas secundarias y configuraciones globales para Streamlit.
*   `mldsa/`: Implementación core de matemáticas post-cuánticas bajo FIPS 204.

---

**Nota:** Q-Proof System es un sistema de grado de investigación/estudio de la criptografía moderna aplicable. Usa la capa de transporte seguro (HTTPS) en entornos de producción.
