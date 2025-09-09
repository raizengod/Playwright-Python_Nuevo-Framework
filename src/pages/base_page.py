import os
import time
import logging
from datetime import datetime
from typing import Union, Optional, Dict, Any, List

from playwright.sync_api import Page, Dialog, Locator, Error, TimeoutError

# --- Importación de las nuevas clases de acciones ---
from .actions_elementos import ElementActions
from .actions_tablas import TableActions
from .actions_archivos import FileActions
from .actions_dialogos import DialogActions
from .actions_dropdowns import DropdownActions
from .actions_teclado import KeyboardActions
from .actions_navegacion import NavigationActions

from src.utils.logger import setup_logger
from src.utils.config import LOGGER_DIR, SCREENSHOT_DIR

# Asegúrate de importar la clase de localizadores
from src.locator.locator_home import HomeLocatorsPage
from src.locator.locator_registro import RegistroLocatorsPage
from src.locator.locator_login import LoginLocatorsPage
from src.locator.locator_dashboard import DasboardLocatorsPage

class BasePage:
    """
    Clase base que actúa como un agregador para todas las clases de acciones.
    Inicializa la página, el logger y todas las clases de acciones específicas,
    proporcionando un punto de entrada único y organizado para las pruebas.
    """

    #1- Creamos una función incial 'Constructor'-----ES IMPORTANTE TENER ESTE INICIADOR-----
    def __init__(self, page: Page):
        """
        Inicializa la clase Funciones_Globales con un objeto Page de Playwright.

        Args:
            page (Page): El objeto de página de Playwright que representa la pestaña
                         del navegador activa.
        """
        self.page = page
        self.logger = setup_logger(name='AutomationFramework', console_level=logging.INFO, file_level=logging.DEBUG)
        
        # --- Banderas para manejo de eventos de diálogo ---
        self._alerta_detectada = False
        self._alerta_mensaje_capturado = ""
        self._alerta_tipo_capturado = ""
        self._alerta_input_capturado = ""
        
        # --- Banderas para manejo de nuevas pestañas (popups) ---
        self._all_new_pages_opened_by_click: List[Page] = []
        self.page.context.on("page", self._on_new_page)
        
        # --- Instanciación de las clases de acciones (mejora de arquitectura) ---
        self.element = ElementActions(self)
        self.table = TableActions(self)
        self.file = FileActions(self)
        self.dialog = DialogActions(self)
        self.dropdown = DropdownActions(self)
        self.keyboard = KeyboardActions(self)
        self.navigation = NavigationActions(self)
        
        # --- Instancia de la clase de localizadores de la página de inicio ---
        self.home = HomeLocatorsPage(self.page)
        self.registro = RegistroLocatorsPage(self.page)
        self.login = LoginLocatorsPage(self.page)
        self.dashboard = DasboardLocatorsPage(self.page)
        
    #2- Función para generar el nombre de archivo con marca de tiempo
    def _generar_nombre_archivo_con_timestamp(self, prefijo):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3] # Quita los últimos 3 dígitos para milisegundos más precisos
        return f"{timestamp}_{prefijo}"
    
    #3- Función para tomar captura de pantalla
    def tomar_captura(self, nombre_base, directorio):
        """
        Toma una captura de pantalla de la página y la guarda en el directorio especificado.
        Por defecto, usa SCREENSHOT_DIR de config.py.

        Args:
            nombre_base (str): El nombre base para el archivo de la captura de pantalla.
            directorio (str): El directorio donde se guardará la captura. Por defecto, SCREENSHOT_DIR.
        """
        try:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
                self.logger.info(f"\n Directorio creado para capturas de pantalla: {directorio}") #

            nombre_archivo = self._generar_nombre_archivo_con_timestamp(nombre_base) #
            ruta_completa = os.path.join(directorio, f"{nombre_archivo}.png") # Cambiado a .png para mejor calidad
            self.page.screenshot(path=ruta_completa) #
            self.logger.info(f"\n 📸 Captura de pantalla guardada en: {ruta_completa}") #
        except Exception as e:
            self.logger.error(f"\n ❌ Error al tomar captura de pantalla '{nombre_base}': {e}") #
        
    #4- unción basica para tiempo de espera que espera recibir el parametro tiempo
    #En caso de no pasar el tiempo por parametro, el mismo tendra un valor de medio segundo
    def esperar_fijo(self, tiempo=0.5):
        """
        Espera un tiempo fijo en segundos.

        Args:
            tiempo (Union[int, float]): El tiempo en segundos a esperar. Por defecto, 0.5 segundos.
        """
        self.logger.debug(f"\n Esperando fijo por {tiempo} segundos...") #
        try:
            time.sleep(tiempo) #
            self.logger.info(f"Espera fija de {tiempo} segundos completada.") #
        except TypeError:
            self.logger.error(f"\n ❌ Error: El tiempo de espera debe ser un número. Se recibió: {tiempo}") #
        except Exception as e:
            self.logger.error(f"\n ❌ Ocurrió un error inesperado durante la espera fija: {e}") #
        
    #5- Función para indicar el tiempo que se tardará en hacer el scroll
    def scroll_pagina(self, horz, vert, tiempo: Union[int, float] = 0.5):
        """
        Realiza un scroll en la página.

        Args:
            horz (int): Cantidad de scroll horizontal. Por defecto, 0.
            vert (int): Cantidad de scroll vertical. Por defecto, 0.
            tiempo (Union[int, float]): Tiempo de espera después del scroll en segundos. Por defecto, 0.5.
        """
        self.logger.debug(f"Realizando scroll - Horizontal: {horz}, Vertical: {vert}. Espera: {tiempo} segundos.") #
        try:
            # --- Medición de rendimiento: Inicio de la acción de scroll ---
            start_time_scroll_action = time.time()
            self.page.mouse.wheel(horz, vert)
            # --- Medición de rendimiento: Fin de la acción de scroll ---
            end_time_scroll_action = time.time()
            duration_scroll_action = end_time_scroll_action - start_time_scroll_action
            self.logger.info(f"PERFORMANCE: Duración de la acción de scroll (Playwright API): {duration_scroll_action:.4f} segundos.")
            
            self.esperar_fijo(tiempo) # Reutiliza la función esperar_fijo para el log y manejo de errores
            self.logger.info(f"Scroll completado (H: {horz}, V: {vert}).") #
        except Exception as e:
            self.logger.error(f"❌ Error al realizar scroll en la página: {e}") #
    
    #79- Función para indicar el tiempo que se tardará en hacer el scroll en pagina movil
    def scroll_pangina_tactil(self, vert: int, nombre_base: str, directorio: str, tiempo_deslizamiento_ms: int = 500) -> None:
        """
        Realiza un scroll vertical simulando un gesto táctil de deslizamiento (swipe).
        Esta función está optimizada para dispositivos móviles y tabletas.

        Args:
            vert (int): La cantidad de píxeles a desplazar verticalmente. Un valor positivo
                        se desliza hacia arriba (mostrando contenido de abajo), y un valor negativo
                        se desliza hacia abajo (mostrando contenido de arriba).
            nombre_base (str): Nombre base para las capturas de pantalla si hay un error.
            directorio (str): Ruta del directorio para guardar las capturas.
            tiempo_deslizamiento_ms (int): Duración del gesto de deslizamiento en milisegundos.
                                        Un valor más alto simula un deslizamiento más lento.
        """
        nombre_paso = f"Desplazamiento táctil (Swipe) vertical: {vert} píxeles"
        self.logger.info(f"\n--- {nombre_paso} ---")

        # --- Medición de rendimiento: Inicio de la acción de scroll táctil ---
        start_time = time.time()
        
        # Define un punto fijo en la pantalla para el inicio y el fin del gesto.
        # Se usa 500 como punto de referencia para el ancho (centro) y se ajusta la altura.
        start_x = 500
        
        # Puntos de inicio y fin para el gesto de deslizamiento
        # Un valor 'vert' positivo simula un swipe de abajo hacia arriba.
        # Un valor 'vert' negativo simula un swipe de arriba hacia abajo.
        start_y = 500
        end_y = 500 + vert
        
        self.logger.debug(f"\n Simulando swipe desde ({start_x}, {start_y}) a ({start_x}, {end_y})")

        try:
            # 1. Toca la pantalla en el punto de inicio.
            self.page.touchscreen.touch_start(start_x, start_y)
            
            # 2. Mueve el dedo para simular el desplazamiento.
            self.page.touchscreen.touch_move(start_x, end_y)
            
            # 3. Levanta el dedo para finalizar el gesto.
            self.page.touchscreen.touch_end(start_x, end_y)
            
            # Espera a que la animación de scroll se complete en la UI
            time.sleep(tiempo_deslizamiento_ms / 1000)

            # --- Medición de rendimiento: Fin de la acción ---
            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"\n✅ ÉXITO: Desplazamiento táctil completado en {duration:.4f} segundos.")
            
        except Error as e:
            error_msg = (
                f"\n❌ FALLO (Playwright Error): Ocurrió un error al realizar el scroll táctil."
                f"\nDetalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.tomar_captura(f"{nombre_base}_fallo_scroll_tactil_playwright", directorio)
            raise AssertionError(error_msg) from e
        
        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado durante el scroll táctil."
                f"\nDetalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.tomar_captura(f"{nombre_base}_fallo_scroll_tactil_inesperado", directorio)
            raise AssertionError(error_msg) from e
        
    # --- Manejadores y funciones para Alertas y Confirmaciones ---

    # Handler para alertas simples (usado con page.once).
    # Este handler captura información de la alerta y la acepta. Integra medición de rendimiento.
    def _get_simple_alert_handler_for_on(self):
        """
        Retorna una función handler (callback) diseñada para ser usada con `page.on('dialog', handler)`.
        
        Este handler:
        - Marca una bandera interna (`_alerta_detectada`) a True.
        - Captura el mensaje y el tipo del diálogo (`dialog.message`, `dialog.type`).
        - Registra información sobre la alerta detectada.
        - Mide el tiempo que tarda la lógica interna del handler en ejecutarse.
        - Acepta automáticamente el diálogo (`dialog.accept()`).
        - Registra la acción de aceptar el diálogo.

        Esta función no toma parámetros de selector o capturas de pantalla directas porque
        es un callback de evento que Playwright invoca.

        Returns:
            callable: Una función que toma un objeto `Dialog` como argumento y maneja la alerta.
        """
        # Se reinician las banderas para cada nueva creación del handler, útil si se usa page.once repetidamente
        self._alerta_detectada = False 
        self._alerta_mensaje_capturado = ""
        self._alerta_tipo_capturado = ""

        def handler(dialog: Dialog):
            """
            Función callback interna que se ejecuta cuando Playwright detecta un diálogo (alerta, confirmación, etc.).
            """
            # --- Medición de rendimiento: Inicio de la ejecución del handler ---
            start_time_handler_execution = time.time()
            self.logger.info(f"\n--- [LISTENER START] Procesando diálogo tipo: '{dialog.type}'. ---")

            try:
                self._alerta_detectada = True
                self._alerta_mensaje_capturado = dialog.message
                self._alerta_tipo_capturado = dialog.type
                
                self.logger.info(f"\n--> [LISTENER ON - Simple Alert] Alerta detectada: Tipo='{dialog.type}', Mensaje='{dialog.message}'")
                
                # Aceptamos el diálogo. Esto simula hacer clic en "Aceptar" o "OK".
                # Para un 'prompt', puedes pasar un texto: dialog.accept("texto de respuesta")
                dialog.accept() 
                self.logger.info("\n--> [LISTENER ON - Simple Alert] Alerta ACEPTADA.")

            except Exception as e:
                # Captura cualquier error que ocurra dentro del handler.
                # Es crucial aquí no re-lanzar, ya que podría romper el listener de Playwright.
                self.logger.error(f"\n❌ ERROR en el handler de alerta para '{dialog.type}' (Mensaje: '{dialog.message}'). Detalles: {e}", exc_info=True)
            finally:
                # --- Medición de rendimiento: Fin de la ejecución del handler ---
                end_time_handler_execution = time.time()
                duration_handler_execution = end_time_handler_execution - start_time_handler_execution
                self.logger.info(f"PERFORMANCE: Tiempo de ejecución del handler de alerta: {duration_handler_execution:.4f} segundos.")
                self.logger.info("\n--- [LISTENER END] Diálogo procesado. ---")

        return handler

    # Handler para diálogos de confirmación (usado con page.once).
    # Este handler captura información del diálogo, realiza una acción configurable (aceptar/descartar),
    # y registra métricas de rendimiento.
    def _get_confirmation_dialog_handler_for_on(self, accion: str):
        """
        Retorna una función handler (callback) diseñada para ser usada con `page.on('dialog', handler)`.
        Este handler está específicamente diseñado para diálogos de tipo 'confirm' o 'prompt',
        permitiendo decidir dinámicamente si se acepta o se descarta el diálogo.

        Este handler:
        - Marca una bandera interna (`_alerta_detectada`) a True.
        - Captura el mensaje y el tipo del diálogo (`dialog.message`, `dialog.type`).
        - Registra información sobre el diálogo detectado.
        - Mide el tiempo que tarda la lógica interna del handler en ejecutarse.
        - Realiza la acción especificada ('accept' o 'dismiss') en el diálogo.
        - Registra la acción tomada.
        - Por defecto, si la acción no es 'accept' ni 'dismiss', acepta el diálogo y emite una advertencia.

        Args:
            accion (str): La acción a realizar en el diálogo. Puede ser 'accept' para aceptar
                          o 'dismiss' para cancelar/descartar.

        Returns:
            callable: Una función que toma un objeto `Dialog` como argumento y maneja el diálogo.
        """
        # Se reinician las banderas para cada nueva creación del handler, útil si se usa page.once repetidamente
        self._alerta_detectada = False 
        self._alerta_mensaje_capturado = ""
        self._alerta_tipo_capturado = ""

        def handler(dialog: Dialog):
            """
            Función callback interna que se ejecuta cuando Playwright detecta un diálogo
            (especialmente 'confirm' o 'prompt').
            """
            # --- Medición de rendimiento: Inicio de la ejecución del handler ---
            start_time_handler_execution = time.time()
            self.logger.info(f"\n--- [LISTENER START] Procesando diálogo de confirmación tipo: '{dialog.type}'. ---")

            try:
                self._alerta_detectada = True
                self._alerta_mensaje_capturado = dialog.message
                self._alerta_tipo_capturado = dialog.type
                
                self.logger.info(f"\n--> [LISTENER ON - Dinámico] Diálogo detectado: Tipo='{dialog.type}', Mensaje='{dialog.message}'")
                
                if accion == 'accept':
                    # Acepta el diálogo (equivalente a hacer clic en "OK" o "Aceptar").
                    # Para un prompt, puedes pasar un valor: dialog.accept("mi respuesta")
                    dialog.accept()
                    self.logger.info("\n--> [LISTENER ON - Dinámico] Diálogo ACEPTADO.")
                elif accion == 'dismiss':
                    # Descarta/cancela el diálogo (equivalente a hacer clic en "Cancelar").
                    dialog.dismiss()
                    self.logger.info("\n--> [LISTENER ON - Dinámico] Diálogo CANCELADO/DESCARTADO.")
                else:
                    # En caso de acción no reconocida, se registra una advertencia y se acepta por defecto.
                    self.logger.warning(f"\n--> [LISTENER ON - Dinámico] Acción desconocida '{accion}' para el diálogo '{dialog.type}'. Aceptando por defecto.")
                    dialog.accept()
                    self.logger.info("\n--> [LISTENER ON - Dinámico] Diálogo ACEPTADO por defecto debido a acción inválida.")

            except Exception as e:
                # Captura cualquier error que ocurra dentro del handler.
                # Es crucial aquí no re-lanzar, ya que podría romper el listener de Playwright.
                self.logger.error(f"\n❌ ERROR en el handler de diálogo para '{dialog.type}' (Mensaje: '{dialog.message}', Acción: '{accion}'). Detalles: {e}", exc_info=True)
            finally:
                # --- Medición de rendimiento: Fin de la ejecución del handler ---
                end_time_handler_execution = time.time()
                duration_handler_execution = end_time_handler_execution - start_time_handler_execution
                self.logger.info(f"PERFORMANCE: Tiempo de ejecución del handler de diálogo de confirmación: {duration_handler_execution:.4f} segundos.")
                self.logger.info("\n--- [LISTENER END] Diálogo procesado. ---")

        return handler
    
    # Handler para diálogos de pregunta (prompt) (usado con page.once).
    # Este handler captura información del diálogo prompt, introduce un texto opcional,
    # realiza una acción configurable (aceptar/descartar), y registra métricas de rendimiento.
    def _get_prompt_dialog_handler_for_on(self, input_text: str = "", accion: str = "accept"):
        """
        Retorna una función handler (callback) diseñada para ser usada con `page.on('dialog', handler)`.
        Este handler está específicamente diseñado para diálogos de tipo 'prompt', permitiendo
        introducir texto y decidir dinámicamente si se acepta o se descarta el diálogo.

        Este handler:
        - Marca una bandera interna (`_alerta_detectada`) a True.
        - Captura el mensaje, el tipo del diálogo y el texto de entrada (`dialog.message`, `dialog.type`, `input_text`).
        - Registra información sobre el diálogo detectado.
        - Mide el tiempo que tarda la lógica interna del handler en ejecutarse.
        - Realiza la acción especificada ('accept' o 'dismiss') en el diálogo.
        - Si la acción es 'accept' y el tipo de diálogo es 'prompt', introduce el `input_text`.
        - Registra la acción tomada.
        - Por defecto, si la acción no es 'accept' ni 'dismiss', descarta el diálogo y emite una advertencia.

        Args:
            input_text (str, opcional): El texto a introducir en el campo de entrada del prompt si se acepta.
                                        Por defecto es una cadena vacía "".
            accion (str, opcional): La acción a realizar en el diálogo. Puede ser 'accept' para aceptar
                                    o 'dismiss' para cancelar/descartar. Por defecto es 'accept'.

        Returns:
            callable: Una función que toma un objeto `Dialog` como argumento y maneja el diálogo.
        """
        # Se reinician las banderas para cada nueva creación del handler
        self._alerta_detectada = False 
        self._alerta_mensaje_capturado = ""
        self._alerta_tipo_capturado = ""
        self._alerta_input_capturado = ""

        def handler(dialog: Dialog):
            """
            Función callback interna que se ejecuta cuando Playwright detecta un diálogo
            (especialmente de tipo 'prompt').
            """
            # --- Medición de rendimiento: Inicio de la ejecución del handler ---
            start_time_handler_execution = time.time()
            self.logger.info(f"\n--- [LISTENER START] Procesando diálogo de prompt tipo: '{dialog.type}'. ---")

            try:
                self._alerta_detectada = True
                self._alerta_mensaje_capturado = dialog.message
                self._alerta_tipo_capturado = dialog.type
                self._alerta_input_capturado = input_text # Almacena el texto que se intentó introducir

                self.logger.info(f"\n--> [LISTENER ON - Prompt Dinámico] Diálogo detectado: Tipo='{dialog.type}', Mensaje='{dialog.message}'.")
                
                if accion == 'accept':
                    if dialog.type == "prompt":
                        # Acepta el prompt e introduce el texto proporcionado.
                        dialog.accept(input_text)
                        self.logger.info(f"\n--> [LISTENER ON - Prompt Dinámico] Texto '{input_text}' introducido y prompt ACEPTADO.")
                    else:
                        # Si no es un prompt pero se especificó 'accept', lo acepta sin texto.
                        self.logger.warning(f"\n--> [LISTENER ON - Prompt Dinámico] Se solicitó 'accept' con texto para un diálogo no-prompt ('{dialog.type}'). Aceptando sin texto.")
                        dialog.accept()
                        self.logger.info("\n--> [LISTENER ON - Prompt Dinámico] Diálogo ACEPTADO (sin texto, no es prompt).")
                elif accion == 'dismiss':
                    # Descarta/cancela el diálogo. El texto de input_text se ignora.
                    dialog.dismiss()
                    self.logger.info("\n--> [LISTENER ON - Prompt Dinámico] Diálogo CANCELADO/DESCARTADO.")
                else:
                    # En caso de acción no reconocida, se registra una advertencia y se descarta por defecto.
                    # Se elige 'dismiss' como valor por defecto más seguro para evitar que el prompt
                    # se quede abierto y bloquee la ejecución si la acción es inválida.
                    self.logger.warning(f"\n--> [LISTENER ON - Prompt Dinámico] Acción desconocida '{accion}' para el diálogo '{dialog.type}'. Descartando por defecto.")
                    dialog.dismiss()
                    self.logger.info("\n--> [LISTENER ON - Prompt Dinámico] Diálogo DESCARTADO por defecto debido a acción inválida.")

            except Exception as e:
                # Captura cualquier error que ocurra dentro del handler.
                # Es crucial aquí no re-lanzar, ya que podría romper el listener de Playwright.
                self.logger.error(f"\n❌ ERROR en el handler de prompt para '{dialog.type}' (Mensaje: '{dialog.message}', Acción: '{accion}', Texto: '{input_text}'). Detalles: {e}", exc_info=True)
            finally:
                # --- Medición de rendimiento: Fin de la ejecución del handler ---
                end_time_handler_execution = time.time()
                duration_handler_execution = end_time_handler_execution - start_time_handler_execution
                self.logger.info(f"PERFORMANCE: Tiempo de ejecución del handler de diálogo de prompt: {duration_handler_execution:.4f} segundos.")
                self.logger.info("\n--- [LISTENER END] Diálogo procesado. ---")

        return handler

    # Handler de eventos para cuando se abre una nueva página (popup/nueva pestaña).
    # Este handler se encarga de detectar y registrar información sobre nuevas páginas,
    # y también mide el tiempo de procesamiento interno.
    def _on_new_page(self, page: Page):
        """
        Manejador de eventos (callback) para detectar nuevas páginas o ventanas emergentes (popups)
        que se abren, por ejemplo, al hacer clic en un enlace con `target="_blank"`.
        
        Este handler:
        - Marca una bandera interna (`_popup_detectado`) a True.
        - Almacena la referencia al objeto `Page` de la nueva ventana.
        - Captura la URL y el título de la nueva página.
        - Añade la nueva página a una lista de todas las páginas detectadas.
        - Registra información sobre la nueva página detectada.
        - Mide el tiempo que tarda la lógica interna del handler en ejecutarse.

        Args:
            page (Page): El objeto `Page` de Playwright que representa la nueva ventana/pestaña abierta.
                         Este es proporcionado automáticamente por Playwright cuando se dispara el evento.
        """
        # --- Medición de rendimiento: Inicio de la ejecución del handler ---
        start_time_handler_execution = time.time()
        self.logger.info("\n--- [LISTENER START] Procesando evento de nueva página. ---")

        try:
            self._popup_detectado = True
            self._popup_page = page
            self._popup_url_capturado = page.url
            # El title() puede requerir una pequeña espera si la página no ha cargado lo suficiente.
            # Sin embargo, para un handler que debe ser rápido, se asume que estará disponible.
            # Si el título no se obtiene inmediatamente, podría ser None o vacío.
            self._popup_title_capturado = page.title() 
            self._all_new_pages_opened_by_click.append(page) # Añadir la nueva página a la lista

            self.logger.info(f"\n🌐 Nueva página (popup/pestaña) detectada. URL: '{page.url}', Título: '{page.title()}'")
            # Opcional: Si solo te interesa la primera popup o una específica, podrías manejarlo aquí.
            # Por ahora, solo la añadimos a la lista para seguimiento.

        except Exception as e:
            # Es crucial capturar excepciones en handlers para evitar que Playwright deshabilite el listener.
            self.logger.error(f"\n❌ ERROR en el handler de nueva página. Detalles: {e}", exc_info=True)
        finally:
            # --- Medición de rendimiento: Fin de la ejecución del handler ---
            end_time_handler_execution = time.time()
            duration_handler_execution = end_time_handler_execution - start_time_handler_execution
            self.logger.info(f"PERFORMANCE: Tiempo de ejecución del handler de nueva página: {duration_handler_execution:.4f} segundos.")
            self.logger.info("\n--- [LISTENER END] Evento de nueva página procesado. ---")
        
    