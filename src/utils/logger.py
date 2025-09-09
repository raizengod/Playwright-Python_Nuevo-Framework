import logging
import os
from datetime import datetime
from .config import LOGGER_DIR # Importa la ruta del directorio de logs desde config.py

def setup_logger(name='playwright_automation', console_level=logging.INFO, file_level=logging.DEBUG):
    """
    Configura y devuelve una instancia de logger para el framework de automatización,
    permitiendo niveles de logging separados para consola y archivo.

    Args:
        name (str): El nombre del logger. Por defecto, 'playwright_automation'.
        console_level (int): El nivel mínimo de logging para los mensajes que se muestran en la consola.
                             Por defecto, logging.INFO.
        file_level (int): El nivel mínimo de logging para los mensajes que se escriben en el archivo.
                          Por defecto, logging.DEBUG.

    Returns:
        logging.Logger: Una instancia del logger configurado.
    """
    # 1. Obtener o crear una instancia del logger
    logger = logging.getLogger(name)

    # 2. Establecer el nivel mínimo para el logger. Este será el nivel más bajo (más detallado)
    # de los dos niveles de los handlers, para asegurar que todos los mensajes estén disponibles.
    logger.setLevel(min(console_level, file_level))

    # 3. Evitar que los logs se propaguen a handlers de loggers padre, lo que evita duplicación
    logger.propagate = False

    # 4. Limpiar handlers existentes para evitar duplicación si la función se llama varias veces
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # 5. Definir el formato de los mensajes de log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # 6. Configurar el handler para la consola (StreamHandler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level) # Nivel de log específico para la consola
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 7. Configurar el handler para el archivo (FileHandler)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file_name = f"automation_log_{timestamp}.log"
    log_file_path = os.path.join(LOGGER_DIR, log_file_name)

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(file_level) # Nivel de log específico para el archivo
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

"""# --- Ejemplo de uso (opcional, para testing rápido del logger) ---
if __name__ == "__main__":
    from config import ensure_directories_exist
    ensure_directories_exist() 

    print("\n--- Probando Logger con Nivel INFO en Consola y DEBUG en Archivo ---")
    my_logger_1 = setup_logger(name='test_logger_1', console_level=logging.INFO, file_level=logging.DEBUG)
    my_logger_1.debug("DEBUG message - Should be in file, not console.")
    my_logger_1.info("INFO message - Should be in console and file.")
    my_logger_1.warning("WARNING message - Should be in console and file.")
    my_logger_1.error("ERROR message - Should be in console and file.", exc_info=True)
    my_logger_1.critical("CRITICAL message - Should be in console and file.")

    print("\n--- Probando Logger con Nivel WARNING en Consola y INFO en Archivo ---")
    my_logger_2 = setup_logger(name='test_logger_2', console_level=logging.WARNING, file_level=logging.INFO)
    my_logger_2.debug("DEBUG message 2 - Should only be in file (if file_level=DEBUG or lower).") # Won't be in this file.
    my_logger_2.info("INFO message 2 - Should be in file, not console.")
    my_logger_2.warning("WARNING message 2 - Should be in console and file.")
    my_logger_2.error("ERROR message 2 - Should be in console and file.")

    print(f"\nLogs guardados en: {LOGGER_DIR}")"""