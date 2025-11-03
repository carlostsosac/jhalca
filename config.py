# config.py
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Carga variables desde .env si existieran (opcional)
load_dotenv()

# ===== CONFIGURACIÓN DE CONEXIÓN A LA BASE DE DATOS (PostgreSQL) =====
# Asegúrate de haber instalado el driver con: pip install psycopg2-binary

# Render y otros servicios de hosting configuran DATABASE_URL automáticamente.
# Para desarrollo local, puedes configurar una URL de PostgreSQL en tu archivo .env
# Ejemplo para .env:
# DATABASE_URL="postgresql://user:password@localhost/jhalca"

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

# Si DATABASE_URL no está definida (desarrollo local sin .env), se puede construir una:
if not SQLALCHEMY_DATABASE_URI:
    driver = os.getenv("DB_DRIVER", "postgresql+psycopg2")
    server = os.getenv("DB_SERVER", "dpg-d44ah1a4d50c738891pg-a")
    database = os.getenv("DB_NAME", "jhalca")
    username = os.getenv("DB_USER", "jhalca_user") # Usuario común en postgres
    password = os.getenv("DB_PASSWORD", "M8rDEkFHSQLQqV9z1bTBYpNPZcCL2hcQ") # Cambiar por tu clave
    SQLALCHEMY_DATABASE_URI = f"{driver}://{username}:{quote_plus(password)}@{server}/{database}"

# ===== CONFIGURACIÓN DE FLASK =====
SECRET_KEY = os.getenv("SECRET_KEY", "una-clave-secreta-muy-fuerte-que-debes-cambiar")
SQLALCHEMY_TRACK_MODIFICATIONS = False
PDF_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'pdfs')
