from playwright.sync_api import Page

class LoginLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
    
    #Selector label apellido
    @property
    def labelDatoLoginInvalido(self):
        return self.page.get_by_text("Invalid username/password")