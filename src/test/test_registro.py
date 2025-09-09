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

def test_ingresar_a_registrarse(base_page: BasePage) -> None:
    """
    Test que verifica el flujo de navegación a la página de registro.
    
    Este test realiza los siguientes pasos:
    1. Navega a la URL base de la aplicación.
    2. Hace clic en el botón 'Register' para iniciar el proceso de registro.
    3. Valida la URL y el título de la página para confirmar que la navegación fue exitosa.
    4. Maneja cualquier obstáculo (popups, banners) que pueda aparecer en la página.
    """
    # 1. Navega a la URL base y toma una captura inicial.
    base_page.navigation.ir_a_url(config.BASE_URL, "Inicio_test_registro", config.SCREENSHOT_DIR)
    
    # 2. Hace clic en el botón 'Register' y toma una captura.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonRegistrarse, "Clic_botonRegistrarse", config.SCREENSHOT_DIR)
    
    # 3. Valida que la URL actual sea la de la página de registro.
    base_page.navigation.validar_url_actual(config.REGISTRAR_URL)
    
    # 4. Maneja cualquier obstáculo que pueda aparecer en la página de registro.
    base_page.element.manejar_obstaculos_en_pagina(ObstaculosLocators.LISTA_DE_OBSTACULOS)
    
    # 5. Valida que el título de la página sea el correcto.
    base_page.navigation.validar_titulo_de_web("Buggy Cars Rating", "validar_titulo_de_web_registro", config.SCREENSHOT_DIR)
    
def test_validar_elementos_en_registro(set_up_Registrar: BasePage) -> None:
    """
    Test que valida la visibilidad, el texto y el estado inicial de los elementos
    en el formulario de la página de registro.
    
    El fixture `set_up_Registrar` se encarga de la navegación previa y el manejo de obstáculos,
    permitiendo que este test se centre solo en las aserciones de la página.
    """
    # El fixture `set_up_Registrar` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # Validaciones del formulario de registro
    
    # 1. Título y etiquetas de los campos
    base_page.element.verificar_texto_contenido(base_page.registro.tituloFormulario, "Register with Buggy Cars Rating", "validar_texto_TrituloFormularioRegistrar", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.labelUserName, "Login", "validar_texto_labelUserName", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.labelNombre, "First Name", "validar_texto_labelNombre", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.labelApellido, "Last Name", "validar_texto_labelApellido", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.labelPassword, "Password", "validar_texto_labelPassword", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.labelConfirmPassword, "Confirm Password", "validar_texto_labelConfirmPassword", config.SCREENSHOT_DIR)

    # 2. Visibilidad y estado inicial de los campos de entrada
    # Se valida que los campos estén visibles y vacíos al inicio.
    base_page.element.validar_elemento_visible(base_page.registro.campoUserName, "validar_campoUserName_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoUserName, "verificar_campoUserName_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajeUserNameVacio, "validar_mensajeUserNameVacio_no_visible", config.SCREENSHOT_DIR)
    
    base_page.element.validar_elemento_visible(base_page.registro.campoNombre, "validar_campoNombre_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoNombre, "verificar_campoNombre_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajeNombreVacio, "validar_mensajeNombreVacio_no_visible", config.SCREENSHOT_DIR)

    base_page.element.validar_elemento_visible(base_page.registro.campoApellido, "validar_campoApellido_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoApellido, "verificar_campoApellido_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajeApellidoVacio, "validar_mensajeApellidoVacio_no_visible", config.SCREENSHOT_DIR)

    base_page.element.validar_elemento_visible(base_page.registro.campoPassword, "validar_campoPassword_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoPassword, "verificar_campoPassword_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajePasswordVacio, "validar_mensajePasswordVacio_no_visible", config.SCREENSHOT_DIR)
    
    base_page.element.validar_elemento_visible(base_page.registro.campoConfirmPassword, "validar_campoConfirmPassword_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoConfirmPassword, "verificar_campoConfirmPassword_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajeConfirmPasswordVacio, "validar_mensajeConfirmPasswordVacio_no_visible", config.SCREENSHOT_DIR)
    
    # 3. Estado inicial de los botones
    base_page.element.validar_elemento_visible(base_page.registro.botonRegistrar, "validar_botónRegistrar_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_desactivado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_desactivado", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.registro.botonCancelar, "validar_botóCancelar_visible", config.SCREENSHOT_DIR)
    base_page.element.verificar_elemento_habilitado(base_page.registro.botonCancelar, "verificar_botonCancelar_habilitado", config.SCREENSHOT_DIR)
    
def test_validar_mensajes_campos_vacios(set_up_Registrar: BasePage) -> None:
    """
    Test que valida la aparición de los mensajes de error para los campos obligatorios.
    
    La estrategia consiste en rellenar un campo y luego limpiarlo para activar el
    mensaje de validación, y luego verificar que el mensaje correcto sea visible.
    """
    # El fixture `set_up_Registrar` ya ha realizado la navegación y el manejo de obstáculos.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    
    # 1. Validar mensaje para el campo de 'Login'
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, datos_usuario["username"], "rellenar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.limpiar_campo(base_page.registro.campoUserName, "limpiar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.mensajeUserNameVacio, "Login is required", "validar_mensajeUserNameVacio_visible", config.SCREENSHOT_DIR)
    
    # 2. Validar mensaje para el campo de 'First Name'
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, datos_usuario["first_name"], "rellenar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.limpiar_campo(base_page.registro.campoNombre, "limpiar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.mensajeNombreVacio, "First Name is required", "validar_mensajeNombreVacio_visible", config.SCREENSHOT_DIR)
    
    # 3. Validar mensaje para el campo de 'Last Name'
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, datos_usuario["last_name"], "rellenar_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.limpiar_campo(base_page.registro.campoApellido, "limpiar_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.mensajeApellidoVacio, "First Name is required", "validar_mensajeApellidoVacio_visible", config.SCREENSHOT_DIR)
    
    # 4. Validar mensaje para el campo de 'Password'
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, datos_usuario["password"], "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.limpiar_campo(base_page.registro.campoPassword, "limpiar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.mensajePasswordVacio, "Password is required", "validar_mensajePasswordVacio_visible", config.SCREENSHOT_DIR)
    
    # 5. Validar mensaje para el campo de 'Confirm Password'
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, datos_usuario["confirm_password"], "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR)
    base_page.element.limpiar_campo(base_page.registro.campoConfirmPassword, "limpiar_campoConfirmPassword", config.SCREENSHOT_DIR)
    base_page.element.verificar_texto_contenido(base_page.registro.mensajeConfirmPasswordVacio, "Passwords do not match", "validar_mensajeConfirmPasswordVacio_visible", config.SCREENSHOT_DIR)
    
    # 6. Estado inicial de los botones
    base_page.element.validar_elemento_desactivado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_desactivado", config.SCREENSHOT_DIR)
    base_page.element.verificar_elemento_habilitado(base_page.registro.botonCancelar, "verificar_botonCancelar_habilitado", config.SCREENSHOT_DIR)

def test_cancelar_registro(set_up_Registrar: BasePage) -> None:
    """
    Test que valida la funcionalidad del botón 'Cancel' en el formulario de registro
    y verifica que el usuario es redirigido a la página de inicio.
    
    Además, este test comprueba el estado inicial de los campos del formulario de registro
    después de la redirección. El fixture `set_up_Registrar` se encarga de la navegación
    inicial, permitiendo que el test se centre en el flujo de la prueba.
    """
    # El fixture `set_up_Registrar` ya ha navegado a la página de registro.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    
    # --- Parte 1: Rellenar el formulario y cancelar ---
    # Este bloque valida el flujo principal de cancelar el registro.
    
    # 1. Rellena todos los campos del formulario de registro con datos de prueba.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, datos_usuario["username"], "rellenar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, datos_usuario["first_name"], "rellenar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, datos_usuario["last_name"], "rellenar_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, datos_usuario["password"], "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, datos_usuario["confirm_password"], "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR) 
    
    # 2. Hace clic en el botón 'Cancel' para anular la acción de registro.
    base_page.element.hacer_clic_en_elemento(base_page.registro.botonCancelar, "Clic_botónCancelar", config.SCREENSHOT_DIR)
    
    # 3. Valida la redirección: verifica que la URL actual sea la de la página de inicio.
    base_page.navigation.validar_url_actual(config.BASE_URL)
    
    # --- Parte 2: Volver a la página de registro y validar su estado inicial ---
    # Este bloque verifica que el formulario se resetee correctamente al volver a él.
    
    # 4. Navega de nuevo a la página de registro.
    base_page.element.hacer_clic_en_elemento(base_page.home.botonRegistrarse, "Clic_botonRegistrarse_segunda_vez", config.SCREENSHOT_DIR)

    # 5. Valida que todos los campos del formulario estén vacíos.
    base_page.element.validar_elemento_vacio(base_page.registro.campoUserName, "verificar_campoUserName_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoNombre, "verificar_campoNombre_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoApellido, "verificar_campoApellido_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoPassword, "verificar_campoPassword_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoConfirmPassword, "verificar_campoConfirmPassword_vacío", config.SCREENSHOT_DIR)
    
    # 6. Valida el estado de los botones.
    base_page.element.validar_elemento_visible(base_page.registro.botonRegistrar, "validar_botonRegistrar_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_desactivado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_desactivado", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.registro.botonCancelar, "validar_botonCancelar_visible", config.SCREENSHOT_DIR)
    base_page.element.verificar_elemento_habilitado(base_page.registro.botonCancelar, "verificar_botonCancelar_habilitado", config.SCREENSHOT_DIR)
    
def test_habilitar_boton_registrar(set_up_Registrar: BasePage) -> None:
    """
    Test que valida el cambio de estado del botón 'Register' en el formulario.
    
    Verifica que el botón se mantiene deshabilitado a medida que se rellenan
    los campos, y que solo se habilita al completar todos los campos obligatorios
    con datos válidos. El fixture `set_up_Registrar` se encarga de la navegación
    inicial, permitiendo que el test se enfoque en esta validación de la UI.
    """
    # El fixture `set_up_Registrar` ya ha navegado a la página de registro.
    # Se asigna la instancia de BasePage a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    
    # --- Relleno de campos y validación del estado del botón en cada paso ---
    # Este enfoque de "validación incremental" es una buena práctica para asegurar
    # que la lógica de activación del botón funciona paso a paso.
    
    # 1. Rellena el campo de nombre de usuario y valida que el botón aún esté desactivado.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, datos_usuario["username"], "rellenar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_desactivado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_desactivado_1", config.SCREENSHOT_DIR)
    
    # 2. Rellena el campo de nombre y valida que el botón permanezca desactivado.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, datos_usuario["first_name"], "rellenar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_desactivado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_desactivado_2", config.SCREENSHOT_DIR)
    
    # 3. Rellena el campo de apellido y valida que el botón siga desactivado.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, datos_usuario["last_name"], "rellenar_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_desactivado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_desactivado_3", config.SCREENSHOT_DIR)
    
    # 4. Rellena el campo de contraseña y valida que el botón se mantenga desactivado.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, datos_usuario["password"], "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_desactivado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_desactivado_4", config.SCREENSHOT_DIR)
    
    # 5. Rellena el campo de confirmación de contraseña, lo que debería cumplir la última condición.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, datos_usuario["confirm_password"], "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR) 
    
    # 6. Valida que el botón 'Register' esté ahora habilitado.
    # Esta es la aserción principal del test, confirmando el cambio de estado final del elemento.
    base_page.element.verificar_elemento_habilitado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_habilitado_final", config.SCREENSHOT_DIR)
    
def test_verificar_orden_tabulacion_en_campos(set_up_Registrar: BasePage) -> None:
    """
    Validar el orden de tabulación (Tab) en los campos del formulario de registro.
    
    Este test simula la navegación del usuario a través del formulario utilizando la
    tecla 'Tab' y verifica que el foco se mueva de manera secuencial y correcta
    a cada campo y botón del formulario. También rellena los campos para simular un
    flujo de usuario completo.
    
    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    
    # 1. Navega y verifica el foco en cada elemento del formulario utilizando la tecla TAB.
    # El test valida que el foco se mueva del campo de usuario al de nombre, y así sucesivamente.
    base_page.keyboard.presionar_tab_y_verificar_foco(base_page.registro.campoUserName, "validar_foco_campoUserName", config.SCREENSHOT_DIR)
    
    # Rellena cada campo después de verificar que ha recibido el foco.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, datos_usuario["username"], "rellenar_campoUserName", config.SCREENSHOT_DIR)
    
    base_page.keyboard.presionar_tab_y_verificar_foco(base_page.registro.campoNombre, "validar_foco_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, datos_usuario["first_name"], "rellenar_campoNombre", config.SCREENSHOT_DIR)
    
    base_page.keyboard.presionar_tab_y_verificar_foco(base_page.registro.campoApellido, "validar_foco_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, datos_usuario["last_name"], "rellenar_campoApellido", config.SCREENSHOT_DIR)
    
    base_page.keyboard.presionar_tab_y_verificar_foco(base_page.registro.campoPassword, "validar_foco_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, datos_usuario["password"], "rellenar_campoPassword", config.SCREENSHOT_DIR)
    
    base_page.keyboard.presionar_tab_y_verificar_foco(base_page.registro.campoConfirmPassword, "validar_foco_campoConfirmPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, datos_usuario["confirm_password"], "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR) 
    
    # 2. Continúa la navegación con TAB para validar que el foco llegue a los botones.
    base_page.keyboard.presionar_tab_y_verificar_foco(base_page.registro.botonRegistrar, "validar_foco_botonRegistrar", config.SCREENSHOT_DIR)
    base_page.keyboard.presionar_tab_y_verificar_foco(base_page.registro.botonCancelar, "validar_foco_botonCancelar", config.SCREENSHOT_DIR)
    
def test_verificar_orden_inverso_tabulacion_en_campos(set_up_Registrar: BasePage) -> None:
    """
    Validar el orden inverso de tabulación (Shift + Tab) en los campos de registro.
    
    Este test simula la navegación inversa del usuario a través del formulario,
    partiendo desde el último elemento y verificando que el foco se mueva
    correctamente hacia atrás con la combinación de teclas 'Shift + Tab'.
    
    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    
    # 1. Establece el foco inicial en el último elemento (botón 'Cancel').
    base_page.element.hacer_focus_en_elemento(base_page.registro.botonCancelar, "hacer_focus_botonCancelar", config.SCREENSHOT_DIR)
    
    # 2. Navega hacia atrás con SHIFT + TAB y verifica el foco en cada campo.
    base_page.keyboard.presionar_shift_tab_y_verificar_foco(base_page.registro.campoConfirmPassword, "validar_foco_campoConfirmPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, datos_usuario["confirm_password"], "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR) 
    
    base_page.keyboard.presionar_shift_tab_y_verificar_foco(base_page.registro.campoPassword, "validar_foco_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, datos_usuario["password"], "rellenar_campoPassword", config.SCREENSHOT_DIR)
    
    base_page.keyboard.presionar_shift_tab_y_verificar_foco(base_page.registro.campoApellido, "validar_foco_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, datos_usuario["last_name"], "rellenar_campoApellido", config.SCREENSHOT_DIR)
    
    base_page.keyboard.presionar_shift_tab_y_verificar_foco(base_page.registro.campoNombre, "validar_foco_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, datos_usuario["first_name"], "rellenar_campoNombre", config.SCREENSHOT_DIR)
    
    base_page.keyboard.presionar_shift_tab_y_verificar_foco(base_page.registro.campoUserName, "validar_foco_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, datos_usuario["username"], "rellenar_campoUserName", config.SCREENSHOT_DIR)
    
    # 3. Valida que el botón de registro esté habilitado después de rellenar los campos.
    base_page.element.verificar_elemento_habilitado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_habilitado_final", config.SCREENSHOT_DIR)
    
def test_verificar_mensaje_politica_password(set_up_Registrar: BasePage) -> None:
    """
    Validar que se muestre el mensaje de política de contraseña al ingresar contraseñas inválidas.
    
    Este test verifica el comportamiento de la interfaz de usuario al intentar
    registrar un usuario con contraseñas que no cumplen con los requisitos de la
    política de seguridad. Se prueba la validación del sistema para:
    1. No tener caracteres en minúscula.
    2. No tener caracteres en mayúscula.
    3. No tener caracteres de símbolo.
    
    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    
    # Precondición: Rellena los campos que no se validan en este test.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, datos_usuario["username"], "rellenar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, datos_usuario["first_name"], "rellenar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, datos_usuario["last_name"], "rellenar_campoApellido", config.SCREENSHOT_DIR)
    
    # Caso 1: Contraseña sin minúsculas.
    # ----------------------------------
    # 1. Rellena los campos de contraseña con un valor que incumple la política.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, "12345678", "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, "12345678", "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR)
    
    # 2. Hace clic en el botón 'Register'.
    base_page.element.hacer_clic_en_elemento(base_page.registro.botonRegistrar, "Clic_con_contraseña_sin_minúsculas", config.SCREENSHOT_DIR)
    
    # 3. Realiza un scroll de 500px hacia abajo para asegurarse de que el mensaje de error sea visible en la pantalla.
    base_page.scroll_pagina(0, 500)
    
    # 4. Valida que se muestre el mensaje de error de política de contraseña.
    base_page.element.verificar_texto_exacto(base_page.registro.mensajePoliticaPassword, "InvalidPasswordException: Password did not conform with policy: Password must have lowercase characters", "validar_mensajePoliticaPassword_visible", config.SCREENSHOT_DIR)
    
    # Caso 2: Contraseña sin mayúsculas.
    # -----------------------------------
    # 1. Rellena los campos de contraseña con un nuevo valor que incumple la política.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, "12345678a", "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, "12345678a", "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR)
    
    # 2. Hace clic en el botón 'Register'.
    base_page.element.hacer_clic_en_elemento(base_page.registro.botonRegistrar, "Clic_con_contraseña_sin_mayúsculas", config.SCREENSHOT_DIR)
    
    # 3. Realiza un scroll de 500px hacia abajo para asegurarse de que el mensaje de error sea visible en la pantalla.
    base_page.scroll_pagina(0, 500)
    
    # 4. Valida que se muestre el mensaje de error de política de contraseña.
    base_page.element.verificar_texto_exacto(base_page.registro.mensajePoliticaPassword, "InvalidPasswordException: Password did not conform with policy: Password must have uppercase characters", "validar_mensajePoliticaPassword_visible", config.SCREENSHOT_DIR)
    
    # Caso 3: Contraseña sin caracteres especial.
    # ---------------------------------------------
    # 1. Rellena los campos de contraseña con un nuevo valor que incumple la política.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, "12345678aB", "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, "12345678aB", "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR)
    
    # 2. Hace clic en el botón 'Register'.
    base_page.element.hacer_clic_en_elemento(base_page.registro.botonRegistrar, "Clic_con_contraseña_sin_símbolo", config.SCREENSHOT_DIR)
    
    # 3. Realiza un scroll de 500px hacia abajo para asegurarse de que el mensaje de error sea visible en la pantalla.
    base_page.scroll_pagina(0, 500)
    
    # 4. Valida que se muestre el mensaje de error de política de contraseña.
    base_page.element.verificar_texto_exacto(base_page.registro.mensajePoliticaPassword, "InvalidPasswordException: Password did not conform with policy: Password must have symbol characters", "validar_mensajePoliticaPassword_visible", config.SCREENSHOT_DIR)
    
def test_registro_usuario_con_un_caracter(set_up_Registrar: BasePage) -> None:
    """
    Test que valida el registro exitoso de un usuario con un nombre de usuario de un solo carácter.
    
    Este test verifica que el sistema permita registrar usuarios con nombres de usuario
    mínimos, siempre que cumplan con los demás requisitos del formulario. El fixture
    `set_up_Registrar` se encarga de la navegación inicial, permitiendo que el test
    se enfoque en este flujo específico.
    
    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # 1. Rellena el formulario con los datos del nuevo usuario.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, "U", "rellenar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, "Nombre", "rellenar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, "Apaellido", "rellenar_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, "aB.12345678", "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, "aB.12345678", "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR)
    
    # 2. Hace clic en el botón 'Register' para completar el registro.
    base_page.element.hacer_clic_en_elemento(base_page.registro.botonRegistrar, "Clic_botonRegistrar", config.SCREENSHOT_DIR)
    
    # 3. Valida que el mensaje de error de "usuario ya existe" esté presente en la página.
    base_page.element.verificar_texto_contenido(base_page.registro.mensajeUsuarioExistente, "UsernameExistsException", "validar_mensajeErrorUsuarioExistente_visible", config.SCREENSHOT_DIR)
    
def test_registro_usuario_con_dos_caracteres(set_up_Registrar: BasePage) -> None:
    """
    Test que valida el registro exitoso de un usuario con un nombre de usuario de un solo carácter.
    
    Este test verifica que el sistema permita registrar usuarios con nombres de usuario
    mínimos, siempre que cumplan con los demás requisitos del formulario. El fixture
    `set_up_Registrar` se encarga de la navegación inicial, permitiendo que el test
    se enfoque en este flujo específico.
    
    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # 1. Rellena el formulario con los datos del nuevo usuario.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, "Us", "rellenar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, "Nonombre", "rellenar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, "Apellido", "rellenar_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, "aB.12345678", "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, "aB.12345678", "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR)
    
    # 2. Hace clic en el botón 'Register' para completar el registro.
    base_page.element.hacer_clic_en_elemento(base_page.registro.botonRegistrar, "Clic_botonRegistrar", config.SCREENSHOT_DIR)
    
    # 3. Valida que el mensaje de error de "usuario ya existe" esté presente en la página.
    base_page.element.verificar_texto_contenido(base_page.registro.mensajeUsuarioExistente, "UsernameExistsException", "validar_mensajeErrorUsuarioExistente_visible", config.SCREENSHOT_DIR)
    
def test_registro_usuario_exitosamente(set_up_Registrar: BasePage) -> None:
    """
    Test que valida el comportamiento del sistema al intentar registrar un usuario
    con un nombre de usuario que no cumple con el mínimo de caracteres requerido.
    
    Este test verifica que el sistema no permita el registro y muestre un mensaje
    de validación apropiado. Adicionalmente, comprueba que los campos del formulario
    se vacíen o reinicien después del intento fallido, un comportamiento común
    para este tipo de validaciones.
    
    Args:
        set_up_Registrar (BasePage): Fixture que navega a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # Genera los datos del usuario llamando al método
    # Esto devuelve un diccionario con los datos
    datos_usuario = generador_datos.generar_usuario_aleatorio()
    
    # 1. Rellena el formulario con datos que no cumplen los requisitos del nombre de usuario.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, datos_usuario["username"], "rellenar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, datos_usuario["first_name"], "rellenar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, datos_usuario["last_name"], "rellenar_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, datos_usuario["password"], "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, datos_usuario["confirm_password"], "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR) 
    
    # 2. Hace clic en el botón 'Register' para intentar completar el registro.
    base_page.element.hacer_clic_en_elemento(base_page.registro.botonRegistrar, "Clic_botonRegistrar", config.SCREENSHOT_DIR)
    
    # 3. Valida que se muestre un mensaje de usuario registrado exitomsamente.
    base_page.element.verificar_texto_exacto(base_page.registro.mensajeRegistroExitoso, "Registration is successful", "validar_mensajeErrorUsuarioExistente_visible", config.SCREENSHOT_DIR)
    
    # 4. Guarda los datos del usuario registrado en un archivo JSON
    # Define la ruta para el archivo JSON de registros
    file_path_json = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.json")

    # Se usa append=True para añadir los datos al final de una lista en el archivo
    exito_escritura = base_page.file.escribir_json(
        file_path=file_path_json,
        data=datos_usuario,
        append=True,
        nombre_paso="Guardar datos de usuario registrado"
    )

    if not exito_escritura:
        base_page.logger.error("❌ No se pudieron guardar los datos del usuario en el archivo JSON.")
    
    # 5. Guarda los datos del usuario registrado en un archivo Excel
    # Define la ruta para el archivo Excel de registros
    excel_file_path = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, "registros_exitosos.xlsx")

    # Llama a la función escribir_excel para guardar los datos en modo 'append'
    exito_escritura_excel = base_page.file.escribir_excel(
        file_path=excel_file_path,
        data=[datos_usuario], # Se pasa una lista con el diccionario
        append=True,
        header=False, # Se asegura que no se escriban los encabezados si es un archivo nuevo
        nombre_paso="Guardar datos de usuario registrado en Excel"
    )

    if not exito_escritura_excel:
        base_page.logger.error("❌ No se pudieron guardar los datos del usuario en el archivo Excel.")    
    
    # 6. Guarda los datos del usuario registrado en un archivo CSV
    # Define la ruta para el archivo CSV de registros
    file_path_csv = os.path.join(config.SOURCE_FILES_DIR_DATA_SOURCE, 'registros_exitosos.csv')
    
    # Llama a la función escribir_excel para guardar los datos en modo 'append'
    exito_escritura_csv = base_page.file.escribir_csv(
        file_path=file_path_csv,
        data=[datos_usuario], # Se pasa una lista con el diccionario
        append=True,
        nombre_paso="Guardar datos de usuario registrado en CSV_con_encabezado"
    )
        
    # 7. Valida que los campos se hayan vaciado como parte del comportamiento de reinicio de la página.
    base_page.element.validar_elemento_vacio(base_page.registro.campoUserName, "verificar_campoUserName_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoNombre, "verificar_campoNombre_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoApellido, "verificar_campoApellido_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoPassword, "verificar_campoPassword_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoConfirmPassword, "verificar_campoConfirmPassword_vacío", config.SCREENSHOT_DIR)
    
def test_registro_usuario_pre_existente(set_up_Registrar: BasePage) -> None:
    """
    Test que valida el comportamiento del sistema al intentar registrar un usuario
    con un nombre de usuario que ya existe en la base de datos.
    
    Este test verifica que se muestre el mensaje de error adecuado y que el
    usuario no pueda completar el registro. El fixture `set_up_Registrar`
    se encarga de la navegación inicial, permitiendo que el test se enfoque
    en este flujo específico.
    
    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar
    
    # 1. Rellena el formulario con los datos del usuario preexistente.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, "UsY", "rellenar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, "Nombre", "rellenar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, "Apellido", "rellenar_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, "aB.12345678", "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, "aB.12345678", "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR)
    
    # 2. Hace clic en el botón 'Register' para intentar completar el registro.
    base_page.element.hacer_clic_en_elemento(base_page.registro.botonRegistrar, "Clic_botonRegistrar", config.SCREENSHOT_DIR)
    
    # 3. Realiza un scroll de 500px hacia abajo para asegurarse de que el mensaje de error sea visible en la pantalla.
    base_page.scroll_pagina(0, 500)
    
    # 4. Valida que el mensaje de error de "usuario ya existe" esté presente en la página.
    base_page.element.verificar_texto_exacto(base_page.registro.mensajeUsuarioExistente, "UsernameExistsException: User already exists", "validar_mensajeErrorUsuarioExistente_visible", config.SCREENSHOT_DIR)
    
def test_regresar_con_navegador_a_home_desde_registro(set_up_Registrar: BasePage) -> None:
    """
    Test que valida la funcionalidad de regresar a la página de inicio
    utilizando la acción de "volver atrás" del navegador (`page.go_back()`).

    Este test verifica que, después de navegar a la página de registro,
    la acción de retroceder en el historial del navegador redirija correctamente
    al usuario a la página de inicio. El fixture `set_up_Registrar` se encarga de
    la navegación inicial para establecer el historial del navegador.

    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar

    # Paso 1: Simula la acción de volver a la página anterior del navegador.
    # Esta acción utiliza el historial de navegación establecido por el fixture.
    base_page.navigation.volver_a_pagina_anterior("Volver_pagina_anterior", config.SCREENSHOT_DIR)

    # Paso 2: Valida que la URL actual sea la de la página de inicio (BASE_URL).
    base_page.navigation.validar_url_actual(config.BASE_URL)

    # Paso 3: Valida la visibilidad de elementos clave de la página de inicio
    # para confirmar que la navegación fue exitosa y que la página se cargó correctamente.
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesPopularMake, "validar_contenedoresDeOpcionesPopularMake_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesModel, "validar_contenedoresDeOpcionesModel_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesOverallRating, "validar_contenedoresDeOpcionesOverallRating_visible", config.SCREENSHOT_DIR)
    
def test_regresar_a_home_desde_registro_con_logo(set_up_Registrar: BasePage) -> None:
    """
    Test que valida la funcionalidad del logo de la aplicación para regresar a la página de inicio
    desde la página de registro.

    Este test verifica que al hacer clic en el logo 'Buggy Rating', el usuario sea redirigido
    correctamente a la página de inicio. El fixture `set_up_Registrar` se encarga de la
    navegación inicial, posicionando el navegador en la página de registro.

    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar

    # Paso 1: Hace clic en el logo 'Buggy Rating' para regresar a la página de inicio.
    base_page.element.hacer_clic_en_elemento(base_page.home.nombreHome, "Clic_en_logo", config.SCREENSHOT_DIR)

    # Paso 2: Valida que la URL actual sea la de la página de inicio (BASE_URL).
    base_page.navigation.validar_url_actual(config.BASE_URL)

    # Paso 3: Valida la visibilidad de elementos clave de la página de inicio para
    # confirmar que la navegación fue exitosa y que la página se cargó correctamente.
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesPopularMake, "validar_contenedoresDeOpcionesPopularMake_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesModel, "validar_contenedoresDeOpcionesModel_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesOverallRating, "validar_contenedoresDeOpcionesOverallRating_visible", config.SCREENSHOT_DIR)
    
def test_avanzar_con_navegador_desde_home_a_registrar(set_up_Registrar: BasePage) -> None:
    """
    Test que valida el flujo de navegación 'atrás' y 'adelante' del navegador.

    Este test verifica que, después de navegar a la página de registro,
    la acción de retroceder en el historial del navegador (`go_back`)
    y luego la acción de avanzar (`go_forward`) redirijan correctamente al
    usuario a las páginas esperadas. El fixture `set_up_Registrar` establece
    el historial de navegación para este flujo.

    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar

    # Paso 1: Simula la acción de volver a la página anterior en el navegador (de registro a home).
    base_page.navigation.volver_a_pagina_anterior("Volver_pagina_anterior", config.SCREENSHOT_DIR)

    # Paso 2: Valida que la navegación fue exitosa y la URL es la de la página de inicio.
    base_page.navigation.validar_url_actual(config.BASE_URL)

    # Paso 3: Valida la visibilidad de elementos de la página de inicio.
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesPopularMake, "validar_contenedoresDeOpcionesPopularMake_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesModel, "validar_contenedoresDeOpcionesModel_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_visible(base_page.home.contenedoresDeOpcionesOverallRating, "validar_contenedoresDeOpcionesOverallRating_visible", config.SCREENSHOT_DIR)
    
    # Paso 4: Simula la acción de avanzar a la página siguiente del navegador (de home a registro).
    base_page.navigation.avanzar_a_pagina_siguiente("Avanzar_con_navegador_desde_home_a_registro", config.SCREENSHOT_DIR)
    
    # Paso 5: Valida que la navegación fue exitosa y la URL es la de la página de registro.
    base_page.navigation.validar_url_actual(config.REGISTRAR_URL)
    
    # Paso 6: Valida los campos y el estado de los botones en la página de registro.
    # Los campos deben estar vacíos y el botón de registrar deshabilitado.
    base_page.element.validar_elemento_vacio(base_page.registro.campoUserName, "verificar_campoUserName_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajeUserNameVacio, "validar_mensajeUserNameVacio_no_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoNombre, "verificar_campoNombre_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajeNombreVacio, "validar_mensajeNombreVacio_no_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoApellido, "verificar_campoApellido_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajeApellidoVacio, "validar_mensajeApellidoVacio_no_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoPassword, "verificar_campoPassword_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajePasswordVacio, "validar_mensajePasswordVacio_no_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoConfirmPassword, "verificar_campoConfirmPassword_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_no_visible(base_page.registro.mensajeConfirmPasswordVacio, "validar_mensajeConfirmPasswordVacio_no_visible", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_desactivado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_desactivado", config.SCREENSHOT_DIR)
    base_page.element.verificar_elemento_habilitado(base_page.registro.botonCancelar, "verificar_botonCancelar_habilitado", config.SCREENSHOT_DIR)
    
def test_avanzar_con_navegador_desde_home_a_registrar_con_datos(set_up_Registrar: BasePage) -> None:
    """
    Test que valida la preservación de los datos del formulario de registro
    al navegar hacia atrás y luego hacia adelante en el navegador.

    Este test simula la entrada de datos en los campos del formulario de registro,
    luego navega hacia atrás y, al volver a avanzar, verifica que los datos
    ingresados no estén.

    Args:
        set_up_Registrar (BasePage): Fixture que proporciona una instancia de BasePage
                                     con la navegación inicial a la página de registro.
    """
    # Asigna la instancia del fixture a una variable local para mayor claridad.
    base_page = set_up_Registrar

    # Paso 1: Rellena los campos del formulario de registro.
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoUserName, "UsY", "rellenar_campoUserName", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoNombre, "Nombre", "rellenar_campoNombre", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoApellido, "Apellido", "rellenar_campoApellido", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoPassword, "aB.12345678", "rellenar_campoPassword", config.SCREENSHOT_DIR)
    base_page.element.rellenar_campo_de_texto(base_page.registro.campoConfirmPassword, "aB.12345678", "rellenar_campoConfirmPassword", config.SCREENSHOT_DIR)

    # Paso 2: Simula la acción de volver a la página anterior en el navegador (de registro a home).
    base_page.navigation.volver_a_pagina_anterior("Volver_pagina_anterior", config.SCREENSHOT_DIR)

    # Paso 3: Simula la acción de avanzar a la página siguiente del navegador (de home a registro).
    base_page.navigation.avanzar_a_pagina_siguiente("Avanzar_con_navegador_desde_home_a_registro", config.SCREENSHOT_DIR)

    # Paso 4: Valida que la URL actual sea la de la página de registro.
    base_page.navigation.validar_url_actual(config.REGISTRAR_URL)
    
    # Paso 5: Valida que los datos previamente ingresados no se hayan preservado.
    base_page.element.validar_elemento_vacio(base_page.registro.campoUserName, "verificar_campoUserName_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoNombre, "verificar_campoNombre_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoApellido, "verificar_campoApellido_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoPassword, "verificar_campoPassword_vacío", config.SCREENSHOT_DIR)
    base_page.element.validar_elemento_vacio(base_page.registro.campoConfirmPassword, "verificar_campoConfirmPassword_vacío", config.SCREENSHOT_DIR)
    
    # Paso 6: Valida el estado de los botones.
    base_page.element.validar_elemento_desactivado(base_page.registro.botonRegistrar, "verificar_botonRegistrar_desactivado", config.SCREENSHOT_DIR)
    base_page.element.verificar_elemento_habilitado(base_page.registro.botonCancelar, "verificar_botonCancelar_habilitado", config.SCREENSHOT_DIR)
    
