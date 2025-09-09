from playwright.sync_api import Page

class HomeLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector de nombre home
    @property
    def nombreHome(self):
        return self.page.get_by_role("link", name="Buggy Rating")
    
    #Selector de campo username
    @property
    def campoUsername(self):
        return self.page.get_by_role("textbox", name="Login")
    
    #Selector de campo password
    @property
    def campoPassword(self):
        return self.page.locator("input[name='password']")
    
    #Selector de boton login
    @property
    def botonLogin(self):
        return self.page.get_by_role("button", name="Login")

    #Selector de boton resgistrarse
    @property
    def botonRegistrarse(self):
        return self.page.get_by_role("link", name="Register")
    
    #Selector de nombre banner central
    @property
    def nombreBannerCentral(self):
        return self.page.get_by_role("heading", name="Buggy Cars Rating")

    #Selector de imagen banner central
    @property
    def imagenBannerCentral(self):
        return self.page.get_by_role("banner").get_by_role("img")
    
    #Selector de contenedores de div popular make
    @property
    def contenedoresDeOpcionesPopularMake(self):
        return self.page.locator("div").filter(has_text="Popular Make Lamborghini(").nth(2)
    
    #Selector de nombre div popular make
    @property
    def nombreDivPopularMake(self):
        return self.page.get_by_role("heading", name="Popular Make")
    #Selector de imagen div popular make
    @property
    def imagenDivPopularMake(self):
        return self.page.locator("div").filter(has_text="Popular Make Lamborghini(").nth(2).get_by_role("img")
    
    #Selector de contenedores de div popular model
    @property
    def contenedoresDeOpcionesModel(self):
        return self.page.locator("div").filter(has_text="Popular Model Lamborghini").nth(2)
    
    #Selector de nombre div popular model
    @property
    def nombreDivPopularModel(self):
        return self.page.get_by_role("heading", name="Popular Model")
    
    #Selector de imagen div popular model
    @property
    def imagenDivPopularModel(self):
        return self.page.locator("div").filter(has_text="Popular Model Lamborghini").nth(2).get_by_role("img")
    
    #Selector de contenedores de div overall rating
    @property
    def contenedoresDeOpcionesOverallRating(self):
        return self.page.locator("div").filter(has_text="Overall Rating List of all").nth(2)
    
    #Selector de nombre div overall rating
    @property
    def nombreDivOverallRating(self):
        return self.page.get_by_role("heading", name="Overall Rating")
    
    #Selector de imagen div overall rating
    @property
    def imagenDivOverallRating(self):
        return self.page.locator("div").filter(has_text="Overall Rating List of all").nth(2).get_by_role("img")