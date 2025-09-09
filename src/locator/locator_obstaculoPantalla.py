from playwright.sync_api import Page

class ObstaculosLocators:
    
    POPUP_SUSCRIPCION = {
        "nombre": "Popup de Suscripción", 
        "locator": "#newsletter-popup a.close-btn"
    }
    BANNER_COOKIES = {
        "nombre": "Banner de Cookies", 
        "locator": "text='Aceptar cookies'"
    }
    ANUNCIO_FLOTANTE = {
        "nombre": "Anuncio Flotante", 
        "locator": ".ad-container button.close"
    }
    # Puedes crear una lista con todos ellos
    LISTA_DE_OBSTACULOS = [
        POPUP_SUSCRIPCION,
        BANNER_COOKIES,
        ANUNCIO_FLOTANTE
    ]