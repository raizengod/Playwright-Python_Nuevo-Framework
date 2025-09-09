from playwright.sync_api import Page

class DasboardLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    @property    
    def labelSaludo(self):
        return self.page.get_by_text("Hi, ")
    
    @property    
    def botonProfile(self):
        return self.page.get_by_role("link", name="Profile")
    
    @property    
    def botonLogout(self):
        return self.page.get_by_role("link", name="Logout")