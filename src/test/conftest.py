# nombra el archivo: Ve a la ubicación de tu archivo y colcoar el nombre a conftest.py
# La convención de conftest.py le indica a Pytest que este archivo contiene fixtures que deben estar disponibles 
# para los tests en ese directorio y sus subdirectorios.
import pytest
import time
from playwright.sync_api import Page, expect, Playwright, sync_playwright
from datetime import datetime
import os
from typing import Generator
from src.utils import config
#from src.utils.config import BASE_URL
from src.pages.base_page import BasePage
from src.locator.locator_obstaculoPantalla import ObstaculosLocators

# Función para generar IDs legibles
def generar_ids_browser(param):
    """
    Genera un ID descriptivo para cada combinación de navegador y dispositivo.
    """
    browser = param['browser']
    device = param['device']
    resolution = param['resolution']

    if device:
        return f"{browser}-{device}"
    else:
        return f"{browser}-{resolution['width']}x{resolution['height']}"

@pytest.fixture(
    scope="function",
    params=[
            # Resoluciones de escritorio
            {"browser": "chromium", "resolution": {"width": 1920, "height": 1080}, "device": None},
            #{"browser": "firefox", "resolution": {"width": 1920, "height": 1080}, "device": None},
            #{"browser": "webkit", "resolution": {"width": 1920, "height": 1080}, "device": None},
            # Emulación de dispositivos móviles
            #{"browser": "chromium", "device": "iPhone 12", "resolution": None},
            #{"browser": "webkit", "device": "Pixel 5", "resolution": None},
            #{"browser": "webkit", "device": "iPhone 12", "resolution": None}
    ],
    ids=generar_ids_browser # <--- Usar la función para generar IDs
)
def playwright_page(playwright: Playwright, request) -> Generator[Page, None, None]:
    """
    Fixture base para configurar el navegador, contexto y página de Playwright con configuraciones comunes.
    Maneja el lanzamiento del navegador, la creación del contexto (con grabación de video y emulación de dispositivos),
    el rastreo (tracing) y la navegación de la página a una URL específica. También renombra el archivo de video al finalizar.
    """
    param = request.param
    browser_type = param["browser"]
    resolution = param["resolution"]
    device_name = param["device"]

    browser_instance = None
    context = None
    page = None

    try:
        if browser_type == "chromium":
            browser_instance = playwright.chromium.launch(headless=True, slow_mo=500)
        elif browser_type == "firefox":
            browser_instance = playwright.firefox.launch(headless=True, slow_mo=500)
        elif browser_type == "webkit":
            browser_instance = playwright.webkit.launch(headless=True, slow_mo=500)
        else:
            raise ValueError(f"\nEl tipo de navegador '{browser_type}' no es compatible.")

        context_options = {
            "record_video_dir": config.VIDEO_DIR,
            "record_video_size": {"width": 1920, "height": 1080}
        }

        if device_name:
            device = playwright.devices[device_name]
            context = browser_instance.new_context(**device, **context_options)
        elif resolution:
            context = browser_instance.new_context(viewport=resolution, **context_options)
        else:
            context = browser_instance.new_context(**context_options)

        page = context.new_page()

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_name_suffix = ""
        if device_name:
            trace_name_suffix = device_name.replace(" ", "_").replace("(", "").replace(")", "")
        elif resolution:
            trace_name_suffix = f"{resolution['width']}x{resolution['height']}"

        trace_file_name = f"traceview_{current_time}_{browser_type}_{trace_name_suffix}.zip"
        trace_path = os.path.join(config.TRACEVIEW_DIR, trace_file_name)

        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        yield page

    finally:
        if context:
            context.tracing.stop(path=trace_path)
            context.close()
            
        if browser_instance:
            browser_instance.close()
            
        if page and page.video:
            video_path = page.video.path()
            new_video_name = datetime.now().strftime("%Y%m%d-%H%M%S") + ".webm"
            new_video_path = os.path.join(config.VIDEO_DIR, new_video_name)
            try:
                os.rename(video_path, new_video_path)
                print(f"\nVideo guardado como: {new_video_path}")
            except Exception as e:
                print(f"\nError al renombrar el video: {e}")
                
# --- Fixture principal de la arquitectura ---
@pytest.fixture(scope="function")
def base_page(playwright_page: Page) -> BasePage:
    """
    Fixture que inicializa la clase BasePage con el objeto 'page' de Playwright.
    Esto proporciona acceso a todas las clases de acciones (elementos, tablas, etc.)
    en cada test que lo requiera.
    """
    return BasePage(playwright_page)

# --- Ejemplo de nuevos fixtures de pre-condición ---
@pytest.fixture
def set_up_Home(base_page: BasePage) -> BasePage:
    """
    Fixture de pre-condición para las pruebas en la página de inicio.
    
    Este fixture garantiza que la página esté en un estado conocido y limpio
    antes de que cada test de la página de inicio comience. Realiza las siguientes acciones:
    
    1. Navega a la URL base de la aplicación.
    2. Valida que la URL actual coincida con la URL base esperada.
    3. Cierra cualquier obstáculo o popup (como banners de cookies o anuncios) que
       puedan interferir con la ejecución del test.
    4. Valida que el título de la página sea el correcto.

    Args:
        base_page (BasePage): Una instancia de la clase BasePage, que se espera
                              sea proporcionada por otro fixture de nivel superior
                              (como el fixture `page` de Playwright).

    Returns:
        BasePage: La instancia de BasePage ya inicializada y configurada, lista para
                  ser utilizada por el test para realizar las validaciones o acciones.
    """
    # 1. Navega a la URL base y toma una captura de pantalla inicial.
    base_page.navigation.ir_a_url(config.BASE_URL, "inicio_test", config.SCREENSHOT_DIR)
    
    # 2. Valida que la URL actual sea la de la página de inicio.
    base_page.navigation.validar_url_actual(config.BASE_URL)
    
    # 3. Intenta cerrar cualquier obstáculo que pueda aparecer.
    #    Esto asegura que los elementos principales de la página no estén cubiertos.
    base_page.element.manejar_obstaculos_en_pagina(ObstaculosLocators.LISTA_DE_OBSTACULOS)
    
    # 4. Valida que el título de la web sea el esperado, confirmando que la página cargó correctamente.
    base_page.navigation.validar_titulo_de_web("Buggy Cars Rating", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # Retorna la instancia de BasePage para que el test pueda comenzar sus acciones.
    return base_page

@pytest.fixture
def set_up_Registrar(base_page: BasePage):
    """
    Fixture que prepara el entorno de la prueba para escenarios de registro.
    
    Este fixture realiza los siguientes pasos de pre-condición:
    1. Navega a la URL base de la aplicación.
    2. Hace clic en el botón 'Register' para ir a la página de registro.
    3. Valida que la URL actual sea la esperada para la página de registro.
    4. Maneja cualquier obstáculo o popup que pueda aparecer en la página.
    5. Valida que el título de la página sea el correcto.

    Args:
        base_page (BasePage): Una instancia de la clase BasePage proporcionada por
                              un fixture de nivel superior (precondición necesaria).

    Returns:
        BasePage: La instancia de BasePage ya inicializada y lista para interactuar
                  con la página de registro.
    """
    # 1. Navega a la URL base de la aplicación.
    base_page.navigation.ir_a_url(config.BASE_URL, "Inicio_test_registro", config.SCREENSHOT_DIR)
    
    # 2. Hace clic en el botón 'Register' para ir a la página de registro.
    #    Se utiliza el localizador desde la instancia de HomeLocatorsPage.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonRegistrarse, "Clic_botonRegistrarse", config.SCREENSHOT_DIR)
    
    # 3. Valida que la URL actual sea la de la página de registro.
    base_page.navigation.validar_url_actual(config.REGISTRAR_URL)
    
    # 4. Maneja cualquier obstáculo en la página (popups, banners, etc.).
    base_page.element.manejar_obstaculos_en_pagina(ObstaculosLocators.LISTA_DE_OBSTACULOS)
    
    # 5. Valida que el título de la página sea el correcto para asegurar que la navegación fue exitosa.
    base_page.navigation.validar_titulo_de_web("Buggy Cars Rating", "validar_titulo_de_web_registro", config.SCREENSHOT_DIR)
    
    # Retorna la instancia de BasePage para que los tests puedan utilizarla.
    return base_page