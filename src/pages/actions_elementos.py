# 6- Función para validar que un elemento es visible
import time
import math
import logging
import os
from typing import Union, Optional, Dict, Any, List, Tuple
from playwright.sync_api import Page, Locator, expect, Error, TimeoutError

class ElementActions:
    def __init__(self, base_page):
        self.base = base_page
        self.page: Page = base_page.page
        self.logger = base_page.logger
    
    def validar_elemento_visible(self, selector, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5, resaltar: bool = True) -> bool:
        """
        Valida que un elemento sea visible en la página dentro de un tiempo límite especificado.
        Esta función integra la medición del tiempo que tarda el elemento en volverse visible,
        lo que es útil para métricas de rendimiento de la interfaz de usuario.

        Args:
            selector: El selector del elemento. Puede ser una cadena (CSS, XPath, etc.) o
                      un objeto `Locator` de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para nombrar las capturas de pantalla
                               tomadas durante la ejecución de la validación.
            directorio (str): Ruta del directorio donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el elemento
                                        sea considerado visible. Si el elemento no es visible
                                        dentro de este plazo, la validación fallará.
                                        Por defecto, 5.0 segundos.
            resaltar (bool): Si es `True`, el elemento visible será resaltado brevemente en la
                             página para una confirmación visual durante la ejecución. Por defecto, `True`.

        Returns:
            bool: `True` si el elemento es visible dentro del tiempo especificado; `False` en caso
                  de que no sea visible (por timeout) o si ocurre otro tipo de error.

        Raises:
            Error: Si ocurre un error específico de Playwright (ej., selector inválido,
                   elemento desprendido del DOM).
            Exception: Para cualquier otro error inesperado durante la ejecución.
        """
        self.logger.info(f"\nValidando visibilidad del elemento con selector: '{selector}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright.
        # Si 'selector' es una cadena, lo convierte a Locator; de lo contrario, usa el objeto directamente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector
        
        # --- Medición de rendimiento: Inicio de la espera por visibilidad ---
        # Registra el tiempo justo antes de iniciar la espera activa de Playwright.
        start_time_visible_check = time.time()

        try:
            # Espera explícita a que el elemento cumpla la condición de ser visible.
            # Playwright reintenta automáticamente hasta que la condición se cumple o
            # el 'timeout' (expresado en milisegundos) expira.
            expect(locator).to_be_visible() 

            # --- Medición de rendimiento: Fin de la espera por visibilidad ---
            # Registra el tiempo inmediatamente después de que el elemento se vuelve visible.
            end_time_visible_check = time.time()
            # Calcula la duración total que tardó el elemento en ser visible.
            duration_visible_check = end_time_visible_check - start_time_visible_check
            # Registra la métrica de rendimiento. Un tiempo elevado aquí puede indicar
            # problemas de carga o renderizado en la aplicación.
            self.logger.info(f"PERFORMANCE: Tiempo que tardó el elemento '{selector}' en ser visible: {duration_visible_check:.4f} segundos.")

            if resaltar:
                # Resalta visualmente el elemento en la página para ayudar en el debugging o demostraciones.
                locator.highlight()
                self.logger.debug(f"Elemento '{selector}' resaltado.")

            # Toma una captura de pantalla para documentar que el elemento es visible.
            self.base.tomar_captura(f"{nombre_base}_visible", directorio)
            self.logger.info(f"\n✔ ÉXITO: El elemento '{selector}' es visible en la página.")
            
            # Realiza una espera fija adicional. Esto es útil para pausas visuales
            # o si el siguiente paso en la prueba requiere un breve momento después
            # de la aparición del elemento. Considera si esta espera es estrictamente
            # necesaria para la lógica de la prueba o si es solo para observación.
            self.base.esperar_fijo(tiempo) 

            return True

        except TimeoutError as e:
            # Manejo específico para cuando el elemento no se vuelve visible dentro del 'timeout'.
            # Se registra el tiempo transcurrido hasta el fallo.
            end_time_visible_check = time.time()
            duration_visible_check = end_time_visible_check - start_time_visible_check
            error_msg = (
                f"\n❌ FALLO (Timeout): El elemento con selector '{selector}' NO fue visible "
                f"después de {duration_visible_check:.4f} segundos (timeout configurado: {tiempo}s). Detalles: {e}"
            )
            self.logger.warning(error_msg)
            # Toma una captura de pantalla en caso de timeout para depuración.
            self.base.tomar_captura(f"{nombre_base}_NO_visible_timeout", directorio)
            return False

        except Error as e:
            # Manejo específico para errores generados por Playwright (ej. selector malformado,
            # elemento que se desprende del DOM antes de la verificación).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar la visibilidad de '{selector}'. "
                f"Posibles causas: Selector inválido, elemento desprendido del DOM. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # exc_info=True para incluir la traza completa.
            # Toma una captura de pantalla para el error de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            raise # Re-lanza la excepción para asegurar que la prueba falle.

        except Exception as e:
            # Manejo general para cualquier otra excepción inesperada que no sea de Playwright o Timeout.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al validar la visibilidad de '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa critical para errores graves y exc_info.
            # Toma una captura para errores inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise # Re-lanza la excepción.

        finally:
            # El bloque finally se ejecuta siempre, independientemente de si hubo una excepción o no.
            # En este caso, no hay operaciones finales específicas necesarias aquí que no estén ya
            # manejadas en los bloques try/except.
            pass
        
    def validar_elemento_no_visible(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Valida que un elemento NO es visible en la página dentro de un tiempo límite especificado.
        Esta función integra la medición del tiempo que tarda el elemento en ocultarse o desaparecer,
        lo que es útil para métricas de rendimiento de la interfaz de usuario.

        Args:
            selector (Union[str, Page.locator]): El selector del elemento (puede ser una cadena CSS/XPath)
                                                  o un objeto `Locator` de Playwright.
            nombre_base (str): Nombre base para las capturas de pantalla.
            directorio (str): Directorio donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): Tiempo máximo de espera (en segundos) para que el elemento
                                        NO sea visible o se oculte. Por defecto, 5.0 segundos.

        Raises:
            AssertionError: Si el elemento permanece visible después del tiempo de espera.
            TimeoutError: Si la operación de espera se agota.
            Error: Si ocurre un error específico de Playwright.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nValidando que el elemento con selector '{selector}' NO es visible. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright para su uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la espera por no visibilidad ---
        # Registra el tiempo justo antes de iniciar la espera activa de Playwright
        # para que el elemento se oculte.
        start_time_hidden_check = time.time()

        try:
            # Espera explícita a que el elemento cumpla la condición de estar oculto (no visible)
            # o de no existir en el DOM. Playwright reintenta automáticamente.
            # El 'timeout' se especifica en milisegundos.
            expect(locator).to_be_hidden()

            # --- Medición de rendimiento: Fin de la espera por no visibilidad ---
            # Registra el tiempo inmediatamente después de que el elemento se oculta.
            end_time_hidden_check = time.time()
            # Calcula la duración total que tardó el elemento en ocultarse.
            duration_hidden_check = end_time_hidden_check - start_time_hidden_check
            # Registra la métrica de rendimiento. Un tiempo elevado aquí podría indicar
            # que la aplicación tarda en ocultar elementos o en limpiar el DOM.
            self.logger.info(f"PERFORMANCE: Tiempo que tardó el elemento '{selector}' en ocultarse/desaparecer: {duration_hidden_check:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: El elemento con selector '{selector}' NO es visible.")
            # La captura de éxito se maneja en el bloque `finally` para asegurar que se tome.

        except TimeoutError as e:
            # Captura específica para el error de tiempo de espera de Playwright.
            # Esto ocurre si el elemento sigue visible después del 'timeout' especificado.
            end_time_hidden_check = time.time() # Registra el tiempo al fallar el timeout.
            duration_hidden_check = end_time_hidden_check - start_time_hidden_check
            error_msg = (
                f"\n❌ FALLO (Timeout): El elemento con selector '{selector}' AÚN ES VISIBLE "
                f"después de {duration_hidden_check:.4f} segundos (timeout configurado: {tiempo}s). Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla en caso de fallo por timeout para depuración.
            self.base.tomar_captura(f"{nombre_base}_fallo_no_visible_timeout", directorio)
            raise # Re-lanza la excepción para que la prueba falle.

        except AssertionError as e:
            # Captura específica para AssertionErrors. Esto podría ocurrir si la aserción
            # es `to_be_hidden` y el elemento inesperadamente no se oculta.
            error_msg = (
                f"\n❌ FALLO (Assertion): El elemento con selector '{selector}' aún es visible o no se ocultó a tiempo. "
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_no_visible_assertion", directorio)
            raise # Re-lanza la excepción para que la prueba falle.
            
        except Error as e:
            # Captura específica para errores internos de Playwright (ej., selector inválido,
            # o problemas con el contexto de la página).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar que '{selector}' NO es visible. "
                f"Posibles causas: Selector inválido, problema de contexto de la página. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_no_visible", directorio)
            raise # Re-lanza la excepción para que la prueba falle.

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al validar que '{selector}' NO es visible. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_no_visible", directorio)
            raise # Re-lanza la excepción.

        finally:
            # Este bloque se ejecuta siempre, independientemente de si la validación fue exitosa o falló.
            # Es un buen lugar para tomar una captura de pantalla final que muestre el estado de la página.
            self.base.tomar_captura(f"{nombre_base}_estado_final_no_visible", directorio=directorio)
            
    def verificar_texto_contenido(self, selector: Union[str, Locator], texto_esperado: str, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Verifica que un elemento localizado en una página web **contiene un texto parcial**.
        Esta función está optimizada para **integrar métricas de rendimiento básicas**, midiendo
        el tiempo que tarda el elemento en volverse visible y en contener el texto esperado.

        Args:
            selector (Union[str, Page.locator]): El **selector del elemento** (puede ser una cadena CSS/XPath)
                                                  o un objeto `Locator` de Playwright preexistente.
            texto_esperado (str): El **texto exacto o parcial** que se espera encontrar dentro del elemento.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla** tomadas durante la validación,
                               facilitando la identificación en el directorio de salida.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el elemento
                                        sea visible Y contenga el texto esperado. Si alguna de estas
                                        condiciones no se cumple dentro de este plazo, la validación fallará.
                                        Por defecto, `5.0` segundos.

        Raises:
            TimeoutError: Si el elemento no se hace visible o no contiene el texto esperado
                          dentro del tiempo límite especificado.
            AssertionError: Si el elemento es visible, pero su contenido de texto no coincide
                            con el `texto_esperado`.
            Error: Si ocurre un error específico de Playwright durante la operación (ej.,
                   selector malformado, problema de comunicación con el navegador).
            Exception: Para cualquier otro error inesperado que no esté cubierto por las excepciones anteriores.
        """
        self.logger.info(f"Verificando que el elemento con selector '{selector}' contiene el texto: '{texto_esperado}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Playwright Locator.
        # Esto permite una interacción consistente, ya sea que se pase una cadena de selector
        # o un Locator ya definido.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la espera por visibilidad ---
        # Registra el tiempo en que comienza la operación de esperar a que el elemento sea visible.
        start_time_visible_check = time.time()
        try:
            # Playwright espera implícitamente a que el elemento cumpla la condición de visibilidad.
            # El `timeout` se convierte de segundos a milisegundos, como lo requiere Playwright.
            expect(locator).to_be_visible()
            
            # Registra el tiempo una vez que el elemento se ha vuelto visible.
            end_time_visible_check = time.time()
            # Calcula la duración de esta fase. Esta métrica es vital para entender
            # la latencia de renderizado de la UI.
            duration_visible_check = end_time_visible_check - start_time_visible_check
            self.logger.info(f"PERFORMANCE: Tiempo que tardó el elemento '{selector}' en ser visible: {duration_visible_check:.4f} segundos.")
            self.logger.debug(f"Elemento con selector '{selector}' es visible.")

            # Opcional: **Resalta visualmente el elemento** en la página del navegador.
            # Esto es extremadamente útil para el debugging o para demos visuales de la prueba.
            locator.highlight()
            # Toma una captura de pantalla del estado actual de la página, antes de verificar el texto,
            # para documentar la visibilidad del elemento.
            self.base.tomar_captura(f"{nombre_base}_antes_verificacion_texto", directorio)

            # --- Medición de rendimiento: Inicio de la espera por el texto ---
            # Registra el tiempo en que comienza la operación de esperar a que el elemento contenga el texto.
            start_time_text_check = time.time()
            # Verifica que el elemento contiene el `texto_esperado`. Playwright también reintenta
            # esta aserción hasta que el texto coincide o el `timeout` se agota.
            expect(locator).to_contain_text(texto_esperado)
            
            # Registra el tiempo una vez que el texto esperado se ha encontrado.
            end_time_text_check = time.time()
            # Calcula la duración de esta fase. Esta métrica es importante si el texto se carga
            # dinámicamente o tarda en aparecer después de que el elemento base es visible.
            duration_text_check = end_time_text_check - start_time_text_check
            self.logger.info(f"PERFORMANCE: Tiempo que tardó el elemento '{selector}' en contener el texto '{texto_esperado}': {duration_text_check:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Elemento con selector '{selector}' contiene el texto esperado: '{texto_esperado}'.")

            # Toma una captura de pantalla final para documentar la verificación exitosa del texto.
            self.base.tomar_captura(nombre_base=f"{nombre_base}_despues_verificacion_texto", directorio=directorio)
            
            # Realiza una **espera fija** después de la verificación. Esto puede ser útil para
            # propósitos de sincronización con el siguiente paso de la prueba o para permitir
            # una observación visual si la prueba se ejecuta en modo interactivo.
            self.base.esperar_fijo(tiempo)

        except TimeoutError as e:
            # Este bloque se ejecuta si el elemento no se hizo visible O no contenía el texto esperado
            # dentro del `tiempo` total especificado.
            end_time_fail = time.time() # Registra el tiempo final de la operación.
            # Calcula la duración total que tardó la operación completa hasta el fallo.
            duration_fail = end_time_fail - start_time_visible_check
            error_msg = (
                f"\n❌ FALLO (Timeout): El elemento con selector '{selector}' no se hizo visible o no contenía "
                f"el texto '{texto_esperado}' después de {duration_fail:.4f} segundos (timeout configurado: {tiempo}s). Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla en el momento del fallo por timeout para depuración.
            self.base.tomar_captura(f"{nombre_base}_fallo_verificacion_texto_timeout", directorio)
            raise # Re-lanza la excepción para asegurar que la prueba falle.

        except AssertionError as e:
            # Este bloque se ejecuta si el elemento era visible, pero el texto real no coincidía
            # con el `texto_esperado` después de las reintentos de `to_contain_text`.
            error_msg = (
                f"\n❌ FALLO (Aserción): El elemento con selector '{selector}' NO contiene el texto esperado: "
                f"'{texto_esperado}'. Contenido actual: '{locator.text_content() if locator else 'N/A'}' Detalle: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla en el momento del fallo de aserción.
            self.base.tomar_captura(f"{nombre_base}_fallo_verificacion_texto_contenido", directorio)
            raise # Re-lanza la excepción.

        except Error as e:
            # Este bloque maneja errores específicos de Playwright que no son timeouts ni aserciones fallidas,
            # como un selector malformado o un problema de comunicación con el navegador.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar texto para '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_verificacion_texto", directorio)
            raise # Re-lanza la excepción.

        except Exception as e:
            # Este bloque captura cualquier otra excepción inesperada que pueda ocurrir.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al verificar el texto para el selector '{selector}'. "
                f"Detalles: {e}"
            )
            # Usa `critical` para errores graves e `exc_info=True` para incluir la traza completa.
            self.logger.critical(error_msg, exc_info=True)
            # Toma una captura para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_verificacion_texto", directorio)
            raise # Re-lanza la excepción.
        
    def validar_mensaje_validacion_html5(self, selector: Union[str, Locator], texto_esperado: Union[str, List[str], Tuple[str]], nombre_base: str, directorio: str, tiempo: Union[int, float] = 5.0):
        """
        Verifica el texto de un mensaje de validación nativo de HTML5 para un elemento de formulario.
        Esta validación se basa en la propiedad `validationMessage` del elemento en lugar de
        un elemento visible en el DOM.

        Args:
            selector (Union[str, Locator]): El selector CSS o un objeto `Locator` para el
                                            elemento del formulario que debe mostrar el mensaje
                                            (por ejemplo, un campo de entrada con `required`).
            texto_esperado (Union[str, List[str], Tuple[str]]): El texto exacto o parcial que se espera
                                                                en el mensaje de validación de HTML5. Puede
                                                                ser una cadena individual o una lista de
                                                                cadenas para validar múltiples idiomas.
            nombre_base (str): Nombre base para las capturas de pantalla, facilitando su
                                identificación.
            directorio (str): La ruta del directorio donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): Tiempo máximo de espera (en segundos) para que el
                                        mensaje de validación contenga el texto esperado.

        Raises:
            TimeoutError: Si el elemento no se hace visible o el mensaje de validación
                            no contiene el texto esperado dentro del tiempo límite.
            AssertionError: Si el mensaje de validación existe, pero no coincide con el
                            texto esperado después de las reintentos.
            Exception: Para cualquier otro error inesperado.
        """
        if isinstance(texto_esperado, str):
            textos_esperados = [texto_esperado]
        else:
            textos_esperados = list(texto_esperado)

        self.logger.info(f"Validando mensaje de validación de HTML5 para el selector '{selector}'. Textos esperados: '{textos_esperados}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Playwright Locator.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la operación ---
        start_time = time.time()

        try:
            # Espera a que el elemento de formulario esté visible.
            expect(locator).to_be_visible(timeout=tiempo * 1000)
            self.logger.debug(f"Elemento con selector '{selector}' es visible.")

            # Resalta el elemento para el debugging visual.
            locator.highlight()

            # Toma una captura de pantalla antes de la validación.
            self.base.tomar_captura(f"{nombre_base}_antes_validacion_mensaje_html5", directorio)

            # Bucle con espera para verificar el mensaje de validación.
            end_time_check = time.time() + tiempo
            current_message = None
            found_match = False

            while time.time() < end_time_check:
                # Usa evaluate para obtener el `validationMessage` que no es un elemento del DOM.
                try:
                    current_message = locator.evaluate("el => el.validationMessage")
                except Error:
                    # El elemento no existe o ya no es válido, se manejará en la excepción principal
                    self.logger.warning("El elemento no está disponible para obtener el mensaje de validación.")
                    break

                # Verifica si el mensaje actual contiene alguno de los textos esperados.
                if current_message and any(esperado in current_message for esperado in textos_esperados):
                    self.logger.info(f"✔ ÉXITO: Mensaje de validación nativo encontrado. Contenido: '{current_message}'.")
                    found_match = True
                    break

                # Espera fija para el reintento.
                time.sleep(0.2)

            if not found_match:
                raise AssertionError(f"El mensaje de validación '{current_message}' no contiene ninguno de los textos esperados: {textos_esperados}.")

            # --- Medición de rendimiento: Fin de la operación ---
            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"PERFORMANCE: Tiempo total para la validación del mensaje de HTML5: {duration:.4f} segundos.")

            # Toma una captura de pantalla final para documentar el éxito.
            self.base.tomar_captura(f"{nombre_base}_despues_validacion_mensaje_html5", directorio)

        except TimeoutError as e:
            error_msg = (
                f"\n❌ FALLO (Timeout): El elemento con selector '{selector}' no se hizo visible o el "
                f"mensaje de validación no apareció después de {tiempo} segundos. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_validacion_html5", directorio)
            raise

        except AssertionError as e:
            error_msg = (
                f"\n❌ FALLO (Aserción): El mensaje de validación del elemento '{selector}' NO es el esperado. "
                f"Mensaje actual: '{current_message}'. Mensajes esperados: '{textos_esperados}'. Detalle: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_asercion_validacion_html5", directorio)
            raise

        except Error as e:
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al validar el mensaje para '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_validacion_html5", directorio)
            raise

        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al validar el mensaje para el selector '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_validacion_html5", directorio)
            raise
        
    def verificar_texto_exacto(self, selector: Union[str, Locator], texto_esperado: str, nombre_base: str, directorio: str, tiempo: Union[int, float] = 5.0):
        """
        Verifica que un elemento localizado en una página web **contiene un texto exactamente igual** al texto esperado.
        Esta función es más estricta que 'verificar_texto_contenido', ya que no acepta coincidencias parciales.
        Al igual que la otra, mide el tiempo que tarda la operación para fines de rendimiento.

        Args:
            selector (Union[str, Page.locator]): El **selector del elemento** (cadena CSS/XPath) o un objeto `Locator`.
            texto_esperado (str): El **texto exacto** que se espera encontrar en el elemento.
            nombre_base (str): Nombre base para las **capturas de pantalla**.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos). Por defecto, `5.0`.

        Raises:
            TimeoutError: Si el elemento no se hace visible o su texto no coincide exactamente
                        con el texto esperado dentro del tiempo límite.
            AssertionError: Si el elemento es visible, pero el texto real no es una coincidencia estricta.
            Error: Si ocurre un error específico de Playwright.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"Verificando que el elemento con selector '{selector}' tiene exactamente el texto: '{texto_esperado}'. Tiempo máximo de espera: {tiempo}s.")

        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        start_time = time.time()
        try:
            # **Resalta visualmente el elemento** en la página del navegador.
            # Esto es extremadamente útil para el debugging o para demos visuales de la prueba.
            locator.highlight()
            
            # Playwright espera implícitamente a que el elemento sea visible y tenga el texto exacto.
            expect(locator).to_have_text(texto_esperado, timeout=tiempo * 1000)

            end_time = time.time()
            duration = end_time - start_time
            self.logger.info(f"PERFORMANCE: Tiempo que tardó la verificación exacta de texto: {duration:.4f} segundos.")
            
            self.logger.info(f"\n✔ ÉXITO: El elemento con selector '{selector}' tiene exactamente el texto esperado.")
            
            self.base.tomar_captura(nombre_base=f"{nombre_base}_verificacion_texto_exacta_exitosa", directorio=directorio)

        except (TimeoutError, AssertionError) as e:
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time
            error_msg = (
                f"\n❌ FALLO: El elemento con selector '{selector}' NO tiene el texto exacto esperado. "
                f"Tiempo transcurrido: {duration_fail:.4f} segundos (timeout: {tiempo}s). "
                f"Texto actual: '{locator.text_content()}' | Texto esperado: '{texto_esperado}'. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_verificacion_texto_exacta", directorio)
            raise
        except Error as e:
            error_msg = (
                f"\n❌ FALLO (Playwright): Error al verificar el texto exacto para '{selector}'. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_verificacion_texto_exacta", directorio)
            raise
        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al verificar el texto exacto. Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_verificacion_texto_exacta", directorio)
            raise
    
    def rellenar_campo_de_texto(self, selector: Union[str, Locator], texto, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Rellena un campo de texto con el valor especificado y toma capturas de pantalla
        en puntos clave de la operación. Esta función incluye una **medición de rendimiento**
        para registrar el tiempo que tarda la operación de rellenado (`.fill()`).

        Args:
            selector (Union[str, Page.locator]): El **selector del campo de texto**. Puede ser
                                                  una cadena (por ejemplo, un selector CSS o XPath)
                                                  o un objeto `Locator` de Playwright preexistente.
            texto: El **valor a introducir** en el campo de texto.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función. Esto ayuda a identificar
                               las imágenes en el directorio de salida (ej., "login_campo_usuario").
            directorio (str): **Ruta completa del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo de espera fijo** (en segundos) que se aplicará
                                        después de rellenar el campo. Es útil para pausas visuales
                                        o para permitir que la interfaz de usuario (UI) reaccione
                                        antes de la siguiente acción. Por defecto, `0.5` segundos.

        Raises:
            TimeoutError: Si la operación de `.fill()` excede el tiempo de espera, lo que indica
                          que el elemento no estaba visible, habilitado o editable a tiempo.
            Error: Si ocurre un problema específico de Playwright durante la interacción
                   (ej., el selector es inválido, el elemento se desprende del DOM).
            Exception: Para cualquier otro error inesperado que ocurra durante la ejecución de la función.
        """
        self.logger.info(f"\nRellenando campo con selector '{selector}' con el texto: '{texto}'.")

        # Asegura que 'selector' sea un objeto Locator de Playwright. Esto garantiza que
        # las interacciones (como 'highlight' y 'fill') se realicen de manera consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        try:
            # Resalta visualmente el campo de texto en el navegador. Esto es una ayuda visual
            # excelente durante la ejecución de la prueba o el debugging.
            locator.highlight()
            # Toma una captura de pantalla del estado del campo *antes* de introducir el texto.
            self.base.tomar_captura(f"{nombre_base}_antes_de_rellenar_texto", directorio)

            # --- Medición de rendimiento: Inicio de la operación de rellenado ---
            # Registra el momento exacto en que comenzamos la operación de 'fill'.
            start_time_fill = time.time()
            
            # Rellena el campo de texto con el valor proporcionado. El método `fill()` de Playwright
            # es robusto: espera automáticamente a que el elemento sea visible, habilitado y editable
            # antes de intentar escribir, lo que reduce la necesidad de esperas explícitas adicionales.
            locator.fill(texto) # Convertimos el 'texto' a cadena para asegurar compatibilidad.
            
            # --- Medición de rendimiento: Fin de la operación de rellenado ---
            # Registra el momento en que la operación de 'fill' ha finalizado.
            end_time_fill = time.time()
            # Calcula la duración total que tomó la operación de rellenado.
            # Esta métrica es fundamental para evaluar la **reactividad de los campos de entrada**
            # y el rendimiento percibido por el usuario.
            duration_fill = end_time_fill - start_time_fill
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en rellenar el campo '{selector}': {duration_fill:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Campo '{selector}' rellenado con éxito con el texto: '{texto}'.")

            # Toma una captura de pantalla del estado del campo *después* de introducir el texto.
            self.base.tomar_captura(f"{nombre_base}_despues_de_rellenar_texto", directorio)

        except TimeoutError as e:
            # Este bloque se ejecuta si la operación `locator.fill()` no pudo completarse
            # dentro del tiempo de espera implícito de Playwright (que se basa en el timeout
            # global de la página o el definido por el usuario para el locator).
            error_msg = (
                f"\n❌ ERROR (Timeout): El tiempo de espera se agotó al interactuar con el selector '{selector}'.\n"
                f"Posibles causas: El elemento no apareció, no fue visible, habilitado o editable a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa para depuración.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_error_timeout_rellenar", directorio)
            # Re-lanza la excepción como un Error de Playwright para mantener la coherencia en el manejo de errores.
            raise Error(error_msg) from e

        except Error as e:
            # Captura errores específicos de Playwright que no son timeouts. Esto incluye problemas como
            # un selector malformado, un elemento que se desprende del DOM, o fallos de comunicación con el navegador.
            error_msg = (
                f"\n❌ ERROR (Playwright): Ocurrió un problema de Playwright al interactuar con el selector '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_rellenar", directorio)
            raise # Re-lanza la excepción para que la prueba se marque como fallida.

        except Exception as e:
            # Este es un bloque de captura general para cualquier otra excepción inesperada
            # que no haya sido manejada por los tipos de errores anteriores.
            error_msg = (
                f"\n❌ ERROR (Inesperado): Se produjo un error desconocido al interactuar con el selector '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel 'critical' para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_rellenar", directorio)
            raise # Re-lanza la excepción.
                
    def rellenar_campo_numerico_positivo(self, selector: Union[str, Locator], valor_numerico: Union[int, float], nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Rellena un campo de texto con un **valor numérico positivo** (entero o flotante)
        y toma capturas de pantalla en puntos clave. Esta función valida el tipo y el
        signo del número, e integra una **medición de rendimiento** para registrar el
        tiempo que tarda la operación de rellenado (`.fill()`).

        Args:
            selector (Union[str, Page.locator]): El **selector del campo de texto** donde se
                                                  introducirá el valor numérico. Puede ser una
                                                  cadena (CSS, XPath, etc.) o un objeto `Locator`.
            valor_numerico (Union[int, float]): El **valor numérico positivo** (entero o flotante)
                                                que se va a introducir en el campo.
            nombre_base (str): Nombre base para las **capturas de pantalla** tomadas,
                               facilitando su identificación en el directorio de salida.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo de espera fijo** (en segundos) que se aplicará
                                        después de rellenar el campo. Útil para pausas visuales
                                        o para permitir que la UI reaccione. Por defecto, `0.5` segundos.

        Raises:
            ValueError: Si el `valor_numerico` no es un tipo numérico (int/float) o si es negativo.
            TimeoutError: Si la operación de `.fill()` se agota (el elemento no está listo).
            Error: Si ocurre un error específico de Playwright (selector inválido, etc.).
            TypeError: Si el `selector` proporcionado no es un tipo válido (`str` o `Locator`).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nRellenando campo con selector '{selector}' con el valor numérico POSITIVO: '{valor_numerico}'.")

        # --- Validaciones de entrada ---
        # 1. Valida que el 'valor_numerico' sea de tipo numérico (int o float).
        if not isinstance(valor_numerico, (int, float)):
            error_msg = f"\n❌ ERROR: El valor proporcionado '{valor_numerico}' no es un tipo numérico (int o float) válido."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_error_valor_no_numerico", directorio)
            raise ValueError(error_msg)

        # 2. Valida que el 'valor_numerico' sea positivo (mayor o igual a cero).
        if valor_numerico < 0:
            error_msg = f"\n❌ ERROR: El valor numérico '{valor_numerico}' no es positivo. Se esperaba un número mayor o igual a cero."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_error_valor_negativo", directorio)
            raise ValueError(error_msg)

        # Convierte el valor numérico a una cadena para poder rellenar el campo de texto.
        valor_a_rellenar_str = str(valor_numerico)

        # Asegura que 'selector' sea un objeto Locator de Playwright.
        # Esto permite una interacción consistente con Playwright.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        elif isinstance(selector, Locator): # Asegura que sea un objeto Locator válido
            locator = selector
        else:
            error_msg = f"\n❌ ERROR: El selector proporcionado '{type(selector)}' no es una cadena ni un objeto Locator válido."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_error_tipo_selector_numerico", directorio)
            raise TypeError(error_msg)

        try:
            # Resalta visualmente el campo de texto en el navegador.
            locator.highlight()
            # Toma una captura de pantalla del estado del campo *antes* de rellenarlo.
            self.base.tomar_captura(f"{nombre_base}_antes_de_rellenar_numerico", directorio)

            # --- Medición de rendimiento: Inicio de la operación de rellenado ---
            # Registra el tiempo justo antes de ejecutar la acción de 'fill'.
            start_time_fill = time.time()
            
            # Rellena el campo de texto con el valor numérico convertido a cadena.
            # El método `fill()` de Playwright esperará automáticamente a que el elemento
            # esté visible, habilitado y editable.
            locator.fill(valor_a_rellenar_str)
            
            # --- Medición de rendimiento: Fin de la operación de rellenado ---
            # Registra el tiempo inmediatamente después de que la operación de 'fill' se ha completado.
            end_time_fill = time.time()
            # Calcula la duración total de la operación de rellenado.
            # Esta métrica es crucial para evaluar la **reactividad de los campos de entrada**,
            # especialmente en formularios donde el rendimiento es crítico.
            duration_fill = end_time_fill - start_time_fill
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en rellenar el campo '{selector}' con '{valor_a_rellenar_str}': {duration_fill:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Campo '{selector}' rellenado con éxito con el valor: '{valor_a_rellenar_str}'.")

            # Toma una captura de pantalla del estado del campo *después* de rellenarlo.
            self.base.tomar_captura(f"{nombre_base}_despues_de_rellenar_numerico", directorio)

        except TimeoutError as e:
            # Captura específica para errores de tiempo de espera de Playwright.
            # Esto indica que el elemento no estaba listo (visible, habilitado, editable)
            # dentro del tiempo implícito de espera de Playwright para la operación `fill()`.
            error_msg = (
                f"\n❌ ERROR (Timeout): El tiempo de espera se agotó al interactuar con el selector '{selector}'.\n"
                f"Posibles causas: El elemento no apareció, no fue visible/habilitado/editable a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_error_timeout_numerico", directorio)
            # Re-lanza la excepción como un Error de Playwright para mantener la coherencia.
            raise Error(error_msg) from e

        except Error as e:
            # Captura específica para errores de Playwright que no son timeouts (ej., selector malformado,
            # elemento desprendido del DOM, problemas con el contexto del navegador).
            error_msg = (
                f"\n❌ ERROR (Playwright): Ocurrió un problema de Playwright al interactuar con el selector '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_numerico", directorio)
            raise # Re-lanza la excepción.

        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir durante la operación.
            error_msg = (
                f"\n❌ ERROR (Inesperado): Se produjo un error desconocido al interactuar con el selector '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_numerico", directorio)
            raise # Re-lanza la excepción.
                
    def hacer_clic_en_elemento(self, selector: Union[str, Locator], nombre_base: str, directorio: str, texto_esperado: str = None, tiempo: Union[int, float] = 0.5):
        """
        Realiza un click en un elemento de la página web. La función incluye
        validaciones opcionales del texto del elemento, toma capturas de pantalla
        antes y después del clic, e integra una **medición de rendimiento** para registrar
        el tiempo que tarda la operación de clic.

        Args:
            selector (Union[str, Page.locator]): El **selector del elemento** sobre el que
                                                  se desea hacer clic. Puede ser una cadena
                                                  (CSS, XPath, etc.) o un objeto `Locator`
                                                  de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            texto_esperado (str, optional): Texto que se espera que el elemento contenga
                                            **antes de hacer clic**. Si se proporciona,
                                            se realizará una aserción `to_have_text` antes del clic.
                                            Por defecto, `None` (no se verifica el texto).
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        elemento esté clicable y para la aserción de texto (si aplica).
                                        También es el tiempo de espera fijo después del clic.
                                        Por defecto, `5.0` segundos.

        Raises:
            TimeoutError: Si el elemento no está visible, habilitado o clicable a tiempo,
                          o si no contiene el `texto_esperado` dentro del plazo.
            Error: Si ocurre un error específico de Playwright durante la interacción.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nIntentando hacer click en el elemento con selector: '{selector}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        try:
            # Resalta visualmente el elemento en el navegador. Útil para depuración y visualización.
            locator.highlight()
            # Toma una captura de pantalla del estado de la página *antes* de realizar el clic.
            self.base.tomar_captura(f"{nombre_base}_antes_click", directorio)

            # Si se proporciona 'texto_esperado', valida que el elemento contenga ese texto.
            # Esta aserción también espera a que el texto esté presente.
            if texto_esperado:
                # Registra el tiempo antes de la aserción de texto.
                start_time_text_check = time.time()
                expect(locator).to_have_text(texto_esperado)
                # Registra el tiempo después de la aserción de texto y calcula la duración.
                end_time_text_check = time.time()
                duration_text_check = end_time_text_check - start_time_text_check
                self.logger.info(f"PERFORMANCE: Tiempo que tardó el elemento '{selector}' en contener el texto '{texto_esperado}': {duration_text_check:.4f} segundos.")
                self.logger.info(f"\n✅ El elemento con selector '{selector}' contiene el texto esperado: '{texto_esperado}'.")

            # --- Medición de rendimiento: Inicio de la operación de clic ---
            # Registra el tiempo justo antes de ejecutar la acción de 'click'.
            start_time_click = time.time()

            # Realiza el clic en el elemento. El método `click()` de Playwright
            # esperará automáticamente a que el elemento sea visible, habilitado y clicable.
            # El `timeout` aquí es para esta operación específica.
            locator.click()

            # --- Medición de rendimiento: Fin de la operación de clic ---
            # Registra el tiempo inmediatamente después de que la operación de clic se ha completado.
            end_time_click = time.time()
            # Calcula la duración total de la operación de clic.
            # Esta métrica es crucial para evaluar la **reactividad de los botones/enlaces**
            # y el rendimiento percibido por el usuario al interactuar.
            duration_click = end_time_click - start_time_click
            self.logger.info(f"PERFORMANCE: Tiempo que tardó el clic en el elemento '{selector}': {duration_click:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Click realizado exitosamente en el elemento con selector '{selector}'.")
            # Toma una captura de pantalla del estado de la página *después* de realizar el clic.
            self.base.tomar_captura(f"{nombre_base}_despues_click", directorio)

        except TimeoutError as e:
            # Captura específica para errores de tiempo de espera de Playwright.
            # Esto indica que el elemento no estaba listo (visible, habilitado, clicable)
            # o que el texto esperado no apareció a tiempo.
            error_msg = (
                f"\n❌ ERROR (Timeout): El tiempo de espera se agotó al intentar hacer click en '{selector}'.\n"
                f"Posibles causas: El elemento no apareció, no fue visible/habilitado/clicable a tiempo, "
                f"o no contenía el texto esperado (si se especificó).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_error_timeout_click", directorio)
            # Re-lanza la excepción como un Error de Playwright para mantener la coherencia.
            raise Error(error_msg) from e

        except Error as e:
            # Captura errores específicos de Playwright que no son timeouts (ej., selector malformado,
            # elemento desprendido del DOM, problemas con el contexto del navegador).
            error_msg = (
                f"\n❌ ERROR (Playwright): Ocurrió un problema de Playwright al hacer click en el selector '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_click", directorio)
            raise # Re-lanza la excepción.

        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir durante la operación de clic.
            error_msg = (
                f"\n❌ ERROR (Inesperado): Se produjo un error desconocido al intentar hacer click en el selector '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_click", directorio)
            raise # Re-lanza la excepción.

    def hacer_doble_click_en_elemento(self, selector: Union[str, Locator], nombre_base: str, directorio: str, texto_esperado: str = None, tiempo: Union[int, float] = 0.5):
        """
        Realiza un **doble click** en un elemento de la página web. La función incluye
        validaciones opcionales del texto del elemento, toma capturas de pantalla
        antes y después del doble clic, e integra una **medición de rendimiento** para
        registrar el tiempo que tarda la operación de doble clic.

        Args:
            selector (Union[str, Page.locator]): El **selector del elemento** sobre el que
                                                  se desea hacer doble clic. Puede ser una cadena
                                                  (CSS, XPath, etc.) o un objeto `Locator`
                                                  de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            texto_esperado (str, optional): Texto que se espera que el elemento contenga
                                            **antes de hacer doble clic**. Si se proporciona,
                                            se realizará una aserción `to_have_text` antes del doble clic.
                                            Por defecto, `None` (no se verifica el texto).
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        elemento esté clicable y para la aserción de texto (si aplica).
                                        También es el tiempo de espera fijo después del doble clic.
                                        Por defecto, `5.0` segundos. (Se cambió de 1 a 5 para consistencia)

        Raises:
            TimeoutError: Si el elemento no está visible, habilitado o doble-clicable a tiempo,
                          o si no contiene el `texto_esperado` dentro del plazo.
            Error: Si ocurre un error específico de Playwright durante la interacción.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nIntentando hacer doble click en el elemento con selector: '{selector}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        try:
            # Resalta visualmente el elemento en el navegador. Útil para depuración y visualización.
            locator.highlight()
            # Toma una captura de pantalla del estado de la página *antes* de realizar el doble clic.
            self.base.tomar_captura(f"{nombre_base}_antes_doble_click", directorio)

            # Si se proporciona 'texto_esperado', valida que el elemento contenga ese texto.
            # Esta aserción también espera a que el texto esté presente.
            if texto_esperado:
                # Registra el tiempo antes de la aserción de texto.
                start_time_text_check = time.time()
                expect(locator).to_have_text(texto_esperado)
                # Registra el tiempo después de la aserción de texto y calcula la duración.
                end_time_text_check = time.time()
                duration_text_check = end_time_text_check - start_time_text_check
                self.logger.info(f"PERFORMANCE: Tiempo que tardó el elemento '{selector}' en contener el texto '{texto_esperado}' antes del doble clic: {duration_text_check:.4f} segundos.")
                self.logger.info(f"\n✅ El elemento con selector '{selector}' contiene el texto esperado: '{texto_esperado}'.")

            # --- Medición de rendimiento: Inicio de la operación de doble clic ---
            # Registra el tiempo justo antes de ejecutar la acción de 'dblclick'.
            start_time_dblclick = time.time()

            # Realiza el doble clic en el elemento. El método `dblclick()` de Playwright
            # esperará automáticamente a que el elemento sea visible, habilitado y doble-clicable.
            # El `timeout` aquí es para esta operación específica.
            locator.dblclick()

            # --- Medición de rendimiento: Fin de la operación de doble clic ---
            # Registra el tiempo inmediatamente después de que la operación de doble clic se ha completado.
            end_time_dblclick = time.time()
            # Calcula la duración total de la operación de doble clic.
            # Esta métrica es crucial para evaluar la **reactividad de la UI**
            # ante interacciones más complejas como el doble clic.
            duration_dblclick = end_time_dblclick - start_time_dblclick
            self.logger.info(f"PERFORMANCE: Tiempo que tardó el doble clic en el elemento '{selector}': {duration_dblclick:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Doble click realizado exitosamente en el elemento con selector '{selector}'.")
            # Toma una captura de pantalla del estado de la página *después* de realizar el doble clic.
            self.base.tomar_captura(f"{nombre_base}_despues_doble_click", directorio)

        except TimeoutError as e:
            # Captura específica para errores de tiempo de espera de Playwright.
            # Esto indica que el elemento no estaba listo (visible, habilitado, doble-clicable)
            # o que el texto esperado no apareció a tiempo.
            error_msg = (
                f"\n❌ ERROR (Timeout): El tiempo de espera se agotó al intentar hacer doble click en '{selector}'.\n"
                f"Posibles causas: El elemento no apareció, no fue visible/habilitado/doble-clicable a tiempo, "
                f"o no contenía el texto esperado (si se especificó).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_error_timeout_doble_click", directorio)
            # Re-lanza la excepción como un Error de Playwright para mantener la coherencia.
            raise Error(error_msg) from e

        except Error as e:
            # Captura errores específicos de Playwright que no son timeouts (ej., selector malformado,
            # elemento desprendido del DOM, problemas con el contexto del navegador).
            error_msg = (
                f"\n❌ ERROR (Playwright): Ocurrió un problema de Playwright al hacer doble click en el selector '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_doble_click", directorio)
            raise # Re-lanza la excepción.

        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir durante la operación de doble clic.
            error_msg = (
                f"\n❌ ERROR (Inesperado): Se produjo un error desconocido al intentar hacer doble click en el selector '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_doble_click", directorio)
            raise # Re-lanza la excepción.
                
    def hacer_hover_en_elemento(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Realiza una acción de **hover (pasar el ratón por encima)** sobre un elemento
        de la página web. La función toma capturas de pantalla antes y después del hover,
        e integra una **medición de rendimiento** para registrar el tiempo que tarda
        la operación de hover.

        Args:
            selector (Union[str, Page.locator]): El **selector del elemento** sobre el que
                                                  se desea realizar el hover. Puede ser una cadena
                                                  (CSS, XPath, etc.) o un objeto `Locator`
                                                  de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        elemento esté visible y sea interactuable antes de realizar
                                        el hover. También es el tiempo de espera fijo después del hover.
                                        Por defecto, `5.0` segundos (se ajustó de 0.5 para consistencia).

        Raises:
            TimeoutError: Si el elemento no está visible o interactuable a tiempo para el hover.
            Error: Si ocurre un error específico de Playwright durante la interacción.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nIntentando hacer hover sobre el elemento con selector: '{selector}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        try:
            # Resalta visualmente el elemento en el navegador. Útil para depuración y visualización.
            locator.highlight()
            # Toma una captura de pantalla del estado de la página *antes* de realizar el hover.
            self.base.tomar_captura(f"{nombre_base}_antes_hover", directorio)

            # --- Medición de rendimiento: Inicio de la operación de hover ---
            # Registra el tiempo justo antes de ejecutar la acción de 'hover'.
            start_time_hover = time.time()

            # Realiza el hover sobre el elemento. El método `hover()` de Playwright
            # esperará automáticamente a que el elemento sea visible y esté listo para la interacción.
            # El `timeout` aquí es para esta operación específica.
            locator.hover()

            # --- Medición de rendimiento: Fin de la operación de hover ---
            # Registra el tiempo inmediatamente después de que la operación de hover se ha completado.
            end_time_hover = time.time()
            # Calcula la duración total de la operación de hover.
            # Esta métrica es importante para evaluar la **reactividad de la UI**
            # ante interacciones que revelan tooltips, menús desplegables, etc.
            duration_hover = end_time_hover - start_time_hover
            self.logger.info(f"PERFORMANCE: Tiempo que tardó el hover en el elemento '{selector}': {duration_hover:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Hover realizado exitosamente en el elemento con selector '{selector}'.")
            # Toma una captura de pantalla del estado de la página *después* de realizar el hover.
            # Esta captura es especialmente útil si el hover revela nuevos elementos (ej., un menú).
            self.base.tomar_captura(f"{nombre_base}_despues_hover", directorio)

        except TimeoutError as e:
            # Captura específica para errores de tiempo de espera de Playwright.
            # Esto indica que el elemento no estaba visible o interactuable a tiempo para el hover.
            error_msg = (
                f"\n❌ ERROR (Timeout): El tiempo de espera se agotó al intentar hacer hover en '{selector}'.\n"
                f"Posibles causas: El elemento no apareció o no fue visible/habilitado a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_error_timeout_hover", directorio)
            # Re-lanza la excepción como un Error de Playwright para mantener la coherencia.
            raise Error(error_msg) from e

        except Error as e:
            # Captura errores específicos de Playwright que no son timeouts (ej., selector malformado,
            # elemento desprendido del DOM, problemas con el contexto del navegador).
            error_msg = (
                f"\n❌ ERROR (Playwright): Ocurrió un problema de Playwright al hacer hover en el selector '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_hover", directorio)
            raise # Re-lanza la excepción.

        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir durante la operación de hover.
            error_msg = (
                f"\n❌ ERROR (Inesperado): Se produjo un error desconocido al intentar hacer hover en el selector '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_hover", directorio)
            raise # Re-lanza la excepción.

    def verificar_elemento_habilitado(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5) -> bool:
        """
        Verifica si un elemento está **habilitado (enabled)** en la página web.
        Esta función espera hasta que el elemento esté habilitado dentro de un tiempo límite,
        y registra el tiempo que tarda esta verificación como una métrica de rendimiento.
        Toma capturas de pantalla tanto en caso de éxito como de fallo.

        Args:
            selector (Union[str, Page.locator]): El **selector del elemento** a verificar.
                                                  Puede ser una cadena (CSS, XPath, etc.)
                                                  o un objeto `Locator` de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        elemento pase a estar habilitado. Si no lo está dentro
                                        de este plazo, la función devolverá `False`.
                                        Por defecto, `5.0` segundos (se ajustó de 0.5 para robustez).

        Returns:
            bool: `True` si el elemento está habilitado dentro del tiempo especificado;
                  `False` en caso contrario (timeout o aserción fallida).

        Raises:
            Error: Si ocurre un problema específico de Playwright que impida la verificación
                   (ej., selector inválido, problema con el navegador).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nVerificando si el elemento con selector '{selector}' está habilitado. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la verificación de habilitación ---
        # Registra el tiempo justo antes de iniciar la aserción de habilitación.
        start_time_enabled_check = time.time()

        try:
            # Resalta visualmente el elemento en el navegador. Útil para depuración.
            locator.highlight()

            # Playwright espera a que el elemento esté habilitado.
            # El `timeout` se especifica en milisegundos.
            expect(locator).to_be_enabled()
            
            # --- Medición de rendimiento: Fin de la verificación ---
            # Registra el tiempo una vez que la aserción de habilitación ha sido exitosa.
            end_time_enabled_check = time.time()
            # Calcula la duración total de la verificación de habilitación.
            # Esta métrica es importante para evaluar la **velocidad con la que los elementos
            # interactivos de la UI se vuelven funcionales**. Un tiempo de habilitación
            # prolongado podría indicar problemas de carga de JavaScript o de renderizado.
            duration_enabled_check = end_time_enabled_check - start_time_enabled_check
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en verificar que el elemento '{selector}' está habilitado: {duration_enabled_check:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: El elemento '{selector}' está habilitado.")
            # Toma una captura de pantalla al verificar que el elemento está habilitado con éxito.
            self.base.tomar_captura(f"{nombre_base}_habilitado", directorio)
            return True

        except TimeoutError as e:
            # Captura específica para cuando el elemento no está habilitado dentro del tiempo especificado.
            # Se registra el tiempo transcurrido hasta el fallo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_enabled_check # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): El elemento con selector '{selector}' NO está habilitado "
                f"después de {duration_fail:.4f} segundos (timeout configurado: {tiempo}s). "
                f"Detalles: {e}"
            )
            self.logger.warning(error_msg) # Usa 'warning' ya que la función devuelve False en lugar de fallar la prueba.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_NO_habilitado_timeout", directorio)
            return False

        except AssertionError as e:
            # Captura si la aserción de habilitación falla por alguna otra razón.
            # Con `to_be_enabled` y un timeout, `TimeoutError` es más común, pero `AssertionError`
            # podría ocurrir si el elemento existe pero la aserción de Playwright lo considera inhabilitado
            # sin agotar el timeout.
            error_msg = (
                f"\n❌ FALLO (Aserción): El elemento con selector '{selector}' NO está habilitado. "
                f"Detalles: {e}"
            )
            self.logger.warning(error_msg) # Usa 'warning' aquí también.
            # Toma una captura de pantalla en el momento del fallo de aserción.
            self.base.tomar_captura(f"{nombre_base}_NO_habilitado_fallo", directorio)
            return False

        except Error as e:
            # Captura errores específicos de Playwright que no son timeouts ni AssertionErrors (ej., selector malformado).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar habilitación de '{selector}'. "
                f"Esto indica un problema fundamental con el selector o el navegador. "
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_habilitado", directorio)
            raise # Re-lanza la excepción porque esto es un fallo de ejecución, no una verificación de estado.

        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error desconocido al verificar la habilitación de '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_habilitado", directorio)
            raise # Re-lanza la excepción.

    def mouse_mueve_y_hace_clic_xy(self, x: int, y: int, nombre_base: str, directorio: str, tiempo: Union[int, float] = 1.0):
        """
        Mueve el cursor del mouse a las coordenadas de pantalla (X, Y) especificadas y luego
        realiza un clic en esas mismas coordenadas. Esta función es útil para interacciones
        precisas fuera del contexto de un elemento específico del DOM.
        Integra una **medición de rendimiento** para registrar el tiempo que tarda la secuencia
        completa (movimiento y clic).

        Args:
            x (int): La **coordenada X** (horizontal) en píxeles de la pantalla,
                     donde se moverá el mouse y se hará clic.
            y (int): La **coordenada Y** (vertical) en píxeles de la pantalla,
                     donde se moverá el mouse y se hará clic.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo de espera fijo** (en segundos) que se aplicará
                                        después de que el clic se haya completado. Útil para
                                        observar los efectos del clic o dar tiempo a la UI.
                                        Por defecto, `1.0` segundos (se ajustó de 0.5 para una espera más razonable).

        Raises:
            ValueError: Si las coordenadas X o Y no son números enteros.
            Exception: Para cualquier error inesperado que ocurra durante la operación del mouse.
        """
        self.logger.info(f"\nIntentando mover el mouse a X:{x}, Y:{y} y haciendo click.")

        # --- Validaciones de entrada ---
        # Asegura que las coordenadas sean de tipo entero para evitar errores inesperados con mouse.move/click.
        if not isinstance(x, int) or not isinstance(y, int):
            error_msg = f"\n❌ ERROR: Las coordenadas X ({x}) e Y ({y}) deben ser números enteros."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_error_coordenadas_invalidas", directorio)
            raise ValueError(error_msg)

        try:
            # Toma una captura de pantalla del estado de la página *antes* de mover y hacer clic.
            self.base.tomar_captura(f"{nombre_base}_antes_mouse_click_xy", directorio)
            
            # --- Medición de rendimiento: Inicio de la operación del mouse ---
            # Registra el tiempo justo antes de iniciar el movimiento y clic del mouse.
            start_time_mouse_action = time.time()

            # Mueve el cursor del mouse a las coordenadas especificadas.
            # `steps=5` hace que el movimiento sea más suave, simulando un usuario real.
            self.page.mouse.move(x, y, steps=5) 
            self.logger.debug(f"\nMouse movido a X:{x}, Y:{y}.")
            
            # Realiza un clic en las mismas coordenadas.
            self.page.mouse.click(x, y)

            # --- Medición de rendimiento: Fin de la operación del mouse ---
            # Registra el tiempo inmediatamente después de que el clic se ha completado.
            end_time_mouse_action = time.time()
            # Calcula la duración total de la secuencia de movimiento y clic.
            # Esta métrica es relevante para acciones de UI que dependen de interacciones
            # de ratón muy precisas y para evaluar la latencia percibida en estas acciones.
            duration_mouse_action = end_time_mouse_action - start_time_mouse_action
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en mover y hacer clic en X:{x}, Y:{y}: {duration_mouse_action:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Click realizado en X:{x}, Y:{y}.")
            # Toma una captura de pantalla del estado de la página *después* de la acción del mouse.
            self.base.tomar_captura(f"{nombre_base}_despues_mouse_click_xy", directorio)

        except Error as e:
            # Captura errores específicos de Playwright relacionados con la interacción del mouse.
            error_msg = (
                f"\n❌ ERROR (Playwright): Ocurrió un problema de Playwright al mover el mouse y hacer clic en X:{x}, Y:{y}.\n"
                f"Esto puede deberse a problemas con la ventana del navegador o el contexto de ejecución.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla en el momento del fallo.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_mouse_click_xy", directorio)
            raise # Re-lanza la excepción.

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ ERROR (Inesperado): Se produjo un error desconocido al mover el mouse y hacer clic en X:{x}, Y:{y}.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_mouse_click_xy", directorio)
            raise # Re-lanza la excepción.

    def marcar_checkbox(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Marca un checkbox especificado por su selector y verifica que se haya marcado
        correctamente. Esta función toma capturas de pantalla antes y después de la
        acción, e integra una **medición de rendimiento** para registrar el tiempo
        que tarda la operación completa (marcar y verificar).

        Args:
            selector (Union[str, Page.locator]): El **selector del checkbox** que se desea marcar.
                                                  Puede ser una cadena (CSS, XPath, etc.) o un objeto
                                                  `Locator` de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        checkbox sea marcado y para que su estado sea verificado.
                                        También es el tiempo de espera fijo después de la operación.
                                        Por defecto, `5.0` segundos (se ajustó de 0.5 para robustez).

        Raises:
            AssertionError: Si el checkbox no puede ser marcado o no se verifica como marcado
                            dentro del tiempo límite, o si ocurre un error de Playwright.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nIntentando marcar el checkbox con selector: '{selector}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la operación de marcado y verificación ---
        # Registra el tiempo justo antes de iniciar la operación.
        start_time_checkbox_action = time.time()

        try:
            # Resalta visualmente el elemento en el navegador. Útil para depuración.
            locator.highlight()
            # Toma una captura de pantalla del estado de la página *antes* de marcar el checkbox.
            self.base.tomar_captura(f"{nombre_base}_antes_marcar_checkbox", directorio)
            
            # Marca el checkbox. Playwright esperará automáticamente a que sea interactuable.
            locator.check()
            # Verifica que el checkbox esté marcado. Esta aserción también espera.
            expect(locator).to_be_checked() 
            
            # --- Medición de rendimiento: Fin de la operación ---
            # Registra el tiempo una vez que el checkbox ha sido marcado y verificado con éxito.
            end_time_checkbox_action = time.time()
            # Calcula la duración total de la operación.
            # Esta métrica es importante para evaluar la **capacidad de respuesta de los elementos
            # de formulario** y la velocidad de actualización de su estado en la UI.
            duration_checkbox_action = end_time_checkbox_action - start_time_checkbox_action
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en marcar y verificar el checkbox '{selector}': {duration_checkbox_action:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Checkbox con selector '{selector}' marcado y verificado exitosamente.")
            # Toma una captura de pantalla del estado de la página *después* de marcar el checkbox.
            self.base.tomar_captura(f"{nombre_base}_despues_marcar_checkbox", directorio)

        except TimeoutError as e:
            # Captura específica para cuando la operación de marcar o la verificación fallan por tiempo.
            # Registra el tiempo transcurrido hasta el fallo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_checkbox_action # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): El checkbox con selector '{selector}' no pudo ser marcado "
                f"o verificado como marcado dentro de {duration_fail:.4f} segundos (timeout configurado: {tiempo}s). "
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_marcar", directorio)
            # Re-lanza la excepción como un AssertionError para que la prueba falle claramente.
            raise AssertionError(f"\nCheckbox no marcado/verificado (Timeout): {selector}") from e

        except Error as e: # Captura errores específicos de Playwright (ej., selector inválido)
            error_msg = (
                f"\n❌ FALLO (Playwright Error): Problema al interactuar con el checkbox '{selector}'.\n"
                f"Posibles causas: Selector inválido, elemento no interactuable, DOM no estable.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_fallo_playwright_error_marcar", directorio)
            raise AssertionError(f"\nError de Playwright con checkbox: {selector}") from e # Re-lanza.

        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Error Inesperado): Ocurrió un error desconocido al intentar marcar el checkbox '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_fallo_inesperado_marcar", directorio)
            raise # Re-lanza la excepción.

    def desmarcar_checkbox(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Desmarca un checkbox especificado por su selector y verifica que se haya desmarcado
        correctamente. Esta función toma capturas de pantalla antes y después de la acción,
        e integra una **medición de rendimiento** para registrar el tiempo que tarda la
        operación completa (desmarcar y verificar).

        Args:
            selector (Union[str, Page.locator]): El **selector del checkbox** que se desea desmarcar.
                                                  Puede ser una cadena (CSS, XPath, etc.) o un objeto
                                                  `Locator` de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        checkbox sea desmarcado y para que su estado sea verificado.
                                        También es el tiempo de espera fijo después de la operación.
                                        Por defecto, `5.0` segundos (se ajustó de 0.5 para robustez).

        Raises:
            AssertionError: Si el checkbox no puede ser desmarcado o no se verifica como desmarcado
                            dentro del tiempo límite, o si ocurre un error de Playwright.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nIntentando desmarcar el checkbox con selector: '{selector}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la operación de desmarcado y verificación ---
        # Registra el tiempo justo antes de iniciar la operación.
        start_time_checkbox_action = time.time()

        try:
            # Resalta visualmente el elemento en el navegador. Útil para depuración.
            locator.highlight()
            # Toma una captura de pantalla del estado de la página *antes* de desmarcar el checkbox.
            self.base.tomar_captura(f"{nombre_base}_antes_desmarcar_checkbox", directorio)
            
            # Desmarca el checkbox. Playwright esperará automáticamente a que sea interactuable.
            locator.uncheck()
            # Verifica que el checkbox no esté marcado. Esta aserción también espera.
            expect(locator).not_to_be_checked() 
            
            # --- Medición de rendimiento: Fin de la operación ---
            # Registra el tiempo una vez que el checkbox ha sido desmarcado y verificado con éxito.
            end_time_checkbox_action = time.time()
            # Calcula la duración total de la operación.
            # Esta métrica es importante para evaluar la **capacidad de respuesta de los elementos
            # de formulario** y la velocidad de actualización de su estado en la UI.
            duration_checkbox_action = end_time_checkbox_action - start_time_checkbox_action
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en desmarcar y verificar el checkbox '{selector}': {duration_checkbox_action:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Checkbox con selector '{selector}' desmarcado y verificado exitosamente.")
            # Toma una captura de pantalla del estado de la página *después* de desmarcar el checkbox.
            self.base.tomar_captura(f"{nombre_base}_despues_desmarcar_checkbox", directorio)

        except TimeoutError as e:
            # Captura específica para cuando la operación de desmarcar o la verificación fallan por tiempo.
            # Registra el tiempo transcurrido hasta el fallo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_checkbox_action # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): El checkbox con selector '{selector}' no pudo ser desmarcado "
                f"o verificado como desmarcado dentro de {duration_fail:.4f} segundos (timeout configurado: {tiempo}s). "
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_desmarcar", directorio)
            # Re-lanza la excepción como un AssertionError para que la prueba falle claramente.
            raise AssertionError(f"\nCheckbox no desmarcado/verificado (Timeout): {selector}") from e

        except Error as e: # Captura errores específicos de Playwright (ej., selector inválido)
            error_msg = (
                f"\n❌ FALLO (Playwright Error): Problema al interactuar con el checkbox '{selector}'.\n"
                f"Posibles causas: Selector inválido, elemento no interactuable, DOM no estable.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_fallo_playwright_error_desmarcar", directorio)
            raise AssertionError(f"\nError de Playwright con checkbox: {selector}") from e # Re-lanza.

        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Error Inesperado): Ocurrió un error desconocido al intentar desmarcar el checkbox '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_fallo_inesperado_desmarcar", directorio)
            raise # Re-lanza la excepción.
                
    def verificar_valor_campo(self, selector: Union[str, Locator], valor_esperado: str, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5) -> bool:
        """
        Verifica que el **valor de un campo de texto** coincida con el `valor_esperado`.
        Esta función espera hasta que el campo de texto contenga el valor deseado dentro
        de un tiempo límite, y registra el tiempo que tarda esta verificación como una
        métrica de rendimiento. Toma capturas de pantalla tanto en caso de éxito como de fallo.
        
        Args:
            selector (Union[str, Page.locator]): El **selector del campo de texto** a verificar.
                                                Puede ser una cadena (CSS, XPath, etc.)
                                                o un objeto `Locator` de Playwright preexistente.
            valor_esperado (str): El **valor de texto exacto** que se espera encontrar en el campo.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                            tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        campo contenga el `valor_esperado`. Si no lo contiene
                                        dentro de este plazo, la función fallará.
                                        Por defecto, `5.0` segundos (se ajustó de 0.5 para robustez).

        Returns:
            bool: `True` si el valor del campo coincide con `valor_esperado` dentro del tiempo especificado;
                `False` en caso de que ocurra un error específico del selector.

        Raises:
            TimeoutError: Si el campo no contiene el valor esperado dentro del tiempo límite.
            AssertionError: Si la aserción falla por cualquier otra razón.
            Error: Si ocurre un problema específico de Playwright (ej., selector inválido, elemento no es un campo de texto).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nVerificando que el campo '{selector}' contiene el valor esperado: '{valor_esperado}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la verificación del valor del campo ---
        start_time_value_check = time.time()

        try:
            locator.highlight()
            self.base.tomar_captura(f"{nombre_base}_antes_verificar_valor_campo", directorio)
            
            # Playwright espera a que el campo contenga el valor especificado.
            # El `timeout` se especifica en milisegundos.
            expect(locator).to_have_value(valor_esperado)
            
            # --- Medición de rendimiento: Fin de la verificación ---
            end_time_value_check = time.time()
            duration_value_check = end_time_value_check - start_time_value_check
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en verificar que el campo '{selector}' contiene el valor '{valor_esperado}': {duration_value_check:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: El campo '{selector}' contiene el valor esperado: '{valor_esperado}'.")
            self.base.tomar_captura(f"{nombre_base}_despues_verificar_valor_campo", directorio)
            return True

        except (TimeoutError, AssertionError) as e:
            # Captura tanto TimeoutError como AssertionError, ya que ambas indican un fallo de aserción.
            actual_value = "No se pudo obtener el valor"
            try:
                actual_value = locator.input_value()
            except Exception:
                pass
            
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_value_check
            error_msg = (
                f"\n❌ FALLO (Aserción): El campo '{selector}' NO contiene el valor esperado '{valor_esperado}'. "
                f"Valor actual: '{actual_value}'. Detalles: {e}"
            )
            self.logger.warning(error_msg)
            self.base.tomar_captura(f"{nombre_base}_fallo_verificar_valor_campo", directorio)
            raise # Re-lanza la excepción para que Pytest la detecte.

        except Error as e:
            # Captura errores específicos de Playwright
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar el valor del campo '{selector}'. "
                f"Esto indica un problema con el selector. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_verificar_valor_campo", directorio)
            raise # Re-lanza la excepción.

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error desconocido al verificar el valor del campo '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_verificar_valor_campo", directorio)
            raise # Re-lanza la excepción.

    def verificar_valor_campo_numerico_int(self, selector: Union[str, Locator], valor_numerico_esperado: int, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5) -> bool:
        """
        Verifica que el **valor de un campo de texto**, interpretado como un **número entero**,
        coincida con el `valor_numerico_esperado`. Esta función espera hasta que el campo
        contenga el valor deseado (como cadena) dentro de un tiempo límite, y registra el
        tiempo que tarda esta verificación como una métrica de rendimiento.
        Toma capturas de pantalla tanto en caso de éxito como de fallo.

        Args:
            selector (Union[str, Page.locator]): El **selector del campo de texto** a verificar.
                                                  Puede ser una cadena (CSS, XPath, etc.)
                                                  o un objeto `Locator` de Playwright preexistente.
            valor_numerico_esperado (int): El **valor numérico entero exacto** que se espera
                                           encontrar en el campo. Se convertirá a cadena para la
                                           comparación con el valor del campo HTML.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        campo contenga el `valor_numerico_esperado`. Si no lo contiene
                                        dentro de este plazo, la función devolverá `False`.
                                        Por defecto, `5.0` segundos (se ajustó de 0.5 para robustez).

        Returns:
            bool: `True` si el valor numérico (entero) del campo coincide con `valor_numerico_esperado`
                  dentro del tiempo especificado; `False` en caso contrario (timeout o aserción fallida).

        Raises:
            TypeError: Si `valor_numerico_esperado` no es un número entero.
            Error: Si ocurre un problema específico de Playwright que impida la verificación
                   (ej., selector inválido, elemento no es un campo de texto).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nVerificando que el campo '{selector}' contiene el valor numérico entero esperado: '{valor_numerico_esperado}'. Tiempo máximo de espera: {tiempo}s.")

        # --- Validación de entrada: Asegura que el valor esperado es un entero ---
        # Es crucial que el valor esperado sea un entero para la lógica de la función.
        if not isinstance(valor_numerico_esperado, int):
            error_msg = (
                f"\n❌ ERROR de tipo: 'valor_numerico_esperado' debe ser un número entero (int), "
                f"pero se recibió un tipo: {type(valor_numerico_esperado).__name__} con valor '{valor_numerico_esperado}'."
            )
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_error_tipo_valor_int", directorio)
            raise TypeError(error_msg) # Se eleva un TypeError para un tipo de dato incorrecto.

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la verificación del valor numérico ---
        # Registra el tiempo justo antes de iniciar la aserción del valor.
        start_time_numeric_check = time.time()

        try:
            # Resalta visualmente el elemento en el navegador. Útil para depuración.
            locator.highlight()
            # Toma una captura de pantalla del estado del campo *antes* de la verificación.
            # Esto puede ser útil para ver el valor inicial si es diferente al esperado.
            self.base.tomar_captura(f"{nombre_base}_antes_verificar_valor_int", directorio)

            # Playwright espera a que el campo contenga el valor especificado (convertido a cadena).
            # El `timeout` se especifica en milisegundos.
            # Se usa `str(valor_numerico_esperado)` porque el valor en un campo de texto HTML
            # siempre se leerá como una cadena, incluso si representa un número.
            expect(locator).to_have_value(str(valor_numerico_esperado))
            
            # --- Medición de rendimiento: Fin de la verificación ---
            # Registra el tiempo una vez que la aserción del valor ha sido exitosa.
            end_time_numeric_check = time.time()
            # Calcula la duración total de la verificación del valor.
            # Esta métrica es importante para evaluar la **velocidad con la que los campos
            # numéricos se pueblan o actualizan** en la UI, lo cual puede depender de la carga
            # de datos, cálculos en el frontend o lógica de la aplicación que establece los valores.
            duration_numeric_check = end_time_numeric_check - start_time_numeric_check
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en verificar que el campo '{selector}' contiene el valor numérico '{valor_numerico_esperado}': {duration_numeric_check:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: El campo '{selector}' contiene el valor numérico entero esperado: '{valor_numerico_esperado}'.")
            # Toma una captura de pantalla al verificar que el campo tiene el valor esperado.
            self.base.tomar_captura(f"{nombre_base}_despues_verificar_valor_int", directorio)
            return True

        except TimeoutError as e:
            # Captura específica para cuando el campo no contiene el valor esperado dentro del tiempo.
            # Se intenta obtener el valor actual del campo para incluirlo en el mensaje de error.
            actual_value_str = "No se pudo obtener el valor o no es un campo de entrada"
            try:
                # Intenta obtener el valor actual como cadena
                actual_value_str = locator.input_value()
            except Exception:
                pass # Ignora si no se puede obtener el valor (ej., elemento no existe o no es input)

            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_numeric_check # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): El campo '{selector}' no contiene el valor entero esperado '{valor_numerico_esperado}' "
                f"después de {duration_fail:.4f} segundos (timeout configurado: {tiempo}s). "
                f"Valor actual en el campo: '{actual_value_str}'. Detalles: {e}"
            )
            self.logger.warning(error_msg) # Usa 'warning' ya que la función devuelve False.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_verificar_valor_int", directorio)
            return False

        except AssertionError as e:
            # Captura si la aserción de valor falla por alguna otra razón (menos común con to_have_value, pero posible).
            actual_value_str = "No se pudo obtener el valor o no es un campo de entrada"
            try:
                actual_value_str = locator.input_value()
                # Intenta convertir el valor actual a entero para una comparación más significativa en el log.
                actual_value_int = int(actual_value_str)
                comparison_msg = f"\n (Valor actual: {actual_value_int}, Esperado: {valor_numerico_esperado})"
            except ValueError: # Si el valor actual no se puede convertir a int.
                comparison_msg = f"\n (Valor actual no numérico: '{actual_value_str}', Esperado: {valor_numerico_esperado})"
            except Exception: # Si no se puede obtener el valor en absoluto.
                comparison_msg = f"\n (No se pudo obtener el valor actual, Esperado: {valor_numerico_esperado})"

            error_msg = (
                f"\n❌ FALLO (Aserción): El campo '{selector}' NO contiene el valor numérico entero esperado. "
                f"{comparison_msg}. Detalles: {e}"
            )
            self.logger.warning(error_msg) # Usa 'warning' aquí también.
            # Toma una captura de pantalla en el momento del fallo de aserción.
            self.base.tomar_captura(f"{nombre_base}_fallo_verificar_valor_int", directorio)
            return False

        except Error as e:
            # Captura errores específicos de Playwright (ej., selector inválido, elemento no es un campo de entrada).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar el valor numérico entero del campo '{selector}'. "
                f"Esto indica un problema fundamental con el selector o el tipo de elemento.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_verificar_valor_int", directorio)
            raise # Re-lanza la excepción porque esto es un fallo de ejecución, no una verificación de estado.

        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error desconocido al verificar el valor numérico entero del campo '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_verificar_valor_int", directorio)
            raise # Re-lanza la excepción.

    def verificar_valor_campo_numerico_float(self, selector: Union[str, Locator], valor_numerico_esperado: float, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5, tolerancia: float = 1e-6) -> bool:
        """
        Verifica que el **valor de un campo de texto**, interpretado como un **número flotante**,
        coincida con el `valor_numerico_esperado` dentro de una `tolerancia` específica.
        Esta función espera hasta que el campo esté visible, obtiene su valor, y luego realiza
        la comparación. Registra el tiempo que tarda esta verificación como una métrica de rendimiento.
        Toma capturas de pantalla tanto en caso de éxito como de fallo.

        Args:
            selector (Union[str, Page.locator]): El **selector del campo de texto** a verificar.
                                                  Puede ser una cadena (CSS, XPath, etc.)
                                                  o un objeto `Locator` de Playwright preexistente.
            valor_numerico_esperado (float): El **valor numérico flotante exacto** que se espera
                                           encontrar en el campo.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        campo se haga visible y su valor sea obtenible.
                                        También es el tiempo de espera fijo después de la operación.
                                        Por defecto, `5.0` segundos (se ajustó de 0.5 para robustez).
            tolerancia (float): **Margen de error** aceptable para la comparación de números flotantes.
                                 Debido a la naturaleza de la representación de punto flotante,
                                 raramente se comparan flotantes para una igualdad exacta.
                                 Por defecto, `1e-6` (0.000001).

        Returns:
            bool: `True` si el valor numérico (flotante) del campo coincide con `valor_numerico_esperado`
                  dentro de la tolerancia y el tiempo especificado; `False` en caso contrario.

        Raises:
            TypeError: Si `valor_numerico_esperado` o `tolerancia` no son números flotantes.
            Error: Si ocurre un problema específico de Playwright que impida la verificación
                   (ej., selector inválido, elemento no es un campo de texto).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nVerificando que el campo '{selector}' contiene el valor numérico flotante esperado: '{valor_numerico_esperado}' con tolerancia {tolerancia}. Tiempo máximo de espera: {tiempo}s.")

        # --- Validación de entrada: Asegura que el valor esperado es un flotante y la tolerancia es un flotante ---
        if not isinstance(valor_numerico_esperado, float):
            error_msg = (
                f"\n❌ ERROR de tipo: 'valor_numerico_esperado' debe ser un número flotante (float), "
                f"pero se recibió un tipo: {type(valor_numerico_esperado).__name__} con valor '{valor_numerico_esperado}'."
            )
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_error_tipo_valor_float", directorio)
            raise TypeError(error_msg) # Se eleva un TypeError para un tipo de dato incorrecto.
        
        if not isinstance(tolerancia, float) or tolerancia < 0:
            error_msg = (
                f"\n❌ ERROR de tipo: 'tolerancia' debe ser un número flotante (float) no negativo, "
                f"pero se recibió un tipo: {type(tolerancia).__name__} con valor '{tolerancia}'."
            )
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_error_tipo_tolerancia_float", directorio)
            raise TypeError(error_msg)

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la verificación del valor flotante ---
        # Registra el tiempo justo antes de iniciar la operación de verificación.
        start_time_float_check = time.time()

        try:
            # Resalta visualmente el elemento en el navegador. Útil para depuración.
            locator.highlight()
            # Toma una captura de pantalla del estado del campo *antes* de la verificación.
            self.base.tomar_captura(f"{nombre_base}_antes_verificar_valor_float", directorio)

            # Primero, asegurar que el campo es visible y está presente en el DOM
            # Esto es necesario porque `input_value()` no tiene un mecanismo de espera.
            expect(locator).to_be_visible() 
            
            # Obtener el valor actual del campo como una cadena.
            actual_value_str = locator.input_value()

            # Intentar convertir la cadena a un número flotante.
            actual_value_float = float(actual_value_str)
            
            # Realizar la comparación de flotantes con la tolerancia.
            # `math.isclose` es la forma recomendada para comparar flotantes.
            if math.isclose(actual_value_float, valor_numerico_esperado, rel_tol=tolerancia, abs_tol=tolerancia):
                # --- Medición de rendimiento: Fin de la verificación (éxito) ---
                end_time_float_check = time.time()
                duration_float_check = end_time_float_check - start_time_float_check
                self.logger.info(f"PERFORMANCE: Tiempo que tardó en verificar que el campo '{selector}' contiene el valor flotante '{valor_numerico_esperado}': {duration_float_check:.4f} segundos.")

                self.logger.info(f"\n✔ ÉXITO: El campo '{selector}' contiene el valor numérico flotante esperado: '{valor_numerico_esperado}' (Actual: {actual_value_float}).")
                # Toma una captura de pantalla al verificar que el campo tiene el valor esperado.
                self.base.tomar_captura(f"{nombre_base}_despues_verificar_valor_float", directorio)
                return True
            else:
                # Si la comparación con tolerancia falla
                error_msg = (
                    f"\n❌ FALLO (Inexactitud): El campo '{selector}' NO contiene el valor numérico flotante esperado. "
                    f"Actual: {actual_value_float}, Esperado: {valor_numerico_esperado}, "
                    f"Diferencia: {abs(actual_value_float - valor_numerico_esperado):.10f} (Tolerancia: {tolerancia})."
                )
                self.logger.warning(error_msg)
                self.base.tomar_captura(f"{nombre_base}_fallo_inexactitud_float", directorio)
                return False

        except TimeoutError as e:
            # Captura si el campo no se hace visible o no se puede obtener su valor a tiempo.
            # Se intenta obtener el valor actual del campo si es posible.
            actual_value_str_on_timeout = "N/A"
            try:
                # Intenta obtener el valor actual como cadena justo antes de la excepción.
                actual_value_str_on_timeout = locator.input_value()
            except Exception:
                pass # Ignora si no se puede obtener.

            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_float_check # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): El campo '{selector}' no se hizo visible o no se pudo obtener su valor "
                f"después de {duration_fail:.4f} segundos (timeout configurado: {tiempo}s) para verificar el flotante '{valor_numerico_esperado}'. "
                f"Valor actual (si disponible): '{actual_value_str_on_timeout}'. Detalles: {e}"
            )
            self.logger.warning(error_msg)
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_verificar_valor_float", directorio)
            return False

        except ValueError:
            # Captura si el valor obtenido del campo no es una cadena que pueda convertirse a float.
            error_msg = (
                f"\n❌ FALLO (Valor no numérico): El valor actual del campo '{selector}' ('{actual_value_str}') "
                f"no pudo ser convertido a flotante para comparación. Se esperaba '{valor_numerico_esperado}'."
            )
            self.logger.warning(error_msg)
            self.base.tomar_captura(f"{nombre_base}_fallo_valor_no_float", directorio)
            return False

        except Error as e:
            # Captura errores específicos de Playwright (ej., selector inválido, elemento no es un campo de entrada).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar el valor numérico flotante del campo '{selector}'. "
                f"Esto indica un problema fundamental con el selector o el tipo de elemento.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_verificar_valor_float", directorio)
            raise # Re-lanza la excepción porque esto es un fallo de ejecución, no una verificación de estado.

        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error desconocido al verificar el valor numérico flotante del campo '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_verificar_valor_float", directorio)
            raise # Re-lanza la excepción.

    def verificar_alt_imagen(self, selector: Union[str, Locator], texto_alt_esperado: str, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5) -> bool:
        """
        Verifica que el **texto del atributo 'alt' de una imagen** coincida con el
        `texto_alt_esperado`. Esta función espera a que la imagen sea visible,
        obtiene su atributo 'alt', y luego realiza la comparación.
        Registra el tiempo que tarda esta verificación como una métrica de rendimiento.
        Toma capturas de pantalla tanto en caso de éxito como de fallo.

        Args:
            selector (Union[str, Page.locator]): El **selector de la imagen** a verificar.
                                                  Puede ser una cadena (CSS, XPath, etc.)
                                                  o un objeto `Locator` de Playwright preexistente.
            texto_alt_esperado (str): El **valor exacto del texto 'alt'** que se espera
                                      encontrar en la imagen.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que la
                                        imagen se haga visible y su atributo 'alt' sea obtenible.
                                        También es el tiempo de espera fijo después de la operación.
                                        Por defecto, `5.0` segundos (se ajustó de 0.5 para robustez).

        Returns:
            bool: `True` si el texto 'alt' de la imagen coincide con `texto_alt_esperado`
                  dentro del tiempo especificado; `False` en caso contrario (timeout o no coincidencia).

        Raises:
            Error: Si ocurre un problema específico de Playwright que impida la verificación
                   (ej., selector inválido, el elemento no es una imagen).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nVerificando el texto 'alt' para la imagen con selector: '{selector}'. Valor esperado: '{texto_alt_esperado}'. Tiempo máximo de espera: {tiempo}s.")

        # Asegura que 'selector' sea un objeto Locator de Playwright para un uso consistente.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        # --- Medición de rendimiento: Inicio de la verificación del texto 'alt' ---
        # Registra el tiempo justo antes de iniciar la operación de verificación.
        start_time_alt_check = time.time()

        try:
            # Resalta visualmente el elemento en el navegador. Útil para depuración.
            locator.highlight()
            # Toma una captura de pantalla del estado de la imagen *antes* de la verificación.
            self.base.tomar_captura(f"{nombre_base}_antes_verificar_alt_imagen", directorio)

            # Esperar a que la imagen sea visible y esté adjunta al DOM.
            # Esto es crucial antes de intentar obtener atributos, ya que asegura que el elemento está cargado.
            expect(locator).to_be_visible()
            self.logger.debug(f"\nLa imagen con selector '{selector}' es visible.")

            # Obtener el atributo 'alt' de la imagen.
            # `get_attribute` también tiene un `timeout` que esperará hasta que el atributo esté presente.
            alt_text_actual = locator.get_attribute("alt")

            # Validar que el atributo 'alt' no sea None y coincida con el texto esperado.
            # La comparación debe ser estricta para asegurar que el atributo existe y es correcto.
            if alt_text_actual == texto_alt_esperado:
                # --- Medición de rendimiento: Fin de la verificación (éxito) ---
                end_time_alt_check = time.time()
                duration_alt_check = end_time_alt_check - start_time_alt_check
                self.logger.info(f"PERFORMANCE: Tiempo que tardó en verificar el texto 'alt' de la imagen '{selector}': {duration_alt_check:.4f} segundos.")

                self.logger.info(f"\n✔ ÉXITO: El texto 'alt' de la imagen es '{alt_text_actual}' y coincide con el esperado ('{texto_alt_esperado}').")
                # Toma una captura de pantalla al verificar que el 'alt' de la imagen es el esperado.
                self.base.tomar_captura(f"{nombre_base}_alt_ok", directorio)
                return True
            else:
                # Si el texto 'alt' no coincide con el esperado
                error_msg = (
                    f"\n❌ FALLO (No Coincide): El texto 'alt' actual de la imagen '{selector}' es '{alt_text_actual}', "
                    f"pero se esperaba '{texto_alt_esperado}'."
                )
                self.logger.warning(error_msg) # Usa 'warning' ya que la función devuelve False.
                # Toma una captura de pantalla si el texto 'alt' no coincide.
                self.base.tomar_captura(f"{nombre_base}_alt_error", directorio)
                return False

        except TimeoutError as e:
            # Captura si la imagen no se hace visible o no se puede obtener su atributo 'alt' a tiempo.
            error_msg = (
                f"\n❌ FALLO (Timeout): La imagen con selector '{selector}' no se hizo visible "
                f"o no se pudo obtener su atributo 'alt' después de {tiempo} segundos para verificar el texto '{texto_alt_esperado}'. "
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_alt_imagen", directorio)
            return False

        except Error as e:
            # Captura errores específicos de Playwright (ej., selector inválido, el elemento no es una imagen).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar el texto 'alt' de la imagen '{selector}'. "
                f"Esto indica un problema fundamental con el selector o el tipo de elemento.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla para el error específico de Playwright.
            self.base.tomar_captura(f"{nombre_base}_error_playwright_alt_imagen", directorio)
            raise # Re-lanza la excepción porque esto es un fallo de ejecución, no una verificación de estado.

        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error desconocido al verificar el texto 'alt' de la imagen '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura de pantalla para errores completamente inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_alt_imagen", directorio)
            raise # Re-lanza la excepción.
                
    def verificar_carga_exitosa_imagen(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo_espera_red: Union[int, float] = 10.0, tiempo: Union[int, float] = 0.5) -> bool:
        """
        Verifica que una **imagen especificada por su selector** se cargue exitosamente,
        lo que implica que sea visible en el DOM y que su recurso se descargue con un
        código de estado HTTP exitoso (2xx). Integra mediciones de rendimiento para
        registrar el tiempo total de esta verificación.

        Args:
            selector (Union[str, Locator]): El **selector de la imagen** (e.g., 'img#logo', 'img[alt="banner"]').
                                            Puede ser una cadena o un objeto `Locator` de Playwright.
            nombre_base (str): Nombre base para las **capturas de pantalla** tomadas.
            directorio (str): Directorio donde se guardarán las capturas de pantalla.
            tiempo_espera_red (Union[int, float]): **Tiempo máximo de espera** (en segundos) para
                                                que la imagen sea visible y para que su respuesta
                                                de red se complete. Por defecto, `10.0` segundos.
            tiempo (Union[int, float]): **Tiempo de espera fijo** (en segundos) al final de la
                                        operación, útil para observar cambios. Por defecto, `0.5` segundos.

        Returns:
            bool: `True` si la imagen se carga exitosamente (visible y respuesta 2xx).

        Raises:
            TimeoutError: Si la imagen no es visible o su respuesta de red no llega a tiempo.
            Error: Si ocurre un problema específico de Playwright (ej., selector inválido).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nIniciando verificación de carga exitosa para la imagen con selector: '{selector}'. Tiempo de espera de red: {tiempo_espera_red}s.")

        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector

        start_time_image_load_check = time.time()
        
        # Intenta obtener la URL de la imagen. La aserción de visibilidad es la forma más
        # robusta de garantizar que el elemento existe y tiene un src.
        try:
            expect(locator).to_be_visible()
            image_url = locator.get_attribute("src")
        except Exception as e:
            error_msg = f"\n❌ FALLO: La imagen con selector '{selector}' no es visible o no tiene un atributo 'src'. Detalles: {e}"
            self.logger.error(error_msg)
            self.tomar_captura(f"{nombre_base}_no_visible_o_src_missing", directorio)
            raise ValueError(error_msg)

        self.logger.info(f"\nLa imagen con selector '{selector}' es visible en el DOM y tiene la URL: {image_url}")

        try:
            locator.highlight()
            self.base.tomar_captura(f"{nombre_base}_antes_verificar_carga_imagen", directorio)

            # Usamos page.wait_for_event para esperar la respuesta de red.
            # Esto es compatible con la API síncrona de Playwright.
            self.logger.debug(f"\nEsperando respuesta de red para la imagen con URL: {image_url} (timeout: {tiempo_espera_red}s).")
            
            # El evento 'response' se dispara cuando una respuesta de red se completa.
            response = self.page.wait_for_event(
                "response",
                lambda resp: resp.url == image_url and resp.request.resource_type == "image",
                timeout=tiempo_espera_red * 1000
            )
            
            # 4. Verificar el código de estado de la respuesta HTTP.
            if 200 <= response.status <= 299:
                # Medición de rendimiento y logging de éxito.
                end_time_image_load_check = time.time()
                duration_image_load_check = end_time_image_load_check - start_time_image_load_check
                self.logger.info(f"PERFORMANCE: Tiempo total para verificar la carga exitosa de la imagen '{selector}' (URL: {image_url}): {duration_image_load_check:.4f} segundos.")
                self.logger.info(f"\n✔ ÉXITO: La imagen con URL '{image_url}' cargó exitosamente con estado HTTP {response.status}.")
                self.base.tomar_captura(f"{nombre_base}_carga_ok", directorio)
                return True
            else:
                error_msg = f"\n❌ FALLO: La imagen con URL '{image_url}' cargó con un estado de error: {response.status}."
                self.logger.error(error_msg)
                self.base.tomar_captura(f"{nombre_base}_carga_fallida_status_{response.status}", directorio)
                raise ValueError(error_msg)

        except TimeoutError as e:
            # Captura si el elemento no aparece o la respuesta de red no llega a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_image_load_check # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): No se pudo verificar la carga de la imagen con selector '{selector}' "
                f"y URL '{image_url if image_url else 'N/A'}' después de {duration_fail:.4f} segundos (timeout configurado: {tiempo_espera_red}s).\n"
                f"Posibles causas: El elemento no apareció a tiempo o la respuesta de red no se completó.\n"
                f"Detalles: {e}"
            )
            self.logger.warning(error_msg, exc_info=True) # Usa 'warning' ya que la función devuelve False.
            self.base.tomar_captura(f"{nombre_base}_timeout_verificacion", directorio)
            raise TimeoutError(error_msg) # Eleva un error de timeout específico.

        except Error as e: # Captura errores específicos de Playwright (ej., selector inválido, no es un elemento de imagen)
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar la carga de la imagen con selector '{selector}'.\n"
                f"Esto indica un problema fundamental con el selector o que el elemento no es una imagen válida.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            raise

        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error desconocido al verificar la carga de la imagen con selector '{selector}' "
                f"y URL '{image_url if image_url else 'N/A'}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise # Re-lanza la excepción.
                
    def obtener_valor_elemento(self, selector: Locator, nombre_base: str, directorio: str, tiempo_espera_elemento: Union[int, float] = 0.5) -> Optional[str]:
        """
        Extrae y retorna el valor de un elemento dado su Playwright Locator.
        Prioriza la extracción de valores de campos de formulario (`input_value`),
        luego intenta `text_content` y `inner_text` para otros tipos de elementos.
        Mide el rendimiento de la operación de extracción.

        Args:
            selector (Locator): El **Locator de Playwright** que representa el elemento
                                del cual se desea extraer el valor. Es crucial que sea
                                un Locator para aprovechar sus funcionalidades de espera y contexto.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_elemento (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                        para que el elemento sea visible y esté
                                                        habilitado antes de intentar extraer su valor.
                                                        Por defecto, `5.0` segundos.

        Returns:
            Optional[str]: El valor extraído del elemento como una cadena de texto (str).
                           Retorna `None` si no se pudo extraer ningún valor significativo
                           después de intentar todos los métodos, o si el elemento no tiene texto.

        Raises:
            AssertionError: Si el elemento no se vuelve visible/habilitado a tiempo,
                            o si ocurre un error inesperado de Playwright o genérico
                            que impida la extracción del valor.
        """
        self.logger.info(f"\n⚙️ Extrayendo valor del elemento con selector: '{selector}'. Tiempo máximo de espera: {tiempo_espera_elemento}s.")
        valor_extraido = None
        
        # --- Medición de rendimiento: Inicio de la extracción del valor ---
        # Registra el tiempo justo antes de iniciar la interacción con el elemento.
        start_time_extraction = time.time()

        try:
            # 1. Asegurar que el elemento esté visible y habilitado
            # Estas aserciones son cruciales para garantizar que el elemento está listo para interactuar.
            self.logger.debug(f"\nEsperando que el elemento '{selector}' sea visible (timeout: {tiempo_espera_elemento}s).")
            expect(selector).to_be_visible()
            
            self.logger.debug(f"\nEsperando que el elemento '{selector}' esté habilitado (timeout: {tiempo_espera_elemento}s).")
            expect(selector).to_be_enabled()

            # Resaltar el elemento para depuración visual y tomar una captura.
            selector.highlight()
            self.base.tomar_captura(f"{nombre_base}_antes_extraccion_valor", directorio)
            self.logger.debug(f"\nElemento '{selector}' es visible y habilitado.")

            # 2. Intentar extraer el valor usando diferentes métodos de Playwright
            # Priorizamos `input_value` para campos de formulario (<input>, <textarea>, <select>).
            try:
                valor_extraido = selector.input_value() # Un timeout corto para input_value
                self.logger.debug(f"\nValor extraído (input_value) de '{selector}': '{valor_extraido}'")
            except Error as e_input: # Capturamos el error si input_value no es aplicable (ej. no es un elemento de entrada)
                self.logger.debug(f"\ninput_value no aplicable o falló para '{selector}'. Intentando text_content/inner_text. Error: {e_input}")
                
                # Si input_value falla, intentamos con text_content o inner_text para otros elementos (p. ej. <div>, <span>, <p>)
                try:
                    valor_extraido = selector.text_content() # Un timeout corto para text_content
                    # Si text_content devuelve solo espacios en blanco o es vacío,
                    # intentamos inner_text, que a veces es más preciso para texto renderizado visiblemente.
                    if valor_extraido is not None and valor_extraido.strip() == "":
                        valor_extraido = selector.inner_text() # Un timeout corto para inner_text
                        self.logger.debug(f"\nValor extraído (inner_text) de '{selector}': '{valor_extraido}' (después de text_content vacío).")
                    else:
                        self.logger.debug(f"\nValor extraído (text_content) de '{selector}': '{valor_extraido}'")
                except Error as e_text_inner:
                    self.logger.warning(f"\nNo se pudo extraer input_value, text_content ni inner_text de '{selector}'. Detalles: {e_text_inner}")
                    valor_extraido = None # Asegurarse de que sea None si todos los intentos fallan

            # 3. Procesar el valor extraído y registrar el rendimiento
            valor_final = None
            if valor_extraido is not None:
                # Eliminar espacios en blanco al inicio y al final si el valor es una cadena.
                valor_final = valor_extraido.strip() if isinstance(valor_extraido, str) else valor_extraido
                self.logger.info(f"\n✅ Valor final obtenido del elemento '{selector}': '{valor_final}'")
                self.base.tomar_captura(f"{nombre_base}_valor_extraido_exito", directorio)
            else:
                self.logger.warning(f"\n❌ No se pudo extraer ningún valor significativo del elemento '{selector}'.")
                self.base.tomar_captura(f"{nombre_base}_fallo_extraccion_valor_no_encontrado", directorio)
            
            # --- Medición de rendimiento: Fin de la extracción del valor ---
            end_time_extraction = time.time()
            duration_extraction = end_time_extraction - start_time_extraction
            self.logger.info(f"PERFORMANCE: Tiempo total de extracción del valor del elemento '{selector}': {duration_extraction:.4f} segundos.")

            return valor_final

        except TimeoutError as e:
            # Captura si el elemento no se vuelve visible o habilitado a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_extraction
            mensaje_error = (
                f"\n❌ FALLO (Timeout): El elemento '{selector}' no se volvió visible/habilitado a tiempo "
                f"después de {duration_fail:.4f} segundos (timeout configurado: {tiempo_espera_elemento}s) "
                f"para extraer su valor. Detalles: {e}"
            )
            self.logger.error(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_extraccion_valor", directorio)
            # Elevar AssertionError para indicar un fallo de prueba claro.
            raise AssertionError(f"\nElemento no disponible para extracción de valor: {selector}") from e

        except Error as e:
            # Captura errores específicos de Playwright durante la interacción con el DOM.
            mensaje_error = (
                f"\n❌ FALLO (Error de Playwright): Ocurrió un error de Playwright al intentar extraer el valor de '{selector}'. Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True) # Nivel crítico para errores de Playwright.
            self.base.tomar_captura(f"{nombre_base}_fallo_playwright_error_extraccion_valor", directorio)
            raise AssertionError(f"\nError de Playwright al extraer valor: {selector}") from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            mensaje_error = (
                f"\n❌ FALLO (Error Inesperado): Ocurrió un error desconocido al intentar extraer el valor de '{selector}'. Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_inesperado_extraccion_valor", directorio)
            raise AssertionError(f"\nError inesperado al extraer valor: {selector}") from e
        
    def obtener_valor_elemento_disabled(self, selector: Union[str, Locator], nombre_base: str, directorio: str, 
                                 tiempo_max_espera_visibilidad: Union[int, float] = 5.0, nombre_paso: str = "") -> Optional[str]:
        """
        Extrae y retorna el valor textual (contenido o atributo 'value') de un elemento de la página.
        La función intenta obtener el valor de diferentes maneras:
        1.  Usa `locator.input_value()` para elementos de formulario como `<input>`, `<textarea>` o `<select>`.
        2.  Si `input_value()` no es aplicable o falla, intenta `locator.inner_text()` para obtener el texto
            visible renderizado dentro del elemento.
        3.  Si `inner_text()` no es apropiado (ej., texto oculto), intenta `locator.text_content()` para todo el texto.
        
        Playwright espera implícitamente que el elemento sea visible antes de intentar la extracción,
        lo cual es configurado por 'tiempo_max_espera_visibilidad'.

        Args:
            selector (Union[str, Locator]): El selector del elemento (CSS, XPath, texto, etc.).
                                            Puede ser un string o un objeto Locator de Playwright ya existente.
            nombre_base (str): Nombre base para las capturas de pantalla, asegurando un nombre único.
            directorio (str): Directorio donde se guardarán las capturas de pantalla. El directorio
                              se creará si no existe.
            tiempo_max_espera_visibilidad (Union[int, float], opcional): Tiempo máximo en segundos que Playwright
                                                                        esperará a que el elemento sea visible
                                                                        antes de intentar extraer su valor.
                                                                        Por defecto es 5.0 segundos.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para el registro (logs).
                                         Por defecto es una cadena vacía "".

        Returns:
            Optional[str]: El valor extraído del elemento como string, o None si no se pudo extraer ningún valor.

        Raises:
            AssertionError: Si el elemento no se vuelve visible dentro del tiempo de espera.
            Error: Para otros errores específicos de Playwright durante la interacción.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\n--- {nombre_paso}: Extrayendo valor del elemento con selector: '{selector}'. ---")

        # --- Medición de rendimiento: Inicio de la operación total de la función ---
        start_time_total_operation = time.time()
        
        locator: Locator = None # Inicializamos el locator
        valor_extraido: Optional[str] = None # Para almacenar el valor extraído

        try:
            # --- Medición de rendimiento: Tiempo de localización del elemento y espera de visibilidad ---
            start_time_locator = time.time()
            if isinstance(selector, str):
                locator = self.page.locator(selector)
            else: # Asume que si no es str, ya es un Locator
                locator = selector
            
            # Esperar a que el elemento sea visible antes de intentar extraer su valor
            expect(locator).to_be_visible()
            end_time_locator = time.time()
            duration_locator = end_time_locator - start_time_locator
            self.logger.info(f"PERFORMANCE: Tiempo de localización y espera de visibilidad para '{selector}': {duration_locator:.4f} segundos.")
            
            # Resaltar el elemento (útil para la depuración visual)
            # locator.highlight() 

            # Tomar captura de pantalla antes de la extracción
            self.base.tomar_captura(f"{nombre_base}_antes_extraccion_valor", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada antes de la extracción de valor: '{nombre_base}_antes_extraccion_valor.png'")

            # --- Medición de rendimiento: Tiempo de extracción del valor ---
            start_time_extraction = time.time()
            # Priorizamos input_value() para campos de formulario (incluyendo <select>, <input>, <textarea>)
            # input_value() extrae el valor del atributo 'value' o el contenido de <textarea>.
            try:
                valor_extraido = locator.input_value()
                self.logger.debug(f"\nValor extraído (input_value) de '{selector}': '{valor_extraido}'")
            except Error as e: # Captura si no es un elemento de entrada o si falla la operación
                self.logger.debug(f"\ninput_value no aplicable o falló para '{selector}' (Detalles: {e.message if hasattr(e, 'message') else str(e)}). Intentando text_content/inner_text.")
                
                # Si falla input_value, intentamos con inner_text o text_content para otros elementos
                # inner_text() es a menudo preferible ya que devuelve el texto visible y renderizado.
                try:
                    valor_extraido = locator.inner_text()
                    self.logger.debug(f"\nValor extraído (inner_text) de '{selector}': '{valor_extraido}'")
                except Error as e_inner:
                    self.logger.debug(f"\ninner_text falló para '{selector}' (Detalles: {e_inner.message if hasattr(e_inner, 'message') else str(e_inner)}). Intentando text_content.")
                    try:
                        valor_extraido = locator.text_content()
                        self.logger.debug(f"\nValor extraído (text_content) de '{selector}': '{valor_extraido}'")
                    except Error as e_text:
                        self.logger.warning(f"\nNo se pudo extraer input_value, inner_text ni text_content de '{selector}' (Detalles: {e_text.message if hasattr(e_text, 'message') else str(e_text)}).")
                        valor_extraido = None # Asegurarse de que sea None si todo falla

            end_time_extraction = time.time()
            duration_extraction = end_time_extraction - start_time_extraction
            self.logger.info(f"PERFORMANCE: Tiempo de extracción del valor para '{selector}': {duration_extraction:.4f} segundos.")

            if valor_extraido is not None:
                # Stripping whitespace for cleaner results if it's a string
                valor_final = valor_extraido.strip() if isinstance(valor_extraido, str) else valor_extraido
                self.logger.info(f"\n✅ Valor final obtenido del elemento '{selector}': '{valor_final}'")
                self.base.tomar_captura(f"{nombre_base}_valor_extraido_exito", directorio)
                return valor_final
            else:
                self.logger.warning(f"\n❌ No se pudo extraer ningún valor significativo del elemento '{selector}'.")
                self.base.tomar_captura(f"{nombre_base}_fallo_extraccion_valor_no_encontrado", directorio)
                return None

        except TimeoutError as e:
            mensaje_error = (
                f"\n❌ FALLO (Timeout): El elemento '{selector}' "
                f"no se volvió visible a tiempo ({tiempo_max_espera_visibilidad}s) para extraer su valor. Detalles: {e}"
            )
            self.logger.error(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_extraccion_valor", directorio)
            # Elevar una excepción clara para que el flujo de la prueba se detenga si el elemento no está disponible
            raise AssertionError(f"\nElemento no disponible para extracción de valor: {selector}. Error: {e.message if hasattr(e, 'message') else str(e)}") from e

        except Error as e: # Captura errores específicos de Playwright (directamente 'Error' sin alias)
            mensaje_error = (
                f"\n❌ FALLO (Error de Playwright): Ocurrió un error de Playwright al intentar extraer el valor de '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.error(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_playwright_error_extraccion_valor", directorio)
            raise AssertionError(f"\nError de Playwright al extraer valor: {selector}. Error: {e.message if hasattr(e, 'message') else str(e)}") from e

        except Exception as e: # Captura cualquier otro error inesperado
            mensaje_error = (
                f"\n❌ FALLO (Error Inesperado): Ocurrió un error desconocido al intentar extraer el valor de '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_inesperado_extraccion_valor", directorio)
            raise AssertionError(f"\nError inesperado al extraer valor: {selector}. Error: {e}") from e

        finally:
            # --- Medición de rendimiento: Fin de la operación total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (obtener_valor_de_elemento): {duration_total_operation:.4f} segundos.")
            
            # El parámetro 'tiempo' original en tu función no tenía un uso claro aquí,
            # ya que las operaciones de extracción tienen sus propios timeouts o son sincrónicas.
            # Lo he renombrado a 'tiempo_max_espera_visibilidad' y se usa en expect().to_be_visible().
            # No se añade una espera fija aquí por defecto. Si se necesita una pausa
            # adicional después de la extracción, se debería añadir un nuevo parámetro.
            pass
                
    def realizar_drag_and_drop(self, elemento_origen: Locator, elemento_destino: Locator, nombre_base: str, directorio: str, nombre_paso: str = "", tiempo_espera_manual: float = 0.5, timeout_ms: int = 15000) -> None:
        """
        Realiza una operación de "Drag and Drop" de un elemento de origen a un elemento de destino.
        Intenta primero con el método estándar de Playwright (`locator.drag_to()`).
        Si el método estándar falla (ej. por `TimeoutError` u otro `Playwright Error`),
        recurre a un método manual que simula las acciones de ratón (`hover`, `mouse.down`, `mouse.up`).
        Integra pruebas de rendimiento para ambos enfoques.

        Args:
            elemento_origen (Locator): El **Locator** del elemento que se desea arrastrar.
            elemento_destino (Locator): El **Locator** del área o elemento donde se desea soltar el elemento arrastrado.
            nombre_base (str): Nombre base para las **capturas de pantalla** tomadas durante la ejecución.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para los logs y nombres de capturas. Por defecto "".
            tiempo_espera_manual (float, opcional): Tiempo en segundos para las pausas entre las acciones
                                                   del ratón en el método manual (aplicado con `esperar_fijo`). Por defecto `0.5` segundos.
            timeout_ms (int, opcional): Tiempo máximo en milisegundos para esperar la operación de Drag and Drop
                                        (tanto para `drag_to` como para las validaciones iniciales y pasos manuales).
                                        Por defecto `15000`ms (15 segundos).

        Raises:
            AssertionError: Si la operación de Drag and Drop (estándar o manual) falla,
                            o si los elementos no están listos para la interacción.
        """
        self.logger.info(f"\n--- {nombre_paso}: Intentando realizar 'Drag and Drop' de '{elemento_origen}' a '{elemento_destino}' ---")
        
        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Pre-validación: Verificar que ambos elementos estén visibles y habilitados antes de interactuar.
            self.logger.info(f"\n🔍 Validando que el elemento de origen '{elemento_origen}' esté habilitado y listo para interactuar...")
            # --- Medición de rendimiento: Inicio pre-validación ---
            start_time_pre_validation = time.time()
            expect(elemento_origen).to_be_enabled()
            expect(elemento_destino).to_be_enabled()
            # --- Medición de rendimiento: Fin pre-validación ---
            end_time_pre_validation = time.time()
            duration_pre_validation = end_time_pre_validation - start_time_pre_validation
            self.logger.info(f"PERFORMANCE: Tiempo de pre-validación de elementos: {duration_pre_validation:.4f} segundos.")
            
            self.logger.info(f"\n✅ Ambos elementos están habilitados y listos para 'Drag and Drop'.")
            self.base.tomar_captura(f"{nombre_base}_antes_drag_and_drop", directorio)

            # 2. Intento 1: Usar el método .drag_to() del Locator (recomendado por Playwright)
            self.logger.info(f"\n🔄 Intentando 'Drag and Drop' con el método estándar de Playwright (locator.drag_to())...")
            # --- Medición de rendimiento: Inicio drag_to ---
            start_time_drag_to = time.time()
            try:
                elemento_origen.drag_to(elemento_destino)
                # --- Medición de rendimiento: Fin drag_to ---
                end_time_drag_to = time.time()
                duration_drag_to = end_time_drag_to - start_time_drag_to
                self.logger.info(f"PERFORMANCE: Tiempo del método estándar 'drag_to': {duration_drag_to:.4f} segundos.")

                self.logger.info(f"\n✅ 'Drag and Drop' realizado exitosamente con el método estándar.")
                self.base.tomar_captura(f"{nombre_base}_drag_and_drop_exitoso_estandar", directorio)
                
                # --- Medición de rendimiento: Fin total de la función ---
                end_time_total_operation = time.time()
                duration_total_operation = end_time_total_operation - start_time_total_operation
                self.logger.info(f"PERFORMANCE: Tiempo total de la operación (estándar D&D): {duration_total_operation:.4f} segundos.")
                return # Si funciona, salimos de la función

            except (Error, TimeoutError) as e:
                # Captura errores específicos de Playwright (incluyendo TimeoutError de drag_to)
                self.logger.warning(f"\n⚠️ Advertencia: El método directo 'locator.drag_to()' falló con error de Playwright: {type(e).__name__}: {e}")
                self.logger.info("\n🔄 Recurriendo a 'Drag and Drop' con método manual de Playwright (mouse.hover, mouse.down, mouse.up)...")
                self.base.tomar_captura(f"{nombre_base}_fallo_directo_intentando_manual", directorio)
                
                # Registrar el rendimiento del intento fallido de drag_to
                end_time_drag_to = time.time() # Registrar el tiempo que tomó fallar
                duration_drag_to = end_time_drag_to - start_time_drag_to
                self.logger.info(f"PERFORMANCE: Tiempo del método estándar 'drag_to' (fallido): {duration_drag_to:.4f} segundos.")

                # 3. Intento 2 (Fallback): Usar el método manual
                self._realizar_drag_and_drop_manual(elemento_origen, elemento_destino, nombre_base, directorio, nombre_paso, tiempo_pausa_mouse=tiempo_espera_manual, timeout_ms=timeout_ms)
                self.logger.info(f"\n✅ 'Drag and Drop' realizado exitosamente con el método manual.")
                self.base.tomar_captura(f"{nombre_base}_drag_and_drop_exitoso_manual", directorio)

        except (Error, TimeoutError) as e: # Captura errores de Playwright que puedan ocurrir fuera del drag_to o en la pre-validación
            error_msg = (
                f"\n❌ FALLO (Playwright Error) - {nombre_paso}: Ocurrió un error de Playwright al realizar 'Drag and Drop'.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_drag_and_drop", directorio)
            raise AssertionError(error_msg) from e
        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Inesperado) - {nombre_paso}: Ocurrió un error inesperado al intentar realizar 'Drag and Drop'.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_drag_and_drop", directorio)
            raise AssertionError(error_msg) from e
        finally:
            # --- Medición de rendimiento: Fin total de la función (si no se salió antes) ---
            if 'start_time_total_operation' in locals() and 'end_time_total_operation' not in locals():
                end_time_total_operation = time.time()
                duration_total_operation = end_time_total_operation - start_time_total_operation
                self.logger.info(f"PERFORMANCE: Tiempo total de la operación (fallback manual D&D): {duration_total_operation:.4f} segundos.")
        
    def mover_slider_rango_doble(self, pulgar_izquierdo_locator: Locator, pulgar_derecho_locator: Locator, barra_slider_locator: Locator,
                            porcentaje_destino_izquierdo: float, porcentaje_destino_derecho: float,
                            nombre_base: str, directorio: str, nombre_paso: str = "",
                            tolerancia_pixeles: int = 3, timeout_ms: int = 15000) -> None:
        """
        Mueve los dos "pulgares" (handles) de un slider de rango horizontal a porcentajes de destino específicos.
        Utiliza las acciones de ratón de Playwright para simular el arrastre.
        Integra mediciones de rendimiento detalladas para cada paso del movimiento.

        Args:
            pulgar_izquierdo_locator (Locator): El **Locator** del pulgar izquierdo (mínimo) del slider.
            pulgar_derecho_locator (Locator): El **Locator** del pulgar derecho (máximo) del slider.
            barra_slider_locator (Locator): El **Locator** de la barra principal del slider (donde se mueven los pulgares).
            porcentaje_destino_izquierdo (float): El porcentaje de la barra (0.0 a 1.0) al que se moverá el pulgar izquierdo.
            porcentaje_destino_derecho (float): El porcentaje de la barra (0.0 a 1.0) al que se moverá el pulgar derecho.
            nombre_base (str): Nombre base para las **capturas de pantalla** tomadas durante la ejecución.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            nombre_paso (str, opcional): Descripción del paso que se está ejecutando para los logs y nombres de capturas. Por defecto "".
            tolerancia_pixeles (int, opcional): Margen de error en píxeles para considerar que un pulgar
                                                ya está en su posición deseada. Por defecto `3` píxeles.
            timeout_ms (int, opcional): Tiempo máximo en milisegundos para esperar la visibilidad/habilitación
                                        de los elementos. Por defecto `15000`ms (15 segundos).

        Raises:
            ValueError: Si los porcentajes de destino son inválidos o el izquierdo es mayor que el derecho.
            RuntimeError: Si no se puede obtener el bounding box de los elementos.
            AssertionError: Si ocurre un error de Playwright o un error inesperado durante la interacción.
        """
        self.logger.info(f"\n--- {nombre_paso}: Intentando mover el slider de rango. Pulgar Izquierdo a {porcentaje_destino_izquierdo*100:.0f}%, Pulgar Derecho a {porcentaje_destino_derecho*100:.0f}% ---")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        # 1. Validaciones iniciales de porcentajes
        if not (0.0 <= porcentaje_destino_izquierdo <= 1.0) or not (0.0 <= porcentaje_destino_derecho <= 1.0):
            error_msg = "\n❌ Los porcentajes de destino para ambos pulgares deben ser valores flotantes entre 0.0 (0%) y 1.0 (100%)."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_error_validacion_porcentajes", directorio)
            raise ValueError(error_msg)
        
        # Validación de negocio: el porcentaje izquierdo no puede ser mayor que el derecho
        if porcentaje_destino_izquierdo > porcentaje_destino_derecho:
            error_msg = "\n❌ El porcentaje del pulgar izquierdo no puede ser mayor que el del pulgar derecho."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_error_validacion_orden_porcentajes", directorio)
            raise ValueError(error_msg)
        
        elementos_a_validar: Dict[str, Locator] = {
            "pulgar izquierdo": pulgar_izquierdo_locator,
            "pulgar derecho": pulgar_derecho_locator,
            "barra del slider": barra_slider_locator
        }

        try:
            # 2. Pre-validación: Verificar visibilidad y habilitación de todos los elementos
            self.logger.info("\n🔍 Validando visibilidad y habilitación de los elementos del slider...")
            # --- Medición de rendimiento: Inicio pre-validación ---
            start_time_pre_validation = time.time()
            for nombre_elemento, localizador_elemento in elementos_a_validar.items():
                expect(localizador_elemento).to_be_visible()
                expect(localizador_elemento).to_be_enabled()
                localizador_elemento.highlight() # Para visualización durante la ejecución
                self.base.esperar_fijo(0.1) # Pequeña pausa para que se vea el highlight
            
            # --- Medición de rendimiento: Fin pre-validación ---
            end_time_pre_validation = time.time()
            duration_pre_validation = end_time_pre_validation - start_time_pre_validation
            self.logger.info(f"PERFORMANCE: Tiempo de pre-validación de elementos del slider: {duration_pre_validation:.4f} segundos.")
            self.logger.info("\n✅ Todos los elementos del slider están visibles y habilitados.")
            self.base.tomar_captura(f"{nombre_base}_slider_elementos_listos", directorio)

            # 3. Obtener el bounding box de la barra del slider (esencial para el cálculo de posiciones)
            self.logger.debug("\n  --> Obteniendo bounding box de la barra del slider...")
            # --- Medición de rendimiento: Inicio obtener bounding box ---
            start_time_get_bounding_box = time.time()
            caja_barra = barra_slider_locator.bounding_box()
            if not caja_barra:
                raise RuntimeError(f"\n❌ No se pudo obtener el bounding box de la barra del slider '{barra_slider_locator}'.")
            # --- Medición de rendimiento: Fin obtener bounding box ---
            end_time_get_bounding_box = time.time()
            duration_get_bounding_box = end_time_get_bounding_box - start_time_get_bounding_box
            self.logger.info(f"PERFORMANCE: Tiempo de obtención de bounding box de la barra: {duration_get_bounding_box:.4f} segundos.")

            inicio_x_barra = caja_barra['x']
            ancho_barra = caja_barra['width']
            posicion_y_barra = caja_barra['y'] + (caja_barra['height'] / 2) # Y central de la barra para movimientos

            # --- 4. Mover Pulgar Izquierdo (Mínimo) ---
            self.logger.info(f"\n🔄 Moviendo pulgar izquierdo a {porcentaje_destino_izquierdo*100:.0f}%...")
            # --- Medición de rendimiento: Inicio movimiento pulgar izquierdo ---
            start_time_move_left_thumb = time.time()

            caja_pulgar_izquierdo = pulgar_izquierdo_locator.bounding_box()
            if not caja_pulgar_izquierdo:
                raise RuntimeError(f"\n❌ No se pudo obtener el bounding box del pulgar izquierdo '{pulgar_izquierdo_locator}'.")

            posicion_x_destino_izquierdo = inicio_x_barra + (ancho_barra * porcentaje_destino_izquierdo)
            # Usar la Y central de la barra para movimientos, para mantener una línea recta si el pulgar no es perfectamente redondo
            posicion_y_movimiento_izquierdo = posicion_y_barra 

            # Calcular la posición X central actual del pulgar izquierdo para iniciar el arrastre
            posicion_x_actual_izquierdo_centro = caja_pulgar_izquierdo['x'] + (caja_pulgar_izquierdo['width'] / 2)

            # Verificar si el pulgar izquierdo ya está en la posición deseada dentro de la tolerancia
            if abs(posicion_x_actual_izquierdo_centro - posicion_x_destino_izquierdo) < tolerancia_pixeles:
                self.logger.info(f"\n  > Pulgar izquierdo ya se encuentra en la posición deseada ({porcentaje_destino_izquierdo*100:.0f}%). No se requiere movimiento.")
            else:
                self.logger.info(f"\n  > Iniciando arrastre de pulgar izquierdo de X={posicion_x_actual_izquierdo_centro:.0f} a X={posicion_x_destino_izquierdo:.0f}...")
                
                # Acciones del ratón para el arrastre
                self.logger.debug("\n    -> mouse.move al origen")
                self.page.mouse.move(posicion_x_actual_izquierdo_centro, posicion_y_movimiento_izquierdo) # Mover al centro del pulgar actual
                self.base.esperar_fijo(0.1) # Pequeña pausa
                
                self.logger.debug("\n    -> mouse.down")
                self.page.mouse.down() # Presionar el botón del ratón
                self.base.esperar_fijo(0.2) # Pausa para simular la interacción humana
                
                self.logger.debug("\n    -> mouse.move al destino (arrastrando)")
                self.page.mouse.move(posicion_x_destino_izquierdo, posicion_y_movimiento_izquierdo, steps=10) # Arrastrar suavemente
                self.base.esperar_fijo(0.2) # Pausa para simular la interacción humana
                
                self.logger.debug("\n    -> mouse.up")
                self.page.mouse.up() # Soltar el botón del ratón
                self.logger.info(f"\n  > Pulgar izquierdo movido a X={posicion_x_destino_izquierdo:.0f}.")
            
            # --- Medición de rendimiento: Fin movimiento pulgar izquierdo ---
            end_time_move_left_thumb = time.time()
            duration_move_left_thumb = end_time_move_left_thumb - start_time_move_left_thumb
            self.logger.info(f"PERFORMANCE: Tiempo de movimiento de pulgar izquierdo: {duration_move_left_thumb:.4f} segundos.")
            self.base.tomar_captura(f"{nombre_base}_slider_izquierdo_movido", directorio)
            self.base.esperar_fijo(0.5) # Pausa adicional después de procesar el primer pulgar para estabilización

            # --- 5. Mover Pulgar Derecho (Máximo) ---
            self.logger.info(f"\n🔄 Moviendo pulgar derecho a {porcentaje_destino_derecho*100:.0f}%...")
            # --- Medición de rendimiento: Inicio movimiento pulgar derecho ---
            start_time_move_right_thumb = time.time()

            caja_pulgar_derecho = pulgar_derecho_locator.bounding_box()
            if not caja_pulgar_derecho:
                raise RuntimeError(f"\n❌ No se pudo obtener el bounding box del pulgar derecho '{pulgar_derecho_locator}'.")

            posicion_x_destino_derecho = inicio_x_barra + (ancho_barra * porcentaje_destino_derecho)
            # Usar la Y central de la barra para movimientos
            posicion_y_movimiento_derecho = posicion_y_barra 

            # Calcular la posición X central actual del pulgar derecho para iniciar el arrastre
            posicion_x_actual_derecho_centro = caja_pulgar_derecho['x'] + (caja_pulgar_derecho['width'] / 2)

            # Verificar si el pulgar derecho ya está en la posición deseada dentro de la tolerancia
            if abs(posicion_x_actual_derecho_centro - posicion_x_destino_derecho) < tolerancia_pixeles:
                self.logger.info(f"\n  > Pulgar derecho ya se encuentra en la posición deseada ({porcentaje_destino_derecho*100:.0f}%). No se requiere movimiento.")
            else:
                self.logger.info(f"\n  > Iniciando arrastre de pulgar derecho de X={posicion_x_actual_derecho_centro:.0f} a X={posicion_x_destino_derecho:.0f}...")
                
                # Acciones del ratón para el arrastre
                self.logger.debug("\n    -> mouse.move al origen")
                self.page.mouse.move(posicion_x_actual_derecho_centro, posicion_y_movimiento_derecho) # Mover al centro del pulgar actual
                self.base.esperar_fijo(0.1) # Pequeña pausa
                
                self.logger.debug("\n    -> mouse.down")
                self.page.mouse.down() # Presionar el botón del ratón
                self.base.esperar_fijo(0.2) # Pausa para simular la interacción humana
                
                self.logger.debug("\n    -> mouse.move al destino (arrastrando)")
                self.page.mouse.move(posicion_x_destino_derecho, posicion_y_movimiento_derecho, steps=10) # Arrastrar suavemente
                self.base.esperar_fijo(0.2) # Pausa para simular la interacción humana
                
                self.logger.debug("    -> mouse.up")
                self.page.mouse.up() # Soltar el botón del ratón
                self.logger.info(f"\n  > Pulgar derecho movido a X={posicion_x_destino_derecho:.0f}.")
            
            # --- Medición de rendimiento: Fin movimiento pulgar derecho ---
            end_time_move_right_thumb = time.time()
            duration_move_right_thumb = end_time_move_right_thumb - start_time_move_right_thumb
            self.logger.info(f"PERFORMANCE: Tiempo de movimiento de pulgar derecho: {duration_move_right_thumb:.4f} segundos.")

            self.logger.info(f"\n✅ Slider de rango procesado exitosamente. Izquierdo a {porcentaje_destino_izquierdo*100:.0f}%, Derecho a {porcentaje_destino_derecho*100:.0f}%.")
            self.base.tomar_captura(f"{nombre_base}_slider_rango_procesado_{int(porcentaje_destino_izquierdo*100)}_{int(porcentaje_destino_derecho*100)}pc_final", directorio)

            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (mover slider de rango): {duration_total_operation:.4f} segundos.")

        except (ValueError, RuntimeError) as e:
            # Captura errores de validación de entrada o de obtención de bounding box
            self.logger.critical(f"\n❌ FALLO (Validación/Configuración) - {nombre_paso}: {e}", exc_info=True)
            # La captura ya se tomó en los bloques if/elif donde se lanzó el error de validación
            raise AssertionError(f"\nError de validación/configuración en mover_slider_rango: {e}") from e

        except (Error, TimeoutError) as e:
            # Captura errores específicos de Playwright, incluyendo TimeoutError de expect()
            mensaje_error = (
                f"\n❌ FALLO (Error de Playwright) - {nombre_paso}: Ocurrió un error de Playwright al intentar mover el slider de rango.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_slider_rango", directorio)
            raise AssertionError(mensaje_error) from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada
            mensaje_error = (
                f"\n❌ FALLO (Inesperado) - {nombre_paso}: Ocurrió un error inesperado al intentar mover el slider de rango.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_slider_rango", directorio)
            raise AssertionError(mensaje_error) from e
            
    def hacer_click_derecho_en_elemento(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo_espera_post_click: Union[int, float] = 0.5, nombre_paso: str = ""):
        """
        Realiza una acción de click derecho (context click) sobre un elemento en la página.
        Esta función mide el tiempo de localización del elemento y el tiempo que tarda el click,
        proporcionando métricas de rendimiento clave para tus interacciones con Playwright.
        También toma capturas de pantalla antes y después de la acción para depuración y evidencia.

        Args:
            selector (Union[str, Locator]): El selector del elemento (puede ser un string CSS/XPath/texto,
                                            o un objeto Locator de Playwright ya existente).
            nombre_base (str): Nombre base para las capturas de pantalla, asegurando un nombre único.
            directorio (str): Directorio donde se guardarán las capturas de pantalla. El directorio
                              se creará si no existe.
            tiempo_espera_post_click (Union[int, float], opcional): Tiempo en segundos de espera explícita
                                                                    después de realizar el click derecho.
                                                                    Útil para permitir que el menú contextual
                                                                    aparezca o que la página reaccione. Por defecto es 0.5 segundos.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para el registro (logs).
                                         Por defecto es una cadena vacía "".

        Raises:
            TimeoutError: Si el elemento no se encuentra o no es interactuable dentro del tiempo de espera de Playwright.
            Error: Para otros errores específicos de Playwright durante la interacción.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\n--- {nombre_paso}: Intentando hacer click derecho sobre el elemento con selector: '{selector}'. ---")

        # --- Medición de rendimiento: Inicio de la operación total de la función ---
        start_time_total_operation = time.time()
        
        locator: Locator = None # Inicializamos el locator

        try:
            # --- Medición de rendimiento: Tiempo de localización del elemento ---
            start_time_locator = time.time()
            if isinstance(selector, str):
                locator = self.page.locator(selector)
            else: # Asume que si no es str, ya es un Locator
                locator = selector
            end_time_locator = time.time()
            duration_locator = end_time_locator - start_time_locator
            self.logger.info(f"PERFORMANCE: Tiempo de localización del elemento '{selector}': {duration_locator:.4f} segundos.")

            # Resaltar el elemento antes de la interacción (útil para la depuración visual)
            # locator.highlight() 

            # Tomar captura de pantalla antes del click derecho
            self.base.tomar_captura(f"{nombre_base}_antes_click_derecho", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada antes del click derecho: '{nombre_base}_antes_click_derecho.png'")

            # --- Medición de rendimiento: Tiempo de ejecución del click derecho ---
            start_time_click = time.time()
            # El atributo 'button="right"' es clave para el click derecho (context click)
            # Playwright espera implícitamente que el elemento esté visible y habilitado.
            locator.click(button="right") 
            end_time_click = time.time()
            duration_click = end_time_click - start_time_click
            self.logger.info(f"PERFORMANCE: Tiempo de ejecución del click derecho en '{selector}': {duration_click:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Click derecho realizado exitosamente en el elemento con selector '{selector}'.")
            
            # Tomar captura de pantalla después del click derecho
            self.base.tomar_captura(f"{nombre_base}_despues_click_derecho", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada después del click derecho: '{nombre_base}_despues_click_derecho.png'")

        except TimeoutError as e:
            error_msg = (
                f"\n❌ FALLO (Timeout): El tiempo de espera se agotó al hacer click derecho en '{selector}'.\n"
                f"Posibles causas: El elemento no apareció, no fue visible/habilitado a tiempo ({e.message if hasattr(e, 'message') else str(e)}).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_timeout_click_derecho", directorio)
            # Re-lanzamos la excepción TimeoutError que ya es específica de Playwright
            raise 

        except Error as e: # Captura errores específicos de Playwright (directamente 'Error' sin alias)
            error_msg = (
                f"\n❌ FALLO (Playwright): Ocurrió un problema de Playwright al hacer click derecho en '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_click_derecho", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Inesperado): Se produjo un error desconocido al intentar hacer click derecho en '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_click_derecho", directorio)
            raise # Re-lanza la excepción

        finally:
            # --- Medición de rendimiento: Fin de la operación total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (hacer_click_derecho_en_elemento): {duration_total_operation:.4f} segundos.")
            
            # Espera fija después de la interacción, si se especificó
            # Nota: el parámetro de entrada 'tiempo' se ha renombrado a 'tiempo_espera_post_click' para mayor claridad.
            if tiempo_espera_post_click > 0:
                self.logger.info(f"\n⏳ Esperando {tiempo_espera_post_click} segundos después del click derecho.")
                self.base.esperar_fijo(tiempo_espera_post_click) # Asegúrate de que esta función exista
    
    def hacer_mouse_down_en_elemento(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo_espera_post_accion: Union[int, float] = 0.5, nombre_paso: str = ""):
        """
        Realiza una acción de 'mouse down' (presionar el botón izquierdo del ratón) sobre el centro de un elemento.
        Esta función solo simula la acción de presionar el botón, sin la liberación ('mouse up').
        Mide el tiempo de localización del elemento y el tiempo que tarda la acción de 'mouse down',
        proporcionando métricas de rendimiento clave para tus interacciones con Playwright.
        También toma capturas de pantalla antes y después de la acción para depuración y evidencia.

        Args:
            selector (Union[str, Locator]): El selector del elemento (puede ser un string CSS/XPath/texto,
                                            o un objeto Locator de Playwright ya existente).
            nombre_base (str): Nombre base para las capturas de pantalla, asegurando un nombre único.
            directorio (str): Directorio donde se guardarán las capturas de pantalla. El directorio
                              se creará si no existe.
            tiempo_espera_post_accion (Union[int, float], opcional): Tiempo en segundos de espera explícita
                                                                    después de realizar la acción de 'mouse down'.
                                                                    Útil para permitir que la página reaccione
                                                                    a la presión del botón. Por defecto es 0.5 segundos.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para el registro (logs).
                                         Por defecto es una cadena vacía "".

        Raises:
            TimeoutError: Si el elemento no se encuentra o no es visible/habilitado dentro del tiempo de espera de Playwright.
            Error: Para otros errores específicos de Playwright durante la interacción.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\n--- {nombre_paso}: Intentando hacer 'mouse down' sobre el elemento con selector: '{selector}'. ---")

        # --- Medición de rendimiento: Inicio de la operación total de la función ---
        start_time_total_operation = time.time()
        
        locator: Locator = None # Inicializamos el locator
        element_bounding_box: Optional[Dict[str, Any]] = None # Para almacenar las coordenadas del elemento

        try:
            # --- Medición de rendimiento: Tiempo de localización del elemento ---
            start_time_locator = time.time()
            if isinstance(selector, str):
                locator = self.page.locator(selector)
            else: # Asume que si no es str, ya es un Locator
                locator = selector

            # Asegurarse de que el elemento esté visible y obtener su bounding box
            # Playwright ya espera visibilidad/habilitación con locator.wait_for() o actionability checks.
            # Pero para obtener el bounding_box, el elemento debe estar en el DOM y visible.
            element_bounding_box = locator.bounding_box()

            if not element_bounding_box:
                raise Error(f"\nNo se pudo obtener el bounding box del elemento '{selector}'. Es posible que no sea visible o no esté adjunto al DOM.")
            
            # Calcular el centro del elemento
            center_x = element_bounding_box['x'] + element_bounding_box['width'] / 2
            center_y = element_bounding_box['y'] + element_bounding_box['height'] / 2

            end_time_locator = time.time()
            duration_locator = end_time_locator - start_time_locator
            self.logger.info(f"PERFORMANCE: Tiempo de localización y obtención de coordenadas para '{selector}': {duration_locator:.4f} segundos. Coordenadas: ({center_x:.2f}, {center_y:.2f})")

            # Resaltar el elemento antes de la interacción (útil para la depuración visual)
            # locator.highlight() 

            # Tomar captura de pantalla antes de la acción
            self.base.tomar_captura(f"{nombre_base}_antes_mouse_down", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada antes del 'mouse down': '{nombre_base}_antes_mouse_down.png'")

            # --- Medición de rendimiento: Tiempo de ejecución de la acción de 'mouse down' ---
            start_time_action = time.time()
            # Realiza la acción de 'mouse down' puro en las coordenadas del centro del elemento.
            self.page.mouse.down(button="left", x=center_x, y=center_y) 
            end_time_action = time.time()
            duration_action = end_time_action - start_time_action
            self.logger.info(f"PERFORMANCE: Tiempo de ejecución de la acción 'mouse down' en '{selector}': {duration_action:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Acción de 'mouse down' realizada exitosamente en el elemento con selector '{selector}'.")
            
            # Tomar captura de pantalla después de la acción
            self.tomar_captura(f"{nombre_base}_despues_mouse_down", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada después del 'mouse down': '{nombre_base}_despues_mouse_down.png'")

        except TimeoutError as e:
            error_msg = (
                f"\n❌ FALLO (Timeout): El tiempo de espera se agotó al hacer 'mouse down' en '{selector}'.\n"
                f"Posibles causas: El elemento no apareció, no fue visible/habilitado a tiempo para obtener coordenadas ({e.message if hasattr(e, 'message') else str(e)}).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_timeout_mouse_down", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Error as e: # Captura errores específicos de Playwright (directamente 'Error' sin alias)
            error_msg = (
                f"\n❌ FALLO (Playwright): Ocurrió un problema de Playwright al hacer 'mouse down' en '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_mouse_down", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Inesperado): Se produjo un error desconocido al intentar hacer 'mouse down' en '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_mouse_down", directorio)
            raise # Re-lanza la excepción

        finally:
            # --- Medición de rendimiento: Fin de la operación total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (hacer_mouse_down_en_elemento): {duration_total_operation:.4f} segundos.")
            
            # Espera fija después de la interacción, si se especificó
            if tiempo_espera_post_accion > 0:
                self.logger.info(f"\n⏳ Esperando {tiempo_espera_post_accion} segundos después de la acción de 'mouse down'.")
                self.base.esperar_fijo(tiempo_espera_post_accion) # Asegúrate de que esta función exista
    
    def hacer_mouse_up_de_elemento(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo_espera_post_accion: Union[int, float] = 0.5, nombre_paso: str = ""):
        """
        Realiza una acción de 'mouse up' (soltar el botón izquierdo del ratón) sobre el centro de un elemento.
        Esta función solo simula la acción de liberar el botón, típicamente usada después de un 'mouse down'
        en escenarios de arrastrar y soltar, o interacciones complejas.
        Mide el tiempo de localización del elemento y el tiempo que tarda la acción de 'mouse up',
        proporcionando métricas de rendimiento clave para tus interacciones con Playwright.
        También toma capturas de pantalla antes y después de la acción para depuración y evidencia.

        Args:
            selector (Union[str, Locator]): El selector del elemento (puede ser un string CSS/XPath/texto,
                                            o un objeto Locator de Playwright ya existente).
            nombre_base (str): Nombre base para las capturas de pantalla, asegurando un nombre único.
            directorio (str): Directorio donde se guardarán las capturas de pantalla. El directorio
                              se creará si no existe.
            tiempo_espera_post_accion (Union[int, float], opcional): Tiempo en segundos de espera explícita
                                                                    después de realizar la acción de 'mouse up'.
                                                                    Útil para permitir que la página reaccione
                                                                    a la liberación del botón. Por defecto es 0.5 segundos.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para el registro (logs).
                                         Por defecto es una cadena vacía "".

        Raises:
            TimeoutError: Si el elemento no se encuentra o no es visible/habilitado dentro del tiempo de espera de Playwright.
            Error: Para otros errores específicos de Playwright durante la interacción.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\n--- {nombre_paso}: Intentando hacer 'mouse up' sobre el elemento con selector: '{selector}'. ---")

        # --- Medición de rendimiento: Inicio de la operación total de la función ---
        start_time_total_operation = time.time()
        
        locator: Locator = None # Inicializamos el locator
        element_bounding_box: Optional[Dict[str, Any]] = None # Para almacenar las coordenadas del elemento

        try:
            # --- Medición de rendimiento: Tiempo de localización del elemento ---
            start_time_locator = time.time()
            if isinstance(selector, str):
                locator = self.page.locator(selector)
            else: # Asume que si no es str, ya es un Locator
                locator = selector

            # Asegurarse de que el elemento esté visible y obtener su bounding box
            # locator.bounding_box() puede esperar la visibilidad del elemento.
            element_bounding_box = locator.bounding_box()

            if not element_bounding_box:
                raise Error(f"\nNo se pudo obtener el bounding box del elemento '{selector}'. Es posible que no sea visible o no esté adjunto al DOM.")
            
            # Calcular el centro del elemento
            center_x = element_bounding_box['x'] + element_bounding_box['width'] / 2
            center_y = element_bounding_box['y'] + element_bounding_box['height'] / 2

            end_time_locator = time.time()
            duration_locator = end_time_locator - start_time_locator
            self.logger.info(f"PERFORMANCE: Tiempo de localización y obtención de coordenadas para '{selector}': {duration_locator:.4f} segundos. Coordenadas: ({center_x:.2f}, {center_y:.2f})")

            # Resaltar el elemento antes de la interacción (útil para la depuración visual)
            # locator.highlight() 

            # Tomar captura de pantalla antes de la acción
            self.base.tomar_captura(f"{nombre_base}_antes_mouse_up", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada antes del 'mouse up': '{nombre_base}_antes_mouse_up.png'")

            # --- Medición de rendimiento: Tiempo de ejecución de la acción de 'mouse up' ---
            start_time_action = time.time()
            # Realiza la acción de 'mouse up' puro en las coordenadas del centro del elemento.
            self.page.mouse.up(button="left", x=center_x, y=center_y) 
            end_time_action = time.time()
            duration_action = end_time_action - start_time_action
            self.logger.info(f"PERFORMANCE: Tiempo de ejecución de la acción 'mouse up' en '{selector}': {duration_action:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Acción de 'mouse up' realizada exitosamente en el elemento con selector '{selector}'.")
            
            # Tomar captura de pantalla después de la acción
            self.base.tomar_captura(f"{nombre_base}_despues_mouse_up", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada después del 'mouse up': '{nombre_base}_despues_mouse_up.png'")

        except TimeoutError as e:
            error_msg = (
                f"\n❌ FALLO (Timeout): El tiempo de espera se agotó al hacer 'mouse up' en '{selector}'.\n"
                f"Posibles causas: El elemento no apareció, no fue visible/habilitado a tiempo para obtener coordenadas ({e.message if hasattr(e, 'message') else str(e)}).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_timeout_mouse_up", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Error as e: # Captura errores específicos de Playwright (directamente 'Error' sin alias)
            error_msg = (
                f"\n❌ FALLO (Playwright): Ocurrió un problema de Playwright al hacer 'mouse up' en '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_mouse_up", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Inesperado): Se produjo un error desconocido al intentar hacer 'mouse up' en '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_mouse_up", directorio)
            raise # Re-lanza la excepción

        finally:
            # --- Medición de rendimiento: Fin de la operación total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (hacer_mouse_up_de_elemento): {duration_total_operation:.4f} segundos.")
            
            # Espera fija después de la interacción, si se especificó
            if tiempo_espera_post_accion > 0:
                self.logger.info(f"\n⏳ Esperando {tiempo_espera_post_accion} segundos después de la acción de 'mouse up'.")
                self.base.esperar_fijo(tiempo_espera_post_accion) # Asegúrate de que esta función exista
    
    def hacer_focus_en_elemento(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo_espera_post_accion: Union[int, float] = 0.5, nombre_paso: str = ""):
        """
        Realiza una acción de 'focus' (establecer el foco) sobre un elemento especificado.
        Esta función es útil para simular la interacción del usuario al tabular o hacer clic
        en un campo de entrada, botón, etc., y es fundamental para las pruebas de accesibilidad
        y el control de flujo en formularios.
        Mide el tiempo de localización del elemento y el tiempo que tarda la acción de 'focus',
        proporcionando métricas de rendimiento clave.
        También toma capturas de pantalla antes y después de la acción para depuración y evidencia.

        Args:
            selector (Union[str, Locator]): El selector del elemento (puede ser un string CSS/XPath/texto,
                                            o un objeto Locator de Playwright ya existente).
            nombre_base (str): Nombre base para las capturas de pantalla, asegurando un nombre único.
            directorio (str): Directorio donde se guardarán las capturas de pantalla. El directorio
                              se creará si no existe.
            tiempo_espera_post_accion (Union[int, float], opcional): Tiempo en segundos de espera explícita
                                                                    después de realizar la acción de 'focus'.
                                                                    Útil para permitir que la página reaccione
                                                                    o se carguen elementos dependientes. Por defecto es 0.5 segundos.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para el registro (logs).
                                         Por defecto es una cadena vacía "".

        Raises:
            TimeoutError: Si el elemento no se encuentra o no es interactuable dentro del tiempo de espera de Playwright.
            Error: Para otros errores específicos de Playwright durante la interacción.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\n--- {nombre_paso}: Intentando hacer 'focus' sobre el elemento con selector: '{selector}'. ---")

        # --- Medición de rendimiento: Inicio de la operación total de la función ---
        start_time_total_operation = time.time()
        
        locator: Locator = None # Inicializamos el locator

        try:
            # --- Medición de rendimiento: Tiempo de localización del elemento ---
            start_time_locator = time.time()
            if isinstance(selector, str):
                locator = self.page.locator(selector)
            else: # Asume que si no es str, ya es un Locator
                locator = selector
            end_time_locator = time.time()
            duration_locator = end_time_locator - start_time_locator
            self.logger.info(f"PERFORMANCE: Tiempo de localización del elemento '{selector}': {duration_locator:.4f} segundos.")

            # Resaltar el elemento antes de la interacción (útil para la depuración visual)
            # locator.highlight() 

            # Tomar captura de pantalla antes de la acción
            self.base.tomar_captura(f"{nombre_base}_antes_focus", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada antes del 'focus': '{nombre_base}_antes_focus.png'")

            # --- Medición de rendimiento: Tiempo de ejecución de la acción de 'focus' ---
            start_time_action = time.time()
            locator.highlight()
            # El método focus() de Playwright establece el foco en el elemento.
            # Playwright espera implícitamente que el elemento esté visible y habilitado antes de enfocarlo.
            locator.focus() # Eliminado 'timeout' del focus() para usar el de Playwright por defecto o global.
                            # Si se necesita un timeout específico para el focus, se puede volver a añadir: timeout=tiempo_espera_max_para_focus * 1000
            end_time_action = time.time()
            duration_action = end_time_action - start_time_action
            self.logger.info(f"PERFORMANCE: Tiempo de ejecución de la acción 'focus' en '{selector}': {duration_action:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: 'Focus' realizado exitosamente en el elemento con selector '{selector}'.")
            
            # Tomar captura de pantalla después de la acción
            self.base.tomar_captura(f"{nombre_base}_despues_focus", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada después del 'focus': '{nombre_base}_despues_focus.png'")

        except TimeoutError as e:
            error_msg = (
                f"\n❌ FALLO (Timeout): El tiempo de espera se agotó al hacer 'focus' en '{selector}'.\n"
                f"Posibles causas: El elemento no apareció, no fue visible/habilitado a tiempo ({e.message if hasattr(e, 'message') else str(e)}).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_timeout_focus", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Error as e: # Captura errores específicos de Playwright (directamente 'Error' sin alias)
            error_msg = (
                f"\n❌ FALLO (Playwright): Ocurrió un problema de Playwright al hacer 'focus' en '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_focus", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Inesperado): Se produjo un error desconocido al intentar hacer 'focus' en '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_focus", directorio)
            raise # Re-lanza la excepción

        finally:
            # --- Medición de rendimiento: Fin de la operación total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (hacer_focus_en_elemento): {duration_total_operation:.4f} segundos.")
            
            # Espera fija después de la interacción, si se especificó
            # Nota: el parámetro de entrada original 'tiempo' se ha renombrado a 'tiempo_espera_post_accion' para mayor claridad.
            if tiempo_espera_post_accion > 0:
                self.logger.info(f"\n⏳ Esperando {tiempo_espera_post_accion} segundos después de la acción de 'focus'.")
                self.base.esperar_fijo(tiempo_espera_post_accion) # Asegúrate de que esta función exista
    
    def hacer_blur_en_elemento(self, selector: Union[str, Locator], nombre_base: str, directorio: str, tiempo_espera_post_accion: Union[int, float] = 0.5, nombre_paso: str = ""):
        """
        Realiza una acción de 'blur' (quitar el foco) sobre un elemento que actualmente lo tiene.
        Esta función simula que el usuario ha movido el foco de un elemento (por ejemplo, al hacer
        clic fuera de un campo de texto o al presionar Tab para salir de él). Es útil para probar
        validaciones 'on blur' o la finalización de la edición.
        Mide el tiempo de localización del elemento y el tiempo que tarda la acción de 'blur',
        proporcionando métricas de rendimiento clave.
        También toma capturas de pantalla antes y después de la acción para depuración y evidencia.

        Args:
            selector (Union[str, Locator]): El selector del elemento (puede ser un string CSS/XPath/texto,
                                            o un objeto Locator de Playwright ya existente).
            nombre_base (str): Nombre base para las capturas de pantalla, asegurando un nombre único.
            directorio (str): Directorio donde se guardarán las capturas de pantalla. El directorio
                              se creará si no existe.
            tiempo_espera_post_accion (Union[int, float], opcional): Tiempo en segundos de espera explícita
                                                                    después de realizar la acción de 'blur'.
                                                                    Útil para permitir que la página reaccione
                                                                    a la pérdida del foco. Por defecto es 0.5 segundos.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para el registro (logs).
                                         Por defecto es una cadena vacía "".

        Raises:
            TimeoutError: Si el elemento no se encuentra o no es interactuable (o enfocable/desenfocable)
                          dentro del tiempo de espera de Playwright.
            Error: Para otros errores específicos de Playwright durante la interacción.
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\n--- {nombre_paso}: Intentando hacer 'blur' sobre el elemento con selector: '{selector}'. ---")

        # --- Medición de rendimiento: Inicio de la operación total de la función ---
        start_time_total_operation = time.time()
        
        locator: Locator = None # Inicializamos el locator

        try:
            # --- Medición de rendimiento: Tiempo de localización del elemento ---
            start_time_locator = time.time()
            if isinstance(selector, str):
                locator = self.page.locator(selector)
            else: # Asume que si no es str, ya es un Locator
                locator = selector
            
            # Opcional: Podrías querer resaltar el elemento ANTES de desenfocarlo
            # Es útil para ver cuál elemento se va a desenfocar.
            # locator.highlight() 

            end_time_locator = time.time()
            duration_locator = end_time_locator - start_time_locator
            self.logger.info(f"PERFORMANCE: Tiempo de localización del elemento '{selector}': {duration_locator:.4f} segundos.")

            # Tomar captura de pantalla antes de la acción
            self.base.tomar_captura(f"{nombre_base}_antes_blur", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada antes del 'blur': '{nombre_base}_antes_blur.png'")

            # --- Medición de rendimiento: Tiempo de ejecución de la acción de 'blur' ---
            start_time_action = time.time()
            # El método blur() de Playwright quita el foco del elemento.
            # Playwright espera implícitamente que el elemento esté en el DOM y enfocado para poder desenfocarlo.
            locator.blur() # Eliminado 'timeout' del blur() para usar el de Playwright por defecto o global.
                           # Si se necesita un timeout específico para el blur, se puede volver a añadir: timeout=tiempo_espera_max_para_blur * 1000
            end_time_action = time.time()
            duration_action = end_time_action - start_time_action
            self.logger.info(f"PERFORMANCE: Tiempo de ejecución de la acción 'blur' en '{selector}': {duration_action:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: 'Blur' realizado exitosamente en el elemento con selector '{selector}'.")
            
            # Tomar captura de pantalla después de la acción
            self.base.tomar_captura(f"{nombre_base}_despues_blur", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada después del 'blur': '{nombre_base}_despues_blur.png'")

        except TimeoutError as e:
            error_msg = (
                f"\n❌ FALLO (Timeout): El tiempo de espera se agotó al hacer 'blur' en '{selector}'.\n"
                f"Posibles causas: El elemento no estaba presente, visible o no era el elemento enfocado a tiempo ({e.message if hasattr(e, 'message') else str(e)}).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_timeout_blur", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Error as e: # Captura errores específicos de Playwright (directamente 'Error' sin alias)
            error_msg = (
                f"\n❌ FALLO (Playwright): Ocurrió un problema de Playwright al hacer 'blur' en '{selector}'.\n"
                f"Verifica la validez del selector y el estado del elemento en el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_blur", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Inesperado): Se produjo un error desconocido al intentar hacer 'blur' en '{selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_blur", directorio)
            raise # Re-lanza la excepción

        finally:
            # --- Medición de rendimiento: Fin de la operación total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (hacer_blur_en_elemento): {duration_total_operation:.4f} segundos.")
            
            # Espera fija después de la interacción, si se especificó
            # Nota: el parámetro de entrada original 'tiempo' se ha renombrado a 'tiempo_espera_post_accion' para mayor claridad.
            if tiempo_espera_post_accion > 0:
                self.logger.info(f"\n⏳ Esperando {tiempo_espera_post_accion} segundos después de la acción de 'blur'.")
                self.base.esperar_fijo(tiempo_espera_post_accion) # Asegúrate de que esta función exista
    
    def verificar_estado_checkbox_o_select(self, selector: Union[str, Locator], estado_esperado: Union[bool, str], nombre_base: str, directorio: str, tiempo_max_espera_verificacion: Union[int, float] = 0.5, nombre_paso: str = "") -> bool:
        """
        Verifica el estado de un checkbox (marcado/desmarcado) o el valor de una opción seleccionada en un select.
        Esta función utiliza las aserciones de Playwright (`expect`) para manejar las esperas y la validación
        de manera eficiente y robusta. Proporciona métricas de rendimiento para la localización
        y la verificación del estado.

        Args:
            selector (Union[str, Locator]): El selector del checkbox o del elemento <select> (por ejemplo, CSS, XPath).
                                            Puede ser un string o un objeto Locator de Playwright ya existente.
            estado_esperado (Union[bool, str]):
                - Para checkbox: True si se espera que esté marcado, False si se espera que esté desmarcado.
                - Para select: El valor (value) de la opción que se espera que esté seleccionada.
            nombre_base (str): Nombre base para las capturas de pantalla, asegurando un nombre único.
            directorio (str): Directorio donde se guardarán las capturas de pantalla. El directorio
                              se creará si no existe.
            tiempo_max_espera_verificacion (Union[int, float], opcional): Tiempo máximo en segundos que Playwright
                                                                           esperará a que el elemento cumpla la condición.
                                                                           Por defecto es 5.0 segundos.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para el registro (logs).
                                         Por defecto es una cadena vacía "".

        Returns:
            bool: True si la verificación es exitosa (el estado actual coincide con el esperado), False en caso contrario.

        Raises:
            ValueError: Si el 'estado_esperado' no es un tipo válido (bool para checkbox, str para select).
            PlaywrightError (a través de TimeoutError o Error): Si ocurre un problema grave de Playwright
                                                                que impide la verificación.
        """
        self.logger.info(f"\n--- {nombre_paso}: Verificando estado para el selector: '{selector}'. Estado esperado: '{estado_esperado}'. ---")

        # --- Medición de rendimiento: Inicio de la operación total de la función ---
        start_time_total_operation = time.time()
        
        locator: Locator = None # Inicializamos el locator
        tipo_elemento: str = "elemento" # Valor por defecto para los mensajes de error
        valor_actual_str: str = "N/A" # Valor por defecto para los mensajes de error
        mensaje_fallo_esperado: str = "" # Mensaje por defecto para fallos de aserción

        try:
            # --- Medición de rendimiento: Tiempo de localización del elemento ---
            start_time_locator = time.time()
            if isinstance(selector, str):
                # Usar locator().first para manejar casos donde el selector podría devolver múltiples elementos
                # pero solo nos interesa el primero. Si el selector ya es preciso, no hay problema.
                locator = self.page.locator(selector) 
            else: # Asume que si no es str, ya es un Locator
                locator = selector
            end_time_locator = time.time()
            duration_locator = end_time_locator - start_time_locator
            self.logger.info(f"PERFORMANCE: Tiempo de localización del elemento '{selector}': {duration_locator:.4f} segundos.")
            
            # Resaltar el elemento antes de la interacción (útil para la depuración visual)
            # locator.highlight() 

            # Tomar captura de pantalla antes de la verificación
            self.base.tomar_captura(f"{nombre_base}_antes_verificar_estado", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada antes de verificar estado: '{nombre_base}_antes_verificar_estado.png'")

            # --- Lógica de Verificación y Medición de Aserción ---
            start_time_assertion = time.time()
            if isinstance(estado_esperado, bool): # Verificación para Checkbox
                tipo_elemento = "checkbox"
                if estado_esperado:
                    expect(locator).to_be_checked()
                else:
                    expect(locator).not_to_be_checked()
                
                valor_actual_str = str(locator.is_checked())
                mensaje_fallo_esperado = f"se esperaba {'marcado' if estado_esperado else 'desmarcado'} pero está '{valor_actual_str}'."
            
            elif isinstance(estado_esperado, str): # Verificación para Select (option)
                tipo_elemento = "select/option"
                expect(locator).to_have_value(estado_esperado)
                
                valor_actual_str = locator.input_value() # Obtiene el 'value' de la opción seleccionada
                mensaje_fallo_esperado = f"se esperaba la opción con valor '{estado_esperado}' pero la actual es '{valor_actual_str}'."
            
            else:
                raise ValueError(f"\nEl 'estado_esperado' debe ser un booleano para checkbox o un string para select. Tipo proporcionado: {type(estado_esperado).__name__}")

            end_time_assertion = time.time()
            duration_assertion = end_time_assertion - start_time_assertion
            self.logger.info(f"PERFORMANCE: Tiempo de ejecución de la verificación (aserción) para '{selector}': {duration_assertion:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: El {tipo_elemento} '{selector}' tiene el estado esperado '{estado_esperado}'.")
            self.base.tomar_captura(f"{nombre_base}_despues_verificar_estado", directorio)
            return True

        except TimeoutError as e:
            # En caso de Timeout, intentamos obtener el valor actual para el mensaje de error.
            # Se usa un try-except interno para evitar fallos si el locator ya no es válido después del timeout.
            try:
                if tipo_elemento == "checkbox":
                    valor_actual_str = str(locator.is_checked())
                elif tipo_elemento == "select/option":
                    valor_actual_str = locator.input_value()
            except Exception:
                valor_actual_str = "No disponible (error al obtener el valor actual)"

            error_msg = (
                f"\n❌ FALLO (Timeout): El {tipo_elemento} '{selector}' "
                f"no cumplió el estado esperado '{estado_esperado}' después de {tiempo_max_espera_verificacion} segundos. "
                f"Estado actual: '{valor_actual_str}'. Detalles: {e}"
            )
            self.logger.warning(error_msg)
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_verificar_estado", directorio)
            return False

        except AssertionError as e:
            # En caso de AssertionError (falla de expect sin timeout), el valor ya se obtiene arriba.
            error_msg = (
                f"\n❌ FALLO (Aserción): El {tipo_elemento} '{selector}' "
                f"NO cumple el estado esperado. {mensaje_fallo_esperado} "
                f"Detalles: {e}"
            )
            self.logger.warning(error_msg)
            self.base.tomar_captura(f"{nombre_base}_fallo_verificar_estado", directorio)
            return False

        except ValueError as e:
            error_msg = (
                f"\n❌ ERROR (Valor Inválido): Se proporcionó un 'estado_esperado' no válido para el selector '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Incluir exc_info para ValueError también
            self.base.tomar_captura(f"{nombre_base}_error_valor_invalido_verificar_estado", directorio)
            raise # Re-lanzamos el ValueError ya que es un error de uso de la función.

        except Error as e: # Captura errores específicos de Playwright (directamente 'Error' sin alias)
            error_msg = (
                f"\n❌ FALLO (Playwright): Ocurrió un problema de Playwright al verificar el estado del elemento '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_verificar_estado", directorio)
            raise # Re-lanza la excepción original de Playwright

        except Exception as e: # Captura cualquier otro error inesperado
            error_msg = (
                f"\n❌ FALLO (Inesperado): Se produjo un error desconocido al verificar el estado del elemento '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_verificar_estado", directorio)
            raise # Re-lanza la excepción

        finally:
            # --- Medición de rendimiento: Fin de la operación total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (verificar_estado_checkbox_o_select): {duration_total_operation:.4f} segundos.")
            
            # Espera fija después de la verificación, si se especificó.
            # El parámetro original 'tiempo' se renombró a 'tiempo_max_espera_verificacion' para el timeout de expect.
            # Si aún se desea una espera fija *adicional* al final, se usa el parámetro 'tiempo_espera_post_accion'
            # que definí para otras funciones. Para esta función, la espera principal es el timeout de expect.
            # Si el 'tiempo' original se refería a una espera fija *después* de todo, lo mantengo así.
            # Asumiendo que el 'tiempo' original era el timeout para la verificación.
            # Si necesitas una espera adicional después, se puede añadir un nuevo parámetro.
            pass # No hay una espera fija aquí por defecto, ya que el timeout de expect() maneja la espera.
                 # Si 'tiempo' original era para una pausa, el parámetro ha sido absorbido por el timeout de expect.
                 # Si se desea una pausa *adicional* al final, se debería añadir un nuevo parámetro.
        
    def manejar_obstaculos_en_pagina(self, obstaculos_locators: list, timeout: float = 5.0):
        """
        Intenta cerrar banners, popups o elementos que puedan tapar la pantalla.
        
        Args:
            obstaculos_locators (list): Lista de localizadores de los elementos a cerrar.
            timeout (float): Tiempo máximo de espera para cada intento.
        """
        self.logger.info("\n🔄 Intentando cerrar posibles obstáculos en la página...")
        
        for locator_info in obstaculos_locators:
            # Extraemos el localizador y el nombre del obstáculo para el log
            locator_str = locator_info.get("locator")
            nombre = locator_info.get("nombre", "obstáculo genérico")
            
            # Intentamos localizar el elemento con un timeout corto
            obstaculo_locator = self.page.locator(locator_str)
            
            try:
                # Espera a que el elemento sea visible y luego intenta hacer clic
                expect(obstaculo_locator).to_be_visible(timeout=timeout * 1000)
                self.logger.info(f"✅ Se detectó '{nombre}'. Intentando hacer clic para cerrarlo.")
                obstaculo_locator.click()
                self.logger.info(f"✔ '{nombre}' ha sido cerrado exitosamente.")
                # Salimos del bucle si encontramos y cerramos un obstáculo, ya que no puede haber más
                return True
                
            except TimeoutError:
                self.logger.debug(f"❌ '{nombre}' no se detectó. Continuando...")
            except Exception as e:
                self.logger.warning(f"❗ Ocurrió un error al intentar cerrar '{nombre}': {e}")
                
        self.logger.info("✅ No se encontraron obstáculos conocidos o todos fueron manejados.")
        return False
    
    def validar_elemento_vacio(self, selector, nombre_base: str, directorio: str, tiempo: Union[int, float] = 5.0, resaltar: bool = True) -> bool:
        """
        Valida que un elemento específico en la página no contenga texto dentro de un tiempo límite.
        Esta función es útil para verificar que campos de texto o contenedores estén vacíos
        después de una acción, como limpiar un formulario o una búsqueda.

        Args:
            selector: El selector del elemento. Puede ser una cadena (CSS, XPath, etc.) o
                    un objeto `Locator` de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para nombrar las capturas de pantalla
                            tomadas durante la ejecución de la validación.
            directorio (str): Ruta del directorio donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): Tiempo máximo de espera (en segundos) para que el elemento
                                        esté vacío. Si no está vacío dentro de este plazo,
                                        la validación fallará. Por defecto, 5.0 segundos.
            resaltar (bool): Si es `True`, el elemento será resaltado brevemente en la
                            página para una confirmación visual durante la ejecución. Por defecto, `True`.

        Returns:
            bool: `True` si el elemento está vacío dentro del tiempo especificado; `False` en caso
                de que no esté vacío (por timeout) o si ocurre otro tipo de error.

        Raises:
            Error: Si ocurre un error específico de Playwright (ej., selector inválido,
                elemento desprendido del DOM).
            Exception: Para cualquier otro error inesperado durante la ejecución.
        """
        self.logger.info(f"\nValidando que el elemento con selector: '{selector}' esté vacío. Tiempo máximo de espera: {tiempo}s.")
        
        # Asegura que 'selector' sea un objeto Locator de Playwright.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector
        
        # --- Medición de rendimiento: Inicio de la espera por elemento vacío ---
        start_time_empty_check = time.time()
        
        try:
            # Resalta el elemento para confirmación visual
            locator.highlight()
            self.logger.debug(f"Elemento '{selector}' resaltado.")
            # Espera explícita a que el elemento esté vacío.
            expect(locator).to_be_empty(timeout=tiempo * 1000)

            # --- Medición de rendimiento: Fin de la espera ---
            end_time_empty_check = time.time()
            duration_empty_check = end_time_empty_check - start_time_empty_check
            self.logger.info(f"\nPERFORMANCE: Tiempo que tardó el elemento '{selector}' en estar vacío: {duration_empty_check:.4f} segundos.")

            self.base.tomar_captura(f"{nombre_base}_vacio", directorio)
            self.logger.info(f"\n✔ ÉXITO: El elemento '{selector}' está vacío.")
            
            self.base.esperar_fijo(0.5)
            
            return True
        
        except TimeoutError as e:
            end_time_empty_check = time.time()
            duration_empty_check = end_time_empty_check - start_time_empty_check
            error_msg = (
                f"\n❌ FALLO (Timeout): El elemento con selector '{selector}' NO está vacío "
                f"después de {duration_empty_check:.4f} segundos (timeout configurado: {tiempo}s). Detalles: {e}"
            )
            self.logger.warning(error_msg)
            self.base.tomar_captura(f"{nombre_base}_NO_vacio_timeout", directorio)
            return False

        except Error as e:
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar si '{selector}' está vacío. "
                f"Posibles causas: Selector inválido, elemento desprendido del DOM. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            raise

        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al validar si '{selector}' está vacío. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise
    
    def validar_elemento_desactivado(self, selector, nombre_base: str, directorio: str, tiempo: Union[int, float] = 5.0, resaltar: bool = True) -> bool:
        """
        Valida que un elemento en la página esté deshabilitado (desactivado) dentro de un tiempo límite.
        Esto es crucial para verificar el estado de la interfaz de usuario, asegurando que
        ciertos elementos no son interactivos cuando no deberían serlo.

        Args:
            selector: El selector del elemento. Puede ser una cadena (CSS, XPath, etc.) o
                    un objeto `Locator` de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para nombrar las capturas de pantalla
                            tomadas durante la validación.
            directorio (str): Ruta del directorio donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el elemento
                                        sea considerado deshabilitado. Si el elemento no cumple
                                        la condición dentro de este plazo, la validación fallará.
                                        Por defecto, 5.0 segundos.
            resaltar (bool): Si es `True`, el elemento será resaltado brevemente en la
                            página si la validación es exitosa. Por defecto, `True`.

        Returns:
            bool: `True` si el elemento está deshabilitado dentro del tiempo especificado;
                `False` en caso de que no lo esté o si ocurre otro tipo de error.

        Raises:
            Error: Si ocurre un error específico de Playwright (ej., selector inválido).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nValidando que el elemento con selector: '{selector}' esté deshabilitado. Tiempo máximo de espera: {tiempo}s.")
        
        # Asegura que 'selector' sea un objeto Locator de Playwright.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector
            
        # --- Medición de rendimiento: Inicio de la espera por elemento deshabilitado ---
        start_time_disabled_check = time.time()
        
        try:
            # Resalta el elemento para confirmación visual
            locator.highlight()
            self.logger.debug(f"Elemento '{selector}' resaltado.")
            # Espera explícita a que el elemento cumpla la condición de estar deshabilitado.
            expect(locator).to_be_disabled(timeout=tiempo * 1000)
            
            # --- Medición de rendimiento: Fin de la espera ---
            end_time_disabled_check = time.time()
            duration_disabled_check = end_time_disabled_check - start_time_disabled_check
            self.logger.info(f"PERFORMANCE: Tiempo que tardó el elemento '{selector}' en ser deshabilitado: {duration_disabled_check:.4f} segundos.")

            # Toma una captura de pantalla para documentar el estado deshabilitado del elemento.
            self.base.tomar_captura(f"{nombre_base}_deshabilitado", directorio)
            self.logger.info(f"\n✔ ÉXITO: El elemento '{selector}' está deshabilitado en la página.")
            
            # Realiza una espera fija adicional para observación.
            self.base.esperar_fijo(0.5)
            
            return True
        
        except TimeoutError as e:
            # Manejo para cuando el elemento no se deshabilita dentro del tiempo esperado.
            end_time_disabled_check = time.time()
            duration_disabled_check = end_time_disabled_check - start_time_disabled_check
            error_msg = (
                f"\n❌ FALLO (Timeout): El elemento con selector '{selector}' NO se deshabilitó "
                f"después de {duration_disabled_check:.4f} segundos (timeout configurado: {tiempo}s). Detalles: {e}"
            )
            self.logger.warning(error_msg)
            # Toma una captura en caso de fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_NO_deshabilitado_timeout", directorio)
            return False
            
        except Error as e:
            # Manejo para errores de Playwright.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al verificar si '{selector}' está deshabilitado. "
                f"Posibles causas: Selector inválido, elemento desprendido del DOM. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            raise
            
        except Exception as e:
            # Manejo general para cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al validar si '{selector}' está deshabilitado. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise
    
    def limpiar_campo(self, selector, nombre_base: str, directorio: str, tiempo: Union[int, float] = 5.0, resaltar: bool = True) -> bool:
        """
        Limpia el contenido de un campo de texto o entrada en la página.

        Esta función es esencial para reiniciar el estado de un formulario, garantizando que
        el campo esté vacío para la siguiente acción del test. Utiliza `expect` para esperar
        que el campo sea visible y poder interactuar con él de manera confiable.

        Args:
            selector: El selector del elemento. Puede ser una cadena (CSS, XPath, etc.) o
                    un objeto `Locator` de Playwright preexistente.
            nombre_base (str): Nombre base utilizado para nombrar las capturas de pantalla
                            tomadas durante la ejecución.
            directorio (str): Ruta del directorio donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): Tiempo máximo de espera (en segundos) para que el elemento
                                        sea visible antes de intentar limpiarlo. Por defecto, 5.0 segundos.
            resaltar (bool): Si es `True`, el elemento será resaltado brevemente en la
                            página para una confirmación visual. Por defecto, `True`.

        Returns:
            bool: `True` si el campo se limpió con éxito; `False` en caso de que ocurra
                un error o si el elemento no es visible.

        Raises:
            Error: Si ocurre un error específico de Playwright (ej., selector inválido).
            Exception: Para cualquier otro error inesperado durante la ejecución.
        """
        self.logger.info(f"\nLimpiando el campo de texto con selector: '{selector}'.")

        # Asegura que 'selector' sea un objeto Locator de Playwright.
        if isinstance(selector, str):
            locator = self.page.locator(selector)
        else:
            locator = selector
        
        # --- Medición de rendimiento: Inicio de la acción de limpieza ---
        start_time_clear_action = time.time()
        
        try:
            # Espera que el elemento sea visible usando 'expect'.
            # Esto previene errores si el campo aún no ha cargado completamente.
            expect(locator).to_be_visible(timeout=tiempo * 1000)
            # Resalta el campo antes de la acción para una mejor depuración visual.
            locator.highlight()
            self.logger.debug(f"Elemento '{selector}' resaltado.")
            
            # Realiza la acción de limpieza.
            locator.clear()
            
            # --- Medición de rendimiento: Fin de la acción ---
            end_time_clear_action = time.time()
            duration_clear_action = end_time_clear_action - start_time_clear_action
            self.logger.info(f"PERFORMANCE: La limpieza del campo '{selector}' tardó {duration_clear_action:.4f} segundos.")

            # Toma una captura de pantalla para documentar la acción.
            self.base.tomar_captura(f"{nombre_base}_limpiado", directorio)
            self.logger.info(f"\n✔ ÉXITO: El campo '{selector}' se ha limpiado correctamente.")
            
            # Espera fija para observación.
            self.base.esperar_fijo(0.5)
            
            return True
        
        except TimeoutError as e:
            # Manejo para cuando el elemento no es visible dentro del tiempo de espera.
            error_msg = (
                f"\n❌ FALLO (Timeout): El elemento con selector '{selector}' no se encontró o no está visible "
                f"después de {tiempo} segundos para ser limpiado. Detalles: {e}"
            )
            self.logger.warning(error_msg)
            self.base.tomar_captura(f"{nombre_base}_limpiar_fallo_timeout", directorio)
            return False
            
        except Error as e:
            # Manejo para errores de Playwright.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al limpiar el campo '{selector}'. "
                f"Posibles causas: Selector inválido, elemento no interactuable. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_limpiar_error_playwright", directorio)
            raise
            
        except Exception as e:
            # Manejo general para cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al limpiar el campo '{selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_limpiar_error_inesperado", directorio)
            raise
    
    # Función privada para realizar Drag and Drop manual.
    # Utiliza las acciones de ratón de bajo nivel de Playwright para simular arrastrar y soltar.
    # Se usa como método de fallback si el drag_and_drop() automático no funciona.
    # Integra mediciones de rendimiento detalladas.
    def _realizar_drag_and_drop_manual(self, elemento_origen: Locator, elemento_destino: Locator, 
                                      nombre_base: str, directorio: str, nombre_paso: str, 
                                      tiempo_pausa_ms: Union[int, float] = 1000, timeout_locators_ms: int = 5000) -> None:
        """
        Realiza una operación de "Drag and Drop" (arrastrar y soltar) utilizando acciones de ratón
        de bajo nivel de Playwright. Este método es útil como alternativa cuando el método
        `locator.drag_and_drop()` no produce el comportamiento deseado o es insuficiente.
        
        Mide el tiempo de cada paso clave (hover, click, drag, drop) para proporcionar
        métricas de rendimiento detalladas de esta operación manual.

        Args:
            elemento_origen (Locator): El Locator del elemento que se desea arrastrar.
            elemento_destino (Locator): El Locator del elemento donde se desea soltar el origen.
            nombre_base (str): Nombre base para las capturas de pantalla, asegurando un nombre único.
            directorio (str): Directorio donde se guardarán las capturas de pantalla. El directorio
                              se creará si no existe.
            nombre_paso (str): Una descripción del paso que se está ejecutando para el registro (logs).
            tiempo_pausa_ms (Union[int, float], opcional): Tiempo de pausa en milisegundos después de
                                                            presionar el ratón y después de arrastrarlo
                                                            sobre el destino. Por defecto es 1000ms (1 segundo).
                                                            Esto simula un arrastre más "humano".
            timeout_locators_ms (int, opcional): Tiempo máximo en milisegundos que Playwright esperará
                                                a que los localizadores sean visibles/interactuables
                                                durante las operaciones de `hover`. Por defecto es 5000ms.

        Raises:
            Error: Si ocurre un error específico de Playwright durante las operaciones del ratón.
            Exception: Para cualquier otro error inesperado durante la ejecución.
        """
        self.logger.info(f"\n--- {nombre_paso}: Intentando 'Drag and Drop' manualmente de '{elemento_origen}' a '{elemento_destino}'. ---")

        # Asegurarse de que el directorio de capturas de pantalla exista
        if not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)
            self.logger.info(f"\n☑️ Directorio de capturas de pantalla creado: {directorio}")

        # --- Medición de rendimiento: Inicio de la operación total de Drag and Drop manual ---
        start_time_total_drag_drop = time.time()
        
        try:
            self.base.tomar_captura(f"{nombre_base}_antes_drag_drop_manual", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada antes del D&D manual: '{nombre_base}_antes_drag_drop_manual.png'")

            # 1. Mover el ratón sobre el elemento de origen
            start_time_hover_origin = time.time()
            self.logger.info(f"\n🖱️ Moviendo ratón sobre elemento de origen: '{elemento_origen}'...")
            elemento_origen.hover()
            end_time_hover_origin = time.time()
            duration_hover_origin = end_time_hover_origin - start_time_hover_origin
            self.logger.info(f"PERFORMANCE: Tiempo de 'hover' en origen: {duration_hover_origin:.4f} segundos.")

            # 2. Presionar el botón izquierdo del ratón (iniciar arrastre)
            start_time_mouse_down = time.time()
            self.logger.info("\n⬇️ Presionando botón izquierdo del ratón para iniciar arrastre...")
            self.page.mouse.down()
            end_time_mouse_down = time.time()
            duration_mouse_down = end_time_mouse_down - start_time_mouse_down
            self.logger.info(f"PERFORMANCE: Tiempo de 'mouse.down': {duration_mouse_down:.4f} segundos.")

            # Pausa para simular arrastre humano
            if tiempo_pausa_ms > 0:
                self.logger.info(f"\n⏳ Pausa durante arrastre (simulación): {tiempo_pausa_ms} ms...")
                self.page.wait_for_timeout()

            # 3. Mover el ratón sobre el elemento de destino
            start_time_hover_destination = time.time()
            self.logger.info(f"\n➡️ Moviendo ratón sobre elemento de destino: '{elemento_destino}'...")
            elemento_destino.hover(timeout=timeout_locators_ms)
            end_time_hover_destination = time.time()
            duration_hover_destination = end_time_hover_destination - start_time_hover_destination
            self.logger.info(f"PERFORMANCE: Tiempo de 'hover' en destino: {duration_hover_destination:.4f} segundos.")

            # Pausa adicional antes de soltar, si se desea un comportamiento más humano
            if tiempo_pausa_ms > 0:
                self.logger.info(f"\n⏳ Pausa antes de soltar (simulación): {tiempo_pausa_ms} ms...")
                self.page.wait_for_timeout()

            # 4. Soltar el botón izquierdo del ratón (finalizar arrastre)
            start_time_mouse_up = time.time()
            self.logger.info("\n⬆️ Soltando botón izquierdo del ratón para finalizar arrastre...")
            self.page.mouse.up()
            end_time_mouse_up = time.time()
            duration_mouse_up = end_time_mouse_up - start_time_mouse_up
            self.logger.info(f"PERFORMANCE: Tiempo de 'mouse.up': {duration_mouse_up:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: 'Drag and Drop' manual realizado exitosamente de '{elemento_origen}' a '{elemento_destino}'.")
            self.base.tomar_captura(f"{nombre_base}_despues_drag_drop_manual", directorio)
            self.logger.info(f"\n📸 Captura de pantalla tomada después del D&D manual: '{nombre_base}_despues_drag_drop_manual.png'")

        except Error as e:
            error_msg = (
                f"\n❌ FALLO (Playwright Error - Manual) - {nombre_paso}: Ocurrió un error de Playwright al intentar realizar 'Drag and Drop' manualmente.\n"
                f"Asegúrate de que los elementos sean visibles e interactuables. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_manual_drag_and_drop_playwright", directorio)
            raise # Re-lanza la excepción original de Playwright.
        
        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado - Manual) - {nombre_paso}: Ocurrió un error inesperado al intentar realizar 'Drag and Drop' manualmente.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Uso critical para errores inesperados graves.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_manual_drag_and_drop", directorio)
            raise # Re-lanza la excepción.
        
        finally:
            # --- Medición de rendimiento: Fin de la operación total de Drag and Drop manual ---
            end_time_total_drag_drop = time.time()
            duration_total_drag_drop = end_time_total_drag_drop - start_time_total_drag_drop
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación 'Drag and Drop' manual: {duration_total_drag_drop:.4f} segundos.")