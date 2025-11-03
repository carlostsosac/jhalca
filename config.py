# config.py
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Carga variables desde .env si existieran (opcional)
load_dotenv()

# ===== CONFIGURACIÓN DE CONEXIÓN A LA BASE DE DATOS (MySQL) =====
# Asegúrate de haber instalado el driver con: pip install PyMySQL
driver = os.getenv("DB_DRIVER", "pymysql")
server = os.getenv("DB_SERVER", "localhost")
database = os.getenv("DB_NAME", "jhalca")
username = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "771510")

# URL de conexión SQLAlchemy
# En producción, se recomienda usar una variable de entorno completa para la URI.
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"mysql+{driver}://{username}:{quote_plus(password)}@{server}/{database}")

# ===== CONFIGURACIÓN DE FLASK =====
SECRET_KEY = os.getenv("SECRET_KEY", "una-clave-secreta-muy-fuerte-que-debes-cambiar")
SQLALCHEMY_TRACK_MODIFICATIONS = False
PDF_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'pdfs')
