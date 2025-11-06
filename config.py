# config.py
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Carga variables desde .env si existieran (opcional)
load_dotenv()

# ===== CONFIGURACIÓN DE CONEXIÓN A LA BASE DE DATOS (MySQL) =====
# Asegúrate de haber instalado el driver con: pip install pymysql

# Render y otros servicios de hosting configuran DATABASE_URL automáticamente.
# Para desarrollo local, puedes configurar una URL de MySQL en tu archivo .env
# Ejemplo para .env:
# DATABASE_URL="mysql+pymysql://user:password@localhost/jhalca"

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

# Si DATABASE_URL no está definida (desarrollo local sin .env), se puede construir una:
if not SQLALCHEMY_DATABASE_URI:
    # Para hosting en servicios como InfinityFree, es mejor configurar DATABASE_URL
    # en su panel de control. Estos valores predeterminados son para desarrollo local.
    db_user = os.getenv("DB_USER", "ifO_40344670") # Reemplaza con tu usuario de BD
    db_password = os.getenv("DB_PASSWORD", "Js771510") # Reemplaza con tu contraseña de BD
    db_host = os.getenv("DB_HOST", "sql305.infinityfree.com") # Reemplaza con tu host de BD
    db_name = os.getenv("DB_NAME", "ifO_40344670_your_db_name") # <-- IMPORTANTE: Reemplaza con el nombre real de tu BD
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{db_user}:{quote_plus(db_password)}@{db_host}/{db_name}"

# ===== CONFIGURACIÓN DE FLASK =====
SECRET_KEY = os.getenv("SECRET_KEY", "una-clave-secreta-muy-fuerte-que-debes-cambiar")
SQLALCHEMY_TRACK_MODIFICATIONS = False
# ===== CONFIGURACIÓN DE SQLAlchemy Pool (Importante para hosting) =====
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_recycle': 280,  # Recicla las conexiones para evitar timeouts del servidor
    'pool_pre_ping': True # Verifica que la conexión esté activa antes de usarla
}

PDF_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'pdfs')
