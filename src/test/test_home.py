import re
import time
import random
import pytest
from playwright.sync_api import Page, expect, Playwright, sync_playwright
from src.pages.base_page import BasePage # Se cambia 'pages.base_page' a 'base_page' y se elimina Funciones_Globales
from src.utils import config
from src.locator.locator_obstaculoPantalla import ObstaculosLocators # Se asume esta importación es necesaria


def test_ingresar_a_home(base_page: BasePage) -> None:
    """
    Test que verifica la navegación a la página de inicio y maneja obstáculos si es necesario.
    
    Ahora usa el fixture 'base_page' directamente para acceder a todas las acciones.
    """
    # NO es necesario inicializar base_page = Funciones_Globales(page).
    # La inyección del fixture hace el trabajo por ti.

    # Navega a la URL base
    base_page.navigation.ir_a_url(config.BASE_URL, "inicio_test", config.SCREENSHOT_DIR)
    
    # Valida que la URL actual sea la de la página de inicio
    # Nota: la función validar_url_actual en tu código de ejemplo
    # usa un regex, por lo que es mejor usar r".*" para que coincida.
    base_page.navigation.validar_url_actual(config.BASE_URL)
    
    # Maneja cualquier obstáculo en la página
    # Se corrige el nombre del objeto de 'element' a 'elementos'
    base_page.element.manejar_obstaculos_en_pagina(ObstaculosLocators.LISTA_DE_OBSTACULOS)
    
    base_page.navigation.validar_titulo_de_web("Buggy Cars Rating", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
def test_validar_elementos_en_home(set_up_Home: BasePage) -> None:
    """
    Test que utiliza el fixture 'set_up_Home' para navegar y configurar la página.
    Se enfoca únicamente en la validación de los elementos de la página de inicio.
    """
    # El fixture 'set_up_Home' ya ha navegado y manejado los obstáculos.
    # Ahora, el objeto 'set_up_Home' es una instancia de BasePage lista para usar.
    base_page = set_up_Home
     # ¡Correcto! Ahora se accede al localizador a través de la instancia de la página
    # que ya contiene la instancia de HomeLocatorsPage.
    base_page.element.validar_elemento_visible(base_page.home.nombreHome, "validar_nombreHome_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.campoUsername, "validar_campoUsername_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.home.campoUsername, "verificar_campoUsername_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.campoPassword, "validar_campoPassword_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.home.campoPassword, "verificar_campoPassword_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.botonLogin, "validar_botonLogin_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.botonRegistrarse, "validar_botonRegistrarse_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.nombreBannerCentral, "validar_nombreBannerCentral_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.imagenBannerCentral, "validar_imagenBannerCentral_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesPopularMake, "validar_contenedoresDeOpcionesPopularMake_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.nombreDivPopularMake, "validar_nombreDivPopularMake_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.imagenDivPopularMake, "validar_imagenDivPopularMake_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesModel, "validar_contenedoresDeOpcionesModel_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.nombreDivPopularModel, "validar_nombreDivPopularModel_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.imagenDivPopularModel, "validar_imagenDivPopularModel_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesOverallRating, "validar_contenedoresDeOpcionesOverallRating_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.nombreDivOverallRating, "validar_nombreDivOverallRating_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.imagenDivOverallRating, "validar_imagenDivOverallRating_visible", config.SCREENSHOT_DIR)
    
def test_redireccionamiento_contenedor_popular_make(set_up_Home: BasePage) -> None:
    """
    Test que verifica el redireccionamiento al hacer clic en el contenedor de "Popular Make".
    Utiliza el fixture 'set_up_Home' para la configuración inicial.
    """
    base_page = set_up_Home
    
    # Haz clic en el contenedor de "Popular Make"
    base_page.element.hacer_clic_en_elemento(base_page.home.imagenDivPopularMake, "clic_contenedor_Popular_Make", config.SCREENSHOT_DIR)
    
    # Valida que la URL actual sea la esperada después del clic
    base_page.navigation.validar_url_actual(config.MAKE_URL)
    
def test_redireccionamiento_contenedor_popular_model(set_up_Home: BasePage) -> None:
    """
    Test que verifica el redireccionamiento al hacer clic en el contenedor de "Popular Model".
    Utiliza el fixture 'set_up_Home' para la configuración inicial.
    """
    base_page = set_up_Home
    
    # Haz clic en el contenedor de "Popular Model"
    base_page.element.hacer_clic_en_elemento(base_page.home.imagenDivPopularModel, "clic_contenedor_Popular_Model", config.SCREENSHOT_DIR)
    
    # Valida que la URL actual sea la esperada después del clic
    base_page.navigation.validar_url_actual(config.POPULAR_URL)
    
def test_redireccionamiento_contenedor_overall_rating(set_up_Home: BasePage) -> None:
    """
    Test que verifica el redireccionamiento al hacer clic en el contenedor de "Overall Rating".
    Utiliza el fixture 'set_up_Home' para la configuración inicial.
    """
    base_page = set_up_Home
    
    # Haz clic en el contenedor de "Overall Rating"
    base_page.element.hacer_clic_en_elemento(base_page.home.imagenDivOverallRating, "clic_contenedor_Overall_Rating", config.SCREENSHOT_DIR)
    
    # Valida que la URL actual sea la esperada después del clic
    base_page.navigation.validar_url_actual(config.OVERALL_URL)