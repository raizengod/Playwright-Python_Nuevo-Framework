from playwright.sync_api import Page
import re

class LoginLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
    
    #Selector label apellido
    @property
    def labelDatoLoginInvalido(self):
        # Usamos una expresión regular para que la búsqueda sea insensible a mayúsculas y minúsculas.
        # Esto asegura que el localizador encuentre el elemento sin importar la capitalización.
        return self.page.get_by_text(re.compile("Invalid", re.IGNORECASE))