import re
import time
import random
import pytest
import os
import json
from playwright.sync_api import Page, expect, Playwright, sync_playwright
from src.pages.base_page import BasePage # Se cambia 'pages.base_page' a 'base_page' y se elimina Funciones_Globales
from src.utils import config
from src.locator.locator_obstaculoPantalla import ObstaculosLocators # Se asume esta importación es necesaria
from src.utils.generador_datos import GeneradorDeDatos

# Crea una instancia del generador de datos
generador_datos = GeneradorDeDatos()

def test_login_con_campos_vacios(set_up_Home: BasePage) -> None:
    """
    Test para verificar la validación de campos vacíos en el formulario de login.

    Este test ejecuta dos escenarios clave para asegurar que la validación nativa de
    HTML5 funciona correctamente:
    
    1. Intenta iniciar sesión con ambos campos (usuario y contraseña) vacíos y
        valida que el mensaje de "Completa este campo" aparezca para el campo de usuario.
    
    2. Rellena el campo de usuario y deja el de contraseña vacío. Luego,
        intenta iniciar sesión de nuevo y valida que el mensaje de "Completa este campo"
        aparezca para el campo de contraseña.

    Args:
        set_up_Home (BasePage): Un fixture que inicializa la página de inicio
                                 y proporciona la instancia de `BasePage` para
                                 interactuar con los elementos del DOM.
    """
    
    # El fixture `set_up_Home` ya ha navegado a la página de registro.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    # --- Escenario 1: Login con ambos campos vacíos ---
    
    # Valida que los campos de usuario y contraseña estén vacíos al inicio del test.
    base_page.element.validar_elemento_vacio(base_page.home.campoUsername, "Validar_campo_userName_vacio", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.home.campoPassword, "Validar_campo_Password_vacio", config.SCREENSHOT_DIR)
    
    # Hace clic en el botón de login para activar la validación nativa de HTML5.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin", config.SCREENSHOT_DIR)
    
    # Verifica que el mensaje de validación de HTML5 para el campo de usuario sea el esperado.
    # Ahora pasamos una lista con los textos en español e inglés.
    base_page.element.validar_mensaje_validacion_html5(base_page.home.campoUsername, ["Completa este campo", "Fill out this field", "Please fill out this field."], "Verificar_validacion_HTML5_userName", config.SCREENSHOT_DIR)
    
    # --- Escenario 2: Login con campo de contraseña vacío ---
    
    # Genera datos de usuario aleatorios y únicos para rellenar el campo de usuario.
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    
    # Rellena el campo de usuario con el dato generado.
    base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, datos_usuario["username"], "rellenar_campoUserName", config.SCREENSHOT_DIR)
    
    # Valida que el campo de contraseña siga vacío antes del segundo clic.
    base_page.element.validar_elemento_vacio(base_page.home.campoPassword, "Validar_campo_Password_vacio_segunda_vez", config.SCREENSHOT_DIR)
    
    # Hace clic en el botón de login nuevamente para activar la validación en el campo de contraseña.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin_segunda_vez", config.SCREENSHOT_DIR)
    
    # Verifica que el mensaje de validación de HTML5 aparezca en el campo de contraseña.
    # Se pasa la lista de textos para la validación multilingüe.
    base_page.element.validar_mensaje_validacion_html5(base_page.home.campoPassword, ["Completa este campo", "Fill out this field", "Please fill out this field."], "Verificar_validacion_HTML5_password", config.SCREENSHOT_DIR)
    
    # --- Escenario 3: Login con campo userName vacío ---
    
    # Genera datos de usuario aleatorios y únicos para rellenar el campo de usuario.
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    
    # vaciar el campo usernamer
    base_page.element.limpiar_campo(base_page.home.campoUsername, "vaciar_campoUserName", config.SCREENSHOT_DIR)
    
    # Rellena el campo de password con el dato generado.
    base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, datos_usuario["password"], "rellenar_password", config.SCREENSHOT_DIR)
    
    # Hace clic en el botón de login nuevamente para activar la validación en el campo de contraseña.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin_segunda_vez", config.SCREENSHOT_DIR)
    
    # Verifica que el mensaje de validación de HTML5 aparezca en el campo de contraseña.
    # Se pasa la lista de textos para la validación multilingüe.
    base_page.element.validar_mensaje_validacion_html5(base_page.home.campoUsername, ["Completa este campo", "Fill out this field", "Please fill out this field."], "Verificar_validacion_HTML5_password", config.SCREENSHOT_DIR)

def test_con_formato_userName_invalido(set_up_Home: BasePage) -> None:
    """
    Test que verifica el inicio de sesión con un nombre de usuario de formato inválido.

    Pasos:
    1. Genera un nombre de usuario con formato inválido y una contraseña válida.
    2. Rellena los campos de usuario y contraseña en la página de inicio.
    3. Intenta iniciar sesión.
    4. Valida que aparezca un mensaje de error que indique credenciales inválidas.
    """
    
    # El fixture `set_up_Home` ya ha navegado a la página de registro.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    # Genera datos de usuario aleatorios y únicos para rellenar el campo de usuario.
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    # Utiliza un nombre de usuario con formato inválido para el test.
    username_invalido = generador_datos.generar_username_invalido()
    
    # Rellena el campo de usuario y la contraseña.
    base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, username_invalido, "rellenar_campoUserName_formato_invalido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, datos_usuario["password"], "rellenar_campoPassword", config.SCREENSHOT_DIR)
    
    # Hace clic en el botón de login.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin_segunda_vez", config.SCREENSHOT_DIR)
    
    # Verifica que el mensaje de error sea el esperado.
    base_page.element.verificar_texto_exacto(base_page.login.labelDatoLoginInvalido, "Invalid username/password", "Verificar_username_invalido", config.SCREENSHOT_DIR)

    
def test_con_formato_password_invalido(set_up_Home: BasePage) -> None:
    """
    Test que verifica el inicio de sesión con una contraseña de formato inválido.

    Pasos:
    1. Genera una contraseña con formato inválido y un nombre de usuario válido.
    2. Rellena los campos de usuario y contraseña en la página de inicio.
    3. Intenta iniciar sesión.
    4. Valida que aparezca un mensaje de error que indique credenciales inválidas.
    """
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    # Genera datos de usuario y una contraseña con formato inválido para el test.
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    password_invalido = generador_datos.generar_password_invalido()
    
    # Rellena el campo de usuario y la contraseña.
    base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, datos_usuario["username"], "rellenar_campoUserName_formato_invalido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, password_invalido, "rellenar_campoPassword", config.SCREENSHOT_DIR)
    
    # Hace clic en el botón de login.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin_segunda_vez", config.SCREENSHOT_DIR)
    
    # Valida el mensaje de error esperado.
    base_page.element.verificar_texto_exacto(base_page.login.labelDatoLoginInvalido, "Invalid username/password", "Verificar_username_invalido", config.SCREENSHOT_DIR)
    
def test_con_password_corta(set_up_Home: BasePage) -> None:
    """
    Test que verifica el inicio de sesión con una contraseña demasiado corta.

    Pasos:
    1. Genera una contraseña corta y un nombre de usuario válido.
    2. Rellena los campos de usuario y contraseña en la página de inicio.
    3. Intenta iniciar sesión.
    4. Valida que aparezca un mensaje de error indicando credenciales inválidas.
    """
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    # Genera datos de usuario y una contraseña intencionalmente corta para el test.
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    password_corta = generador_datos.generar_password_muy_corta()
    
    # Rellena los campos de usuario y contraseña.
    base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, datos_usuario["username"], "rellenar_campoUserName_formato_invalido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, password_corta, "rellenar_campoPassword", config.SCREENSHOT_DIR)
    
    # Hace clic en el botón de login.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin_segunda_vez", config.SCREENSHOT_DIR)
    
    # Valida el mensaje de error esperado.
    base_page.element.verificar_texto_exacto(base_page.login.labelDatoLoginInvalido, "Invalid username/password", "Verificar_username_invalido", config.SCREENSHOT_DIR)
    
def test_login_con_usuario_no_registrado(set_up_Home: BasePage) -> None:
    """
    Test que verifica el inicio de sesión con credenciales de un usuario no registrado.

    Pasos:
    1. Genera datos para un usuario inexistente.
    2. Rellena los campos de usuario y contraseña en la página de inicio con los datos generados.
    3. Intenta iniciar sesión.
    4. Valida que aparezca un mensaje de error indicando que el usuario no está registrado.
    """
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Home
    
    # Genera credenciales para un usuario que no existe.
    dato_usuario_no_registrado = generador_datos.generar_usuario_inexistente()
    
    # Rellena los campos de usuario y contraseña.
    base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, dato_usuario_no_registrado["username"], "rellenar_campoUserName_inexistente", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, dato_usuario_no_registrado["password"], "rellenar_campoPassword_inexistente", config.SCREENSHOT_DIR)
    
    # Hace clic en el botón de login.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin_segunda_vez", config.SCREENSHOT_DIR)
    
    # Valida el mensaje de error esperado.
    base_page.element.verificar_texto_exacto(base_page.login.labelDatoLoginInvalido, "Invalid username/password", "Verificar_username_invalido", config.SCREENSHOT_DIR)

def test_login_con_espacio_antes(set_up_Home: BasePage) -> None:
    """
    Verifica que el inicio de sesión falle cuando el nombre de usuario o la contraseña
    tienen un espacio en blanco al inicio.

    Este test simula dos intentos de inicio de sesión con credenciales válidas,
    pero con espacios en blanco al inicio para asegurar que la aplicación maneja
    correctamente este tipo de errores de entrada y muestra el mensaje de error esperado.

    Args:
        set_up_Home (BasePage): Un fixture que inicializa la página de inicio.
    """
    base_page = set_up_Home
    
    # La ruta del archivo se obtiene desde la variable de configuración.
    registros_path = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    try:
        # Lee el archivo JSON de usuarios registrados.
        usuarios_registrados = base_page.file.leer_json(registros_path, "Cargar usuarios registrados")
        
        # Verifica que la lista de usuarios no esté vacía. Si está vacía, se salta el test.
        if not usuarios_registrados:
            pytest.skip("No hay usuarios registrados en el archivo para realizar el test de login.")
            
        # Selecciona un usuario aleatorio para la prueba.
        usuario_a_probar = random.choice(usuarios_registrados)
        
        # --- Escenario 1: Espacio en el nombre de usuario ---
        
        # Rellena el campo de usuario con un espacio al inicio.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, f" {usuario_a_probar["username"]}", "rellenar_campoUserName_exitoso", config.SCREENSHOT_DIR)
        # Rellena el campo de contraseña con el valor correcto.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, usuario_a_probar["password"], "rellenar_campoPassword_exitoso", config.SCREENSHOT_DIR)
        
        # Hace clic en el botón de login.
        base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botónLogin_espacio_antes", config.SCREENSHOT_DIR)
        
        # Valida que el mensaje de datos de login inválidos sea visible.
        base_page.element.validar_elemento_visible(base_page.login.labelDatoLoginInvalido, "Visualizar_mensaje_data_invalida", config.SCREENSHOT_DIR)
        
        # --- Escenario 2: Espacio en la contraseña ---
        
        # Rellena el campo de usuario con el valor correcto.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, usuario_a_probar["username"], "rellenar_campoUserName_exitoso", config.SCREENSHOT_DIR)
        # Rellena el campo de contraseña con un espacio al inicio.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, f" {usuario_a_probar["password"]}", "rellenar_campoPassword_exitoso", config.SCREENSHOT_DIR)
        
        # Hace clic en el botón de login.
        base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botónLogin_espacio_antes", config.SCREENSHOT_DIR)
        
        # Valida que el mensaje de datos de login inválidos sea visible.
        base_page.element.validar_elemento_visible(base_page.login.labelDatoLoginInvalido, "Visualizar_mensaje_data_invalida", config.SCREENSHOT_DIR)
        
    except FileNotFoundError:
        # Si el archivo JSON no existe, se salta el test.
        pytest.skip(f"El archivo de registros de usuarios '{registros_path}' no se encontró.")
    except Exception as e:
        # En caso de cualquier otro error inesperado, el test falla.
        pytest.fail(f"Ocurrió un error inesperado durante el test: {e}")
        
def test_login_con_espacio_despues(set_up_Home: BasePage) -> None:
    """
    Verifica que el inicio de sesión falle cuando el nombre de usuario o la contraseña
    tienen un espacio en blanco al final.

    Similar al test anterior, este caso asegura que la lógica de validación maneja
    correctamente los espacios en blanco al final de las credenciales, lo que
    podría causar un error de autenticación.

    Args:
        set_up_Home (BasePage): Un fixture que inicializa la página de inicio.
    """
    base_page = set_up_Home
    
    # La ruta del archivo se obtiene desde la variable de configuración.
    registros_path = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.csv")
    
    try:
        # Se usa la nueva función para obtener todos los datos del CSV como un diccionario.
        usuarios_registrados = base_page.file.leer_csv_diccionario(registros_path, "Cargar usuarios registrados desde CSV")
        
        # Verifica que la lista de usuarios no esté vacía. Si está vacía, se salta el test.
        if not usuarios_registrados:
            pytest.skip("No hay usuarios registrados en el archivo CSV para realizar el test de login.")
            
        # Selecciona un usuario aleatorio para la prueba.
        usuario_a_probar = random.choice(usuarios_registrados)
        
        # Desglosa los datos del usuario seleccionado para usarlos por separado.
        username = usuario_a_probar["username"]
        password = usuario_a_probar["password"]
        
        # --- Escenario 1: Espacio en el nombre de usuario ---
        
        # Rellena el campo de usuario con un espacio al final.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, f"{username} ", "rellenar_campoUserName_exitoso", config.SCREENSHOT_DIR)
        # Rellena el campo de contraseña con el valor correcto.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, password, "rellenar_campoPassword_exitoso", config.SCREENSHOT_DIR)
        
        # Hace clic en el botón de login.
        base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botónLogin_espacio_después", config.SCREENSHOT_DIR)
        
        # Valida que el mensaje de datos de login inválidos sea visible.
        base_page.element.validar_elemento_visible(base_page.login.labelDatoLoginInvalido, "Visualizar_mensaje_data_invalida", config.SCREENSHOT_DIR)
        
        # --- Escenario 2: Espacio en la contraseña ---
        
        # Rellena el campo de usuario con el valor correcto.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, username, "rellenar_campoUserName_exitoso", config.SCREENSHOT_DIR)
        # Rellena el campo de contraseña con un espacio al final.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, f"{password} ", "rellenar_campoPassword_exitoso", config.SCREENSHOT_DIR)
        
        # Hace clic en el botón de login.
        base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botónLogin_espacio_después", config.SCREENSHOT_DIR)
        
        # Valida que el mensaje de datos de login inválidos sea visible.
        base_page.element.validar_elemento_visible(base_page.login.labelDatoLoginInvalido, "Visualizar_mensaje_data_invalida", config.SCREENSHOT_DIR)
        
    except FileNotFoundError:
        # Si el archivo CSV no existe, se salta el test.
        pytest.skip(f"El archivo de registros de usuarios '{registros_path}' no se encontró.")
    except Exception as e:
        # En caso de cualquier otro error inesperado, el test falla.
        pytest.fail(f"Ocurrió un error inesperado durante el test: {e}")

def test_login_exitoso_data_json(set_up_Home: BasePage) -> None:
    """
    Test que verifica el inicio de sesión exitoso con credenciales válidas.

    Pasos:
    1. Lee los datos de usuarios registrados desde un archivo JSON.
    2. Selecciona un usuario aleatorio de la lista.
    3. Rellena los campos de usuario y contraseña con las credenciales del usuario seleccionado.
    4. Intenta iniciar sesión.
    5. Valida que el login fue exitoso verificando la URL de la página de destino.
    """
    base_page = set_up_Home
    
    # La ruta del archivo se obtiene desde la variable de configuración.
    registros_path = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")
    
    # Se usa la clase FileActions para leer el archivo JSON
    # Se debe importar la clase FileActions y crear una instancia.
    try:
        usuarios_registrados = base_page.file.leer_json(registros_path, "Cargar usuarios registrados")
        
        # Verifica que la lista no esté vacía
        if not usuarios_registrados:
            pytest.skip("No hay usuarios registrados en el archivo para realizar el test de login exitoso.")
            
        # Selecciona un usuario aleatorio
        usuario_a_probar = random.choice(usuarios_registrados)
        
        # Rellena el campo de usuario y la contraseña.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, usuario_a_probar["username"], "rellenar_campoUserName_exitoso", config.SCREENSHOT_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, usuario_a_probar["password"], "rellenar_campoPassword_exitoso", config.SCREENSHOT_DIR)
        
        # Hace clic en el botón de login.
        base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin_exitoso", config.SCREENSHOT_DIR, "Login")
        
        # Valida el saludo personalizado
        base_page.element.verificar_texto_contenido(base_page.dashboard.labelSaludo, f"Hi, {usuario_a_probar["first_name"]}", "Verificar_saludo_personalizado", config.SCREENSHOT_DIR)
        
        # Valida que los botones del dashboard estén visibles
        base_page.element.validar_elemento_visible(base_page.dashboard.botonProfile, "verificar_visibilidad_botón_profile", config.SCREENSHOT_DIR)
        base_page.element.validar_elemento_visible(base_page.dashboard.botonLogout, "verificar_visibilidad_botón_logout", config.SCREENSHOT_DIR)
        
    except FileNotFoundError:
        pytest.skip(f"El archivo de registros de usuarios '{registros_path}' no se encontró.")
    except Exception as e:
        pytest.fail(f"Ocurrió un error inesperado durante el test: {e}")
        
def test_login_exitoso_data_csv(set_up_Home: BasePage) -> None:
    """
    Test que verifica el inicio de sesión exitoso con credenciales válidas
    obtenidas de un archivo CSV.

    Pasos:
    1. Lee los datos de usuarios registrados desde un archivo CSV.
    2. Selecciona un usuario aleatorio de la lista.
    3. Rellena los campos de usuario y contraseña con las credenciales del usuario seleccionado.
    4. Intenta iniciar sesión.
    5. Valida que el login fue exitoso verificando el nombre del usuario logeado.
    """
    base_page = set_up_Home
    
    # La ruta del archivo se obtiene desde la variable de configuración.
    registros_path = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.csv")
    
    try:
        # Se usa la nueva función leer_csv_diccionario para obtener todos los datos
        # de cada fila como un diccionario.
        usuarios_registrados = base_page.file.leer_csv_diccionario(registros_path, "Cargar usuarios registrados desde CSV")
        
        # Verifica que la lista no esté vacía
        if not usuarios_registrados:
            pytest.skip("No hay usuarios registrados en el archivo CSV para realizar el test de login exitoso.")
            
        # Selecciona un usuario aleatorio
        usuario_a_probar = random.choice(usuarios_registrados)
        
        # Desglosa los datos del usuario seleccionado para usarlos por separado.
        username = usuario_a_probar["username"]
        password = usuario_a_probar["password"]
        first_name = usuario_a_probar["first_name"]
        
        # Rellena el campo de usuario y la contraseña.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, username, "rellenar_campoUserName_exitoso_csv", config.SCREENSHOT_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, password, "rellenar_campoPassword_exitoso_csv", config.SCREENSHOT_DIR)
        
        # Hace clic en el botón de login.
        base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin_exitoso", config.SCREENSHOT_DIR, "Login", 4)
        
        # Valida que el mensaje de datos de login inválidos no sea visible.
        base_page.element.validar_elemento_no_visible(base_page.login.labelDatoLoginInvalido, "No_visualizar_mensaje_data_invalida", config.SCREENSHOT_DIR)
        
        # Valida el saludo personalizado
        base_page.element.verificar_texto_contenido(base_page.dashboard.labelSaludo, f"Hi, {first_name}", "Verificar_saludo_personalizado_csv", config.SCREENSHOT_DIR)
        
        # Valida que los botones del dashboard estén visibles
        base_page.element.validar_elemento_visible(base_page.dashboard.botonProfile, "verificar_visibilidad_botón_profile_csv", config.SCREENSHOT_DIR)
        base_page.element.validar_elemento_visible(base_page.dashboard.botonLogout, "verificar_visibilidad_botón_logout_csv", config.SCREENSHOT_DIR)
        
    except FileNotFoundError:
        pytest.skip(f"El archivo de registros de usuarios '{registros_path}' no se encontró.")
    except Exception as e:
        pytest.fail(f"Ocurrió un error inesperado durante el test: {e}")
        
def test_login_exitoso_data_excel(set_up_Home: BasePage) -> None:
    """
    Test que verifica el inicio de sesión exitoso con credenciales válidas
    obtenidas de un archivo Excel.

    Pasos:
    1. Lee los datos de usuarios registrados desde un archivo Excel.
    2. Selecciona un usuario aleatorio de la lista.
    3. Rellena los campos de usuario y contraseña con las credenciales del usuario seleccionado.
    4. Intenta iniciar sesión.
    5. Valida que el login fue exitoso verificando el nombre del usuario logeado.
    """
    base_page = set_up_Home

    # La ruta del archivo ahora apunta directamente al archivo Excel.
    registros_path = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.xlsx")
    hoja_excel = "Sheet1"

    try:
        # Se define la lista de encabezados manualmente
        headers = ["username", "first_name", "last_name", "password", "confirm_password"]
        
        # Usa la nueva función leer_excel_diccionario para obtener los datos.
        # Se indica la hoja de cálculo y se proporcionan los headers.
        usuarios_registrados = base_page.file.leer_excel_diccionario(
            registros_path,
            sheet_name=hoja_excel,
            has_header=False,
            headers=headers,
            nombre_paso="Cargar usuarios registrados desde Excel"
        )
        
        # Verifica que la lista no esté vacía
        if not usuarios_registrados:
            pytest.skip("No hay usuarios registrados en el archivo de datos para realizar el test de login exitoso.")
            
        # Selecciona un usuario aleatorio
        usuario_a_probar = random.choice(usuarios_registrados)
        
        # Rellena el campo de usuario y la contraseña.
        base_page.element.rellenar_campo_de_texto(base_page.home.campoUsername, usuario_a_probar["username"], "rellenar_campoUserName_exitoso_excel", config.SCREENSHOT_DIR)
        base_page.element.rellenar_campo_de_texto(base_page.home.campoPassword, usuario_a_probar["password"], "rellenar_campoPassword_exitoso_excel", config.SCREENSHOT_DIR)
        
        # Hace clic en el botón de login.
        base_page.element.hacer_clic_en_elemento(base_page.home.botonLogin, "Clic_botonLogin_exitoso", config.SCREENSHOT_DIR, "Login", 4)
        
        # Valida que el mensaje de datos de login inválidos no sea visible.
        base_page.element.validar_elemento_no_visible(base_page.login.labelDatoLoginInvalido, "No_visualizar_mensaje_data_invalida", config.SCREENSHOT_DIR)
        
        # Valida el saludo personalizado
        base_page.element.verificar_texto_contenido(base_page.dashboard.labelSaludo, f"Hi, {usuario_a_probar["first_name"]}", "Verificar_saludo_personalizado_excel", config.SCREENSHOT_DIR)
        
        # Valida que los botones del dashboard estén visibles
        base_page.element.validar_elemento_visible(base_page.dashboard.botonProfile, "verificar_visibilidad_botón_profile_excel", config.SCREENSHOT_DIR)
        base_page.element.validar_elemento_visible(base_page.dashboard.botonLogout, "verificar_visibilidad_botón_logout_excel", config.SCREENSHOT_DIR)
        
    except FileNotFoundError:
        pytest.skip(f"El archivo de registros de usuarios '{registros_path}' no se encontró.")
    except Exception as e:
        pytest.fail(f"Ocurrió un error inesperado durante el test: {e}")