from playwright.sync_api import Page

class RegistroLocatorsPage:
    
    def __init__(self, page: Page):
        self.page = page
        
    #Selector de titulo formulario
    @property
    def tituloFormulario(self):
        return self.page.get_by_role("heading", name="Register with Buggy Cars")
        
    #Selector label userName
    @property
    def labelUserName(self):
        return self.page.locator("label").filter(has_text="Login")
    
    #Selector de campo userName
    @property
    def campoUserName(self):
        return self.page.get_by_label("Login")
    
    #Selector label nombre
    @property
    def labelNombre(self):
        return self.page.get_by_text("First Name", exact=True)
    
    #Selector de campo nombre
    @property
    def campoNombre(self):
        return self.page.get_by_role("textbox", name="First Name")
    
    #Selector label apellido
    @property
    def labelApellido(self):
        return self.page.get_by_text("Last Name")
    
    #Selector de campo apellido
    @property
    def campoApellido(self):
        return self.page.get_by_role("textbox", name="Last Name")
    
    #Selector label password
    @property
    def labelPassword(self):
        return self.page.get_by_text("Password", exact=True)
    
    #Selector de campo password
    @property
    def campoPassword(self):
        return self.page.get_by_role("textbox", name="Password", exact=True)
    
    #Selector label confirmar password
    @property
    def labelConfirmPassword(self):
        return self.page.get_by_text("Confirm Password")
    
    #Selector de campo confirmar password
    @property
    def campoConfirmPassword(self):
        return self.page.get_by_role("textbox", name="Confirm Password")
    
    #Selector de botón registrar
    @property
    def botonRegistrar(self):
        return self.page.get_by_role("button", name="Register")
    
    #Selector de botón cancelar
    @property
    def botonCancelar(self):
        return self.page.get_by_role("button", name="Cancel")
    
    #Selector de mensaje campo userName vacío
    @property
    def mensajeUserNameVacio(self):
        return self.page.get_by_text("Login is required")
    
    #Selector de mensaje campo nombre vacío
    @property
    def mensajeNombreVacio(self):
        return self.page.locator("my-register form div").filter(has_text="First Name First Name is").locator("div")
    
    #Selector de mensaje campo apellido vacío
    @property
    def mensajeApellidoVacio(self):
        return self.page.locator("my-register form div").filter(has_text="Last Name First Name is").locator("div")
    
    #Selector de mensaje campo password vacío
    @property
    def mensajePasswordVacio(self):
        return self.page.get_by_text("Password is required")
    
    #Selector de mensaje campo confirmar password vacío
    @property
    def mensajeConfirmPasswordVacio(self):
        return self.page.get_by_text("Passwords do not match")
    
    #Selector de mensaje caracteres mínimos
    @property
    def mensajeCaracteresMinimos(self):
        return self.page.get_by_text("InvalidParameter")

    #Selector de mensaje usuario ya existente
    @property
    def mensajeUsuarioExistente(self):
        return self.page.get_by_text("UsernameExistsException: User")
    
    #Selector de mensaje regla de password no cumplida
    @property
    def mensajePoliticaPassword(self):
        return self.page.get_by_text("InvalidPasswordException:")
    
    #Selector de mensaje confirmación registro exitoso
    @property
    def mensajeRegistroExitoso(self):
        return self.page.get_by_text("Registration is successful")