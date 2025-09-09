import os
import dotenv

# Obtiene la ruta absoluta del directorio donde se encuentra este archivo config.py
# Esto resultará en algo como '.../PRACTICA-RV/PRV/utils'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Navega un nivel arriba para llegar a la raíz de tu paquete principal 'practice'
# CURRENT_DIR = '.../PRACTICA-RV/PRV/utils'
# os.path.dirname(CURRENT_DIR) = '.../PRACTICA-RV/PRV'
PROJECT_ROOT = os.path.dirname(CURRENT_DIR) 

# --- Agregando la lógica de manejo de ambientes ---
# 1. Define la ruta a la carpeta de entornos
ENVIRONMENTS_DIR = os.path.join(PROJECT_ROOT, "environments")

# 2. Obtiene el nombre del ambiente desde una variable de entorno de sistema
#    Si no se especifica, usa 'qa' como ambiente por defecto.
ENVIRONMENT = os.getenv("ENVIRONMENT", "qa")

# 3. Construye la ruta al archivo .env específico del ambiente
dotenv_file = os.path.join(ENVIRONMENTS_DIR, f"{ENVIRONMENT}.env")

# 4. Carga las variables de entorno desde el archivo .env
#    Si el archivo no existe, lo notifica pero continúa (útil para CI/CD)
if os.path.exists(dotenv_file):
    dotenv.load_dotenv(dotenv_file)
else:
    print(f"Advertencia: No se encontró el archivo de entorno '{dotenv_file}'. Usando variables de entorno del sistema.")

# --- Configuración de URLs - Ahora se leen de las variables de entorno ---
# Se utiliza .get() para evitar errores si la variable no existe
BASE_URL = os.getenv("BASE_URL")
MAKE_URL = os.getenv("MAKE_URL")
POPULAR_URL = os.getenv("POPULAR_URL")
OVERALL_URL = os.getenv("OVERALL_URL")
REGISTRAR_URL = os.getenv("REGISTRAR_URL")
DASHBOARD_URL = os.getenv("DASHBOARD_URL")

# Si necesitas una URL para APIs, la cargas de la misma manera
API_URL = os.getenv("API_URL")

# --- Rutas de Almacenamiento de Evidencias ---

# Directorio base donde se guardarán todas las evidencias.
# Construye la ruta absoluta para que apunte a '.../PRACTICA-RV/PRV/test/reports'
EVIDENCE_BASE_DIR = os.path.join(PROJECT_ROOT, "test", "reports")

# Ruta para videos.
# Se creará '.../PRACTICA-RV/PRV/test/reportes/video'
VIDEO_DIR = os.path.join(EVIDENCE_BASE_DIR, "video")

# Ruta para traceview.
# Se creará '.../PRACTICA-RV/PRV/test/reportes/traceview'
TRACEVIEW_DIR = os.path.join(EVIDENCE_BASE_DIR, "traceview")

# Ruta para capturas de pantalla.
# Se creará '.../PRACTICA-RV/PRV/test/reportes/imagen'
SCREENSHOT_DIR = os.path.join(EVIDENCE_BASE_DIR, "imagen")

# Ruta para logger.
# Se creará '.../PRACTICA-RV/PRV/test/reportes/log'
LOGGER_DIR = os.path.join(EVIDENCE_BASE_DIR, "log")

# --- Nueva ruta para archivos fuente ---
# Se creará '.../.../src/test/archivos_data_escritura'
SOURCE_FILES_DIR_DATA_WRITE = os.path.join(PROJECT_ROOT, "test", "files", "files_data_write")

# Se creará '.../.../src/test/archivos_data_fuente'
SOURCE_FILES_DIR_DATA_SOURCE = os.path.join(PROJECT_ROOT, "test", "files", "files_data_source")

# Se creará '.../.../src/test/archivos_upload'
SOURCE_FILES_DIR_UPLOAD = os.path.join(PROJECT_ROOT, "test", "files", "files_upload")

# Se creará '.../.../src/test/archivos_download'
SOURCE_FILES_DIR_DOWNLOAD = os.path.join(PROJECT_ROOT, "test", "files", "files_download")

# Función para asegurar que los directorios existan
def ensure_directories_exist():
    """
    Crea los directorios necesarios si no existen.
    """
    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(TRACEVIEW_DIR, exist_ok=True)
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(SOURCE_FILES_DIR_DATA_WRITE, exist_ok=True)
    os.makedirs(SOURCE_FILES_DIR_DATA_SOURCE, exist_ok=True)
    os.makedirs(SOURCE_FILES_DIR_UPLOAD, exist_ok=True)
    os.makedirs(SOURCE_FILES_DIR_DOWNLOAD, exist_ok=True)
    os.makedirs(LOGGER_DIR, exist_ok=True)
    print(f"Directorios verificados/creados: {EVIDENCE_BASE_DIR}, \
        {SOURCE_FILES_DIR_UPLOAD}, \
            {SOURCE_FILES_DIR_DOWNLOAD}, \
                {LOGGER_DIR}, \
                    {SOURCE_FILES_DIR_DATA_SOURCE}, \
                        {SOURCE_FILES_DIR_DATA_WRITE}")


# Llama a la función para asegurar que los directorios se creen al importar este módulo
ensure_directories_exist()