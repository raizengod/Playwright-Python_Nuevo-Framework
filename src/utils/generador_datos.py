from faker import Faker
import re

# Crea una instancia de Faker, puedes especificar una región para datos localizados
# Por ejemplo: 'es_ES' para España, 'en_US' para Estados Unidos
fake = Faker('es_ES')

class GeneradorDeDatos:
    """
    Clase para generar datos de prueba realistas y aleatorios.
    """
    def generar_usuario_aleatorio(self):
        """Genera un conjunto completo de datos de usuario para el registro."""
        # Genera el nombre de usuario de Faker, que puede contener caracteres especiales.
        username_raw = fake.user_name()
        # Filtra el nombre de usuario para que solo contenga caracteres alfanuméricos (letras y números).
        username_clean = re.sub(r'[^a-zA-Z0-9]', '', username_raw)
        # Combina el nombre de usuario limpio con un número aleatorio para asegurar unicidad.
        username = f"{username_clean}{fake.unique.random_int(min=100, max=999)}"
        
        # Genera un email aleatorio y real
        #email = fake.unique.email()
        first_name = fake.first_name()
        last_name = fake.last_name()
        # Genera la contraseña una sola vez
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)

        return {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            #"email": email,
            "password": password,
            # Añade el campo de confirmación de contraseña, usando la misma variable
            "confirm_password": password 
        }

    def generar_nombre_invalido(self):
        """Genera un nombre que contiene caracteres no permitidos."""
        return fake.name() + "123"

    # Si solo necesitas una función simple, también puedes hacerlo así:
    def generar_email_valido():
        return fake.unique.email()

    def generar_password_invalido(self):
        """
        Genera una contraseña que no cumple con las reglas de seguridad
        (por ejemplo, sin mayúsculas, sin caracteres especiales).
        """
        # La contraseña generada no tendrá mayúsculas, ni caracteres especiales.
        return fake.password(length=8, special_chars=False, digits=True, upper_case=False)
            
    def generar_password_muy_corta(self):
        """
        Genera una contraseña intencionalmente muy corta para tests negativos.
        Se ajusta para que la longitud sea menor que los requerimientos de caracteres.
        """
        return fake.password(length=3, special_chars=False, digits=False, upper_case=False, lower_case=True)

    def generar_username_invalido(self):
        """
        Genera un nombre de usuario que contiene espacios, lo cual generalmente
        es un formato inválido.
        """
        # Un nombre de usuario con espacios
        return fake.name()

    def generar_usuario_inexistente(self):
        """Genera un usuario que no existe."""
        username_raw = fake.user_name()
        username_clean = re.sub(r'[^a-zA-Z0-9]', '', username_raw)
        username = f"{username_clean}{fake.unique.random_int(min=100, max=999)}"
        
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
        return {"username": username, "password": password}