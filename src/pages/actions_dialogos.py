import time
from typing import Union, Optional
from playwright.sync_api import Page, Locator, expect, Error, TimeoutError, Dialog

class DialogActions:
    def __init__(self, base_page):
        self.base = base_page
        self.page: Page = base_page.page
        self.logger = base_page.logger
        
    # 40- Función para verificar una alerta simple utilizando page.expect_event().
    # Integra pruebas de rendimiento para medir la aparición y manejo de la alerta.
    def verificar_alerta_simple_con_expect_event(self, selector: Locator, mensaje_esperado: str, nombre_base: str, directorio: str, tiempo_espera_elemento: Union[int, float] = 0.5, tiempo_espera_alerta: Union[int, float] = 0.5) -> bool:
        """
        Verifica una alerta de tipo 'alert' que aparece después de hacer clic en un selector dado.
        Utiliza `page.expect_event("dialog")` de Playwright para esperar y capturar el diálogo.
        Comprueba el tipo de diálogo y su mensaje, y finalmente lo acepta.
        Integra mediciones de rendimiento para la aparición y manejo de la alerta.

        Args:
            selector (Locator): El **Locator de Playwright** del elemento (ej. botón)
                                que, al ser clicado, dispara la alerta.
            mensaje_esperado (str): El **mensaje esperado** dentro del cuerpo de la alerta.
                                    Se verifica si este mensaje está contenido en el texto de la alerta.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_elemento (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                        para que el `selector` esté visible y habilitado
                                                        antes de intentar hacer clic. Por defecto, `5.0` segundos.
            tiempo_espera_alerta (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                      para que la alerta (diálogo) aparezca después
                                                      de hacer clic en el selector. Por defecto, `5.0` segundos.

        Returns:
            bool: `True` si la alerta apareció, es del tipo 'alert', contiene el mensaje esperado
                  y fue aceptada correctamente; `False` en caso contrario o si ocurre un Timeout.

        Raises:
            AssertionError: Si el elemento disparador no está disponible, si la alerta no aparece,
                            si el tipo de diálogo es incorrecto, o si ocurre un error inesperado
                            de Playwright o genérico.
        """
        self.logger.info(f"\n--- Ejecutando verificación de alerta con expect_event: {nombre_base} ---")
        self.logger.info(f"\nVerificando alerta al hacer clic en '{selector}'")
        self.logger.info(f"\n  --> Mensaje de alerta esperado: '{mensaje_esperado}'")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Validar visibilidad y habilitación del selector que disparará la alerta
            self.logger.debug(f"\n  --> Validando visibilidad y habilitación del botón '{selector}' (timeout: {tiempo_espera_elemento}s)...")
            # --- Medición de rendimiento: Inicio de visibilidad y habilitación del elemento ---
            start_time_element_ready = time.time()
            expect(selector).to_be_visible()
            expect(selector).to_be_enabled()
            selector.highlight()
            self.base.esperar_fijo(0.2) # Pequeña pausa visual antes del clic
            # --- Medición de rendimiento: Fin de visibilidad y habilitación del elemento ---
            end_time_element_ready = time.time()
            duration_element_ready = end_time_element_ready - start_time_element_ready
            self.logger.info(f"PERFORMANCE: Tiempo para que el elemento disparador esté listo: {duration_element_ready:.4f} segundos.")
            
            self.base.tomar_captura(f"{nombre_base}_elemento_listo_para_alerta", directorio)


            self.logger.debug(f"\n  --> Preparando expect_event para la alerta y haciendo clic (timeout de alerta: {tiempo_espera_alerta}s)...")
            
            # 2. Esperar el evento de diálogo (alerta) y hacer clic en el selector
            # Se usa `timeout` en `expect_event` para el tiempo máximo de aparición de la alerta.
            # Se usa `timeout` en `click` para el tiempo máximo de clic en el elemento.
            # Se recomienda que el timeout del `expect_event` sea al menos tan grande como el del `click`
            # para dar tiempo a que la alerta aparezca.
            # Playwright automáticamente acepta diálogos si no hay un handler. Aquí, lo manejamos explícitamente.
            with self.page.expect_event("dialog") as info_dialogo:
                # --- Medición de rendimiento: Inicio de click y espera de alerta ---
                start_time_alert_detection = time.time()
                self.logger.debug(f"\n  --> Haciendo clic en el botón '{selector}' para disparar la alerta...")
                selector.click()
            
            dialogo: Dialog = info_dialogo.value # Obtener el objeto Dialog de la alerta
            # --- Medición de rendimiento: Fin de click y espera de alerta ---
            end_time_alert_detection = time.time()
            duration_alert_detection = end_time_alert_detection - start_time_alert_detection
            self.logger.info(f"PERFORMANCE: Tiempo desde el clic hasta la detección de la alerta: {duration_alert_detection:.4f} segundos.")

            self.logger.info(f"\n  --> Alerta detectada. Tipo: '{dialogo.type}', Mensaje: '{dialogo.message}'")
            self.base.tomar_captura(f"{nombre_base}_alerta_detectada", directorio)

            # 3. Validar el tipo de diálogo
            if dialogo.type != "alert":
                dialogo.accept() # Aceptar para no bloquear si es un tipo inesperado
                self.logger.error(f"\n⚠️ Tipo de diálogo inesperado: '{dialogo.type}'. Se esperaba 'alert'.")
                # Re-lanzar como AssertionError para un fallo claro de la prueba
                raise AssertionError(f"\nTipo de diálogo inesperado: '{dialogo.type}'. Se esperaba 'alert'.")

            # 4. Validar el mensaje de la alerta
            # --- Medición de rendimiento: Inicio de verificación del mensaje ---
            start_time_message_verification = time.time()
            if mensaje_esperado not in dialogo.message:
                self.base.tomar_captura(f"{nombre_base}_alerta_mensaje_incorrecto", directorio)
                error_msg = (
                    f"\n❌ FALLO: Mensaje de alerta incorrecto.\n"
                    f"  --> Esperado (contiene): '{mensaje_esperado}'\n"
                    f"  --> Obtenido: '{dialogo.message}'"
                )
                self.logger.error(error_msg)
                dialogo.accept() # Aceptar para no bloquear antes de fallar
                # Re-lanzar como AssertionError para un fallo claro de la prueba
                raise AssertionError(error_msg)
            # --- Medición de rendimiento: Fin de verificación del mensaje ---
            end_time_message_verification = time.time()
            duration_message_verification = end_time_message_verification - start_time_message_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación del mensaje de la alerta: {duration_message_verification:.4f} segundos.")


            # 5. Aceptar la alerta
            dialogo.accept()
            self.logger.info("\n  ✅  --> Alerta ACEPTADA correctamente.")

            # Opcional: Verificar el resultado en la página después de la interacción
            # Si tu aplicación cambia el estado del DOM (ej. un mensaje de éxito/error)
            # después de que la alerta es aceptada, puedes verificarlo aquí.
            # Por ejemplo: expect(self.page.locator("#status_message")).to_have_text("Operación completada");
            self.base.esperar_fijo(0.5) # Pequeña pausa para que el DOM se actualice si es necesario

            self.base.tomar_captura(f"{nombre_base}_alerta_exitosa", directorio)
            self.logger.info(f"\n✅  --> ÉXITO: La alerta se mostró, mensaje verificado y aceptada correctamente.")
            
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (verificación de alerta): {duration_total_operation:.4f} segundos.")

            return True

        except TimeoutError as e:
            # Captura si el selector no está listo o si la alerta no aparece a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Tiempo de espera excedido): El elemento '{selector}' no estuvo listo "
                f"o la alerta no apareció/fue detectada a tiempo ({tiempo_espera_elemento}s para elemento, {tiempo_espera_alerta}s para alerta).\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_alerta_NO_aparece_timeout", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nTimeout al verificar alerta para selector '{selector}'") from e

        except Error as e:
            # Captura errores específicos de Playwright (ej. click fallido, problemas con el diálogo).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al interactuar con el botón o la alerta.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nError de Playwright al verificar alerta para selector '{selector}'") from e

        except AssertionError as e:
            # Captura las AssertionError lanzadas internamente por la función (tipo de diálogo, mensaje incorrecto).
            self.logger.critical(f"\n❌ FALLO (Validación de Alerta): {e}", exc_info=True)
            # La captura ya se tomó en la lógica interna donde se lanzó el AssertionError
            raise # Re-lanzar la excepción original para que el framework la maneje

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al verificar la alerta.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nError inesperado al verificar alerta para selector '{selector}'") from e
    
    # 41- Función para verificar una alerta simple utilizando page.on("dialog") con page.once().
    # Integra pruebas de rendimiento para medir la aparición y manejo de la alerta a través de un listener.
    def verificar_alerta_simple_con_on(self, selector: Locator, mensaje_alerta_esperado: str, nombre_base: str, directorio: str, tiempo_espera_elemento: Union[int, float] = 0.5, tiempo_max_deteccion_alerta: Union[int, float] = 0.7) -> bool:
        """
        Verifica una alerta de tipo 'alert' que aparece después de hacer clic en un selector dado.
        Utiliza `page.once("dialog")` para registrar un manejador de eventos que captura
        y acepta la alerta cuando aparece. Mide el rendimiento de cada fase.

        Args:
            selector (Locator): El **Locator de Playwright** del elemento (ej. botón)
                                que, al ser clicado, dispara la alerta.
            mensaje_alerta_esperado (str): El **mensaje esperado** dentro del cuerpo de la alerta.
                                           Se verifica si este mensaje está contenido en el texto de la alerta.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_elemento (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                        para que el `selector` esté visible y habilitado
                                                        antes de intentar hacer clic. Por defecto, `5.0` segundos.
            tiempo_max_deteccion_alerta (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                              después de hacer clic para que el listener
                                                              detecte y maneje la alerta. Debe ser mayor que
                                                              el tiempo de procesamiento esperado de la alerta.
                                                              Por defecto, `7.0` segundos.

        Returns:
            bool: `True` si la alerta apareció, es del tipo 'alert', contiene el mensaje esperado
                  y fue aceptada correctamente; `False` en caso contrario o si ocurre un Timeout.

        Raises:
            AssertionError: Si el elemento disparador no está disponible, si la alerta no aparece,
                            si el tipo de diálogo es incorrecto, o si ocurre un error inesperado
                            de Playwright o genérico.
        """
        self.logger.info(f"\n--- Ejecutando verificación de alerta con page.once('dialog'): {nombre_base} ---")
        self.logger.info(f"\nVerificando alerta simple al hacer clic en el botón '{selector}'")
        self.logger.info(f"\n  --> Mensaje de alerta esperado: '{mensaje_alerta_esperado}'")

        # Resetear el estado de las banderas para cada ejecución del test
        # Esto es crucial para evitar que valores de una ejecución anterior afecten la actual.
        self._alerta_detectada = False
        self._alerta_mensaje_capturado = ""
        self._alerta_tipo_capturado = ""

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Validar visibilidad y habilitación del selector que disparará la alerta
            self.logger.debug(f"\n  --> Validando visibilidad y habilitación del botón '{selector}' (timeout: {tiempo_espera_elemento}s)...")
            # --- Medición de rendimiento: Inicio de visibilidad y habilitación del elemento ---
            start_time_element_ready = time.time()
            expect(selector).to_be_visible()
            expect(selector).to_be_enabled()
            selector.highlight()
            self.base.esperar_fijo(0.2) # Pequeña pausa visual antes del clic
            # --- Medición de rendimiento: Fin de visibilidad y habilitación del elemento ---
            end_time_element_ready = time.time()
            duration_element_ready = end_time_element_ready - start_time_element_ready
            self.logger.info(f"PERFORMANCE: Tiempo para que el elemento disparador esté listo: {duration_element_ready:.4f} segundos.")
            
            self.base.tomar_captura(f"{nombre_base}_elemento_listo_para_alerta", directorio)

            # 2. Registrar el listener ANTES de la acción que dispara la alerta
            self.logger.debug("\n  --> Registrando listener para la alerta con page.once('dialog')...")
            # Usa page.once para que el listener se desregistre automáticamente después de detectar el primer diálogo.
            # El handler `_get_simple_alert_handler_for_on()` también acepta la alerta internamente.
            self.page.once("dialog", self._get_simple_alert_handler_for_on())

            # 3. Hacer clic en el botón que dispara la alerta
            self.logger.debug(f"\n  --> Haciendo clic en el botón '{selector}'...")
            # --- Medición de rendimiento: Inicio de click y espera de detección de alerta ---
            start_time_click_and_alert_detection = time.time()
            selector.click() # Reutilizar tiempo_espera_elemento para el click

            # 4. Esperar a que el listener haya detectado y manejado la alerta
            self.logger.debug(f"\n  --> Esperando a que la alerta sea detectada y manejada por el listener (timeout: {tiempo_max_deteccion_alerta}s)...")
            # Bucle de espera activa hasta que la bandera _alerta_detectada sea True
            # Se añade un timeout para el bucle, calculado a partir de tiempo_max_deteccion_alerta
            wait_end_time = time.time() + tiempo_max_deteccion_alerta
            while not self._alerta_detectada and time.time() < wait_end_time:
                time.sleep(0.1) # Pausa breve para evitar consumo excesivo de CPU

            # --- Medición de rendimiento: Fin de click y espera de detección de alerta ---
            end_time_click_and_alert_detection = time.time()
            duration_click_and_alert_detection = end_time_click_and_alert_detection - start_time_click_and_alert_detection
            self.logger.info(f"PERFORMANCE: Tiempo desde el clic hasta la detección de la alerta por el listener: {duration_click_and_alert_detection:.4f} segundos.")

            if not self._alerta_detectada:
                error_msg = f"\n❌ FALLO: La alerta no fue detectada por el listener después de {tiempo_max_deteccion_alerta} segundos."
                self.logger.error(error_msg)
                self.base.tomar_captura(f"{nombre_base}_alerta_NO_detectada_timeout", directorio)
                # Re-lanzar como AssertionError para un fallo claro de la prueba
                raise AssertionError(error_msg)
            
            self.base.tomar_captura(f"{nombre_base}_alerta_detectada_por_listener", directorio)
            self.logger.info(f"\n  ✅  Alerta detectada con éxito por el listener.")

            # 5. Validaciones después de que el listener ha actuado
            # --- Medición de rendimiento: Inicio de verificación de contenido de alerta ---
            start_time_alert_content_verification = time.time()
            if self._alerta_tipo_capturado != "alert":
                self.logger.error(f"\n⚠️ Tipo de diálogo inesperado: '{self._alerta_tipo_capturado}'. Se esperaba 'alert'.")
                # Re-lanzar como AssertionError para un fallo claro de la prueba
                raise AssertionError(f"\nTipo de diálogo inesperado: '{self._alerta_tipo_capturado}'. Se esperaba 'alert'.")

            if mensaje_alerta_esperado not in self._alerta_mensaje_capturado:
                self.base.tomar_captura(f"{nombre_base}_alerta_mensaje_incorrecto", directorio)
                error_msg = (
                    f"\n❌ FALLO: Mensaje de alerta incorrecto.\n"
                    f"  --> Esperado (contiene): '{mensaje_alerta_esperado}'\n"
                    f"  --> Obtenido: '{self._alerta_mensaje_capturado}'"
                )
                self.logger.error(error_msg)
                # Re-lanzar como AssertionError para un fallo claro de la prueba
                raise AssertionError(error_msg)
            
            # --- Medición de rendimiento: Fin de verificación de contenido de alerta ---
            end_time_alert_content_verification = time.time()
            duration_alert_content_verification = end_time_alert_content_verification - start_time_alert_content_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación de tipo y mensaje de la alerta: {duration_alert_content_verification:.4f} segundos.")


            # La alerta ya fue aceptada por el handler `_get_simple_alert_handler_for_on()`.
            self.logger.info("\n  ✅  --> Alerta ACEPTADA (por el listener).")

            # Opcional: Verificar el resultado en la página después de la interacción
            # Si tu aplicación cambia el estado del DOM (ej. un mensaje de éxito/error)
            # después de que la alerta es aceptada, puedes verificarlo aquí.
            # Por ejemplo: expect(self.page.locator("#status_message")).to_have_text("Operación completada");
            self.base.esperar_fijo(0.5) # Pequeña pausa para que el DOM se actualice si es necesario

            self.base.tomar_captura(f"{nombre_base}_alerta_exitosa", directorio)
            self.logger.info(f"\n✅  --> ÉXITO: La alerta se mostró, mensaje verificado y aceptada correctamente.")
            
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (verificación de alerta por listener): {duration_total_operation:.4f} segundos.")

            return True

        except TimeoutError as e:
            # Captura si el selector no está listo. La detección de alerta por timeout se maneja en el bucle.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Tiempo de espera excedido): El elemento '{selector}' no estuvo listo "
                f"antes de intentar hacer clic ({tiempo_espera_elemento}s).\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_elemento_NO_listo_timeout", directorio)
            raise AssertionError(f"\nTimeout al preparar el elemento disparador para '{selector}'") from e

        except Error as e:
            # Captura errores específicos de Playwright (ej. click fallido, problemas con el diálogo).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al interactuar con el botón o la alerta.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            raise AssertionError(f"\nError de Playwright al verificar alerta para selector '{selector}'") from e

        except AssertionError as e:
            # Captura las AssertionError lanzadas internamente por la función (alerta no detectada, tipo incorrecto, mensaje incorrecto).
            self.logger.critical(f"\n❌ FALLO (Validación de Alerta): {e}", exc_info=True)
            # La captura ya se tomó en la lógica interna donde se lanzó el AssertionError
            raise # Re-lanzar la excepción original para que el framework la maneje

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al verificar la alerta.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise AssertionError(f"\nError inesperado al verificar alerta para selector '{selector}'") from e
        
    # 42- Función para verificar una alerta de confirmación utilizando page.expect_event().
    # Este método maneja el diálogo exclusivamente con expect_event e integra pruebas de rendimiento.
    def verificar_confirmacion_expect_event(self, selector: Locator, mensaje_esperado: str, accion_confirmacion: str, nombre_base: str, directorio: str, tiempo_espera_elemento: Union[int, float] = 0.5, tiempo_espera_confirmacion: Union[int, float] = 0.7) -> bool:
        """
        Verifica una alerta de tipo 'confirm' que aparece después de hacer clic en un selector dado.
        Utiliza `page.expect_event("dialog")` de Playwright para esperar y capturar el diálogo.
        Comprueba el tipo de diálogo y su mensaje, y finalmente realiza la acción solicitada (aceptar o cancelar).
        Integra mediciones de rendimiento para cada fase de la operación.

        Args:
            selector (Locator): El **Locator de Playwright** del elemento (ej. botón)
                                que, al ser clicado, dispara la confirmación.
            mensaje_esperado (str): El **mensaje esperado** dentro del cuerpo de la confirmación.
                                    Se verifica si este mensaje está contenido en el texto de la confirmación.
            accion_confirmacion (str): La **acción a realizar** en la confirmación:
                                       'accept' para aceptar el diálogo o 'dismiss' para cancelarlo.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_elemento (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                        para que el `selector` esté visible y habilitado
                                                        antes de intentar hacer clic. Por defecto, `5.0` segundos.
            tiempo_espera_confirmacion (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                            para que la confirmación (diálogo) aparezca después
                                                            de hacer clic en el selector. Debe ser mayor que
                                                            el tiempo de procesamiento esperado. Por defecto, `7.0` segundos.

        Returns:
            bool: `True` si la confirmación apareció, es del tipo 'confirm', contiene el mensaje esperado
                  y fue manejada correctamente; `False` en caso contrario o si ocurre un Timeout.

        Raises:
            AssertionError: Si el elemento disparador no está disponible, si la confirmación no aparece,
                            si el tipo de diálogo es incorrecto, si el mensaje no coincide, si la acción
                            de confirmación no es válida, o si ocurre un error inesperado de Playwright o genérico.
        """
        self.logger.info(f"\n--- Ejecutando verificación de confirmación con expect_event: {nombre_base} ---")
        self.logger.info(f"\nVerificando confirmación al hacer clic en '{selector}' para '{accion_confirmacion}'")
        self.logger.info(f"\n  --> Mensaje de confirmación esperado: '{mensaje_esperado}'")

        # Validar la acción de confirmación antes de iniciar la operación
        if accion_confirmacion not in ['accept', 'dismiss']:
            error_msg = f"\n❌ FALLO: Acción de confirmación no válida: '{accion_confirmacion}'. Use 'accept' o 'dismiss'."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_accion_invalida", directorio)
            raise AssertionError(error_msg)

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Validar visibilidad y habilitación del selector que disparará la confirmación
            self.logger.debug(f"\n  --> Validando visibilidad y habilitación del botón '{selector}' (timeout: {tiempo_espera_elemento}s)...")
            # --- Medición de rendimiento: Inicio de visibilidad y habilitación del elemento ---
            start_time_element_ready = time.time()
            expect(selector).to_be_visible()
            expect(selector).to_be_enabled()
            selector.highlight()
            self.base.esperar_fijo(0.2) # Pequeña pausa visual antes del clic
            # --- Medición de rendimiento: Fin de visibilidad y habilitación del elemento ---
            end_time_element_ready = time.time()
            duration_element_ready = end_time_element_ready - start_time_element_ready
            self.logger.info(f"PERFORMANCE: Tiempo para que el elemento disparador esté listo: {duration_element_ready:.4f} segundos.")
            
            self.base.tomar_captura(f"{nombre_base}_elemento_listo_para_confirmacion", directorio)

            # 2. Esperar el evento de diálogo (confirmación) y hacer clic en el selector
            self.logger.debug(f"\n  --> Preparando expect_event para la confirmación y haciendo clic (timeout de confirmación: {tiempo_espera_confirmacion}s)...")
            
            # Se usa `timeout` en `expect_event` para el tiempo máximo de aparición de la confirmación.
            # Se usa `timeout` en `click` para el tiempo máximo de clic en el elemento.
            # Es importante que el timeout de `expect_event` sea suficiente para que la confirmación aparezca.
            with self.page.expect_event("dialog", timeout=int(tiempo_espera_confirmacion * 1000)) as info_dialogo:
                # --- Medición de rendimiento: Inicio de click y espera de confirmación ---
                start_time_confirm_detection = time.time()
                self.logger.debug(f"\n  --> Haciendo clic en el botón '{selector}' para disparar la confirmación...")
                selector.click(timeout=int(tiempo_espera_elemento * 1000)) # Reutilizar tiempo_espera_elemento para el click
            
            dialogo: Dialog = info_dialogo.value # Obtener el objeto Dialog de la confirmación
            # --- Medición de rendimiento: Fin de click y espera de confirmación ---
            end_time_confirm_detection = time.time()
            duration_confirm_detection = end_time_confirm_detection - start_time_confirm_detection
            self.logger.info(f"PERFORMANCE: Tiempo desde el clic hasta la detección de la confirmación: {duration_confirm_detection:.4f} segundos.")

            self.logger.info(f"\n  --> Confirmación detectada. Tipo: '{dialogo.type}', Mensaje: '{dialogo.message}'")
            self.base.tomar_captura(f"{nombre_base}_confirmacion_detectada", directorio)

            # 3. Validar el tipo de diálogo
            if dialogo.type != "confirm":
                # Realizar la acción solicitada incluso si el tipo es incorrecto para no bloquear
                if accion_confirmacion == 'accept':
                    dialogo.accept()
                else:
                    dialogo.dismiss()
                self.logger.error(f"\n⚠️ Tipo de diálogo inesperado: '{dialogo.type}'. Se esperaba 'confirm'.")
                # Re-lanzar como AssertionError para un fallo claro de la prueba
                raise AssertionError(f"\nTipo de diálogo inesperado: '{dialogo.type}'. Se esperaba 'confirm'.")

            # 4. Validar el mensaje de la confirmación
            # --- Medición de rendimiento: Inicio de verificación del mensaje ---
            start_time_message_verification = time.time()
            if mensaje_esperado not in dialogo.message:
                self.base.tomar_captura(f"{nombre_base}_confirmacion_mensaje_incorrecto", directorio)
                error_msg = (
                    f"\n❌ FALLO: Mensaje de confirmación incorrecto.\n"
                    f"  --> Esperado (contiene): '{mensaje_esperado}'\n"
                    f"  --> Obtenido: '{dialogo.message}'"
                )
                self.logger.error(error_msg)
                # Realizar la acción solicitada para no bloquear antes de fallar
                if accion_confirmacion == 'accept':
                    dialogo.accept()
                else:
                    dialogo.dismiss()
                # Re-lanzar como AssertionError para un fallo claro de la prueba
                raise AssertionError(error_msg)
            # --- Medición de rendimiento: Fin de verificación del mensaje ---
            end_time_message_verification = time.time()
            duration_message_verification = end_time_message_verification - start_time_message_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación del mensaje de la confirmación: {duration_message_verification:.4f} segundos.")

            # 5. Realizar la acción solicitada (Aceptar o Cancelar)
            # --- Medición de rendimiento: Inicio de la acción sobre la confirmación ---
            start_time_confirm_action = time.time()
            if accion_confirmacion == 'accept':
                dialogo.accept()
                self.logger.info("\n  ✅  --> Confirmación ACEPTADA.")
            elif accion_confirmacion == 'dismiss':
                dialogo.dismiss()
                self.logger.info("\n  ✅  --> Confirmación CANCELADA.")
            # --- Medición de rendimiento: Fin de la acción sobre la confirmación ---
            end_time_confirm_action = time.time()
            duration_confirm_action = end_time_confirm_action - start_time_confirm_action
            self.logger.info(f"PERFORMANCE: Tiempo de acción ('{accion_confirmacion}') sobre la confirmación: {duration_confirm_action:.4f} segundos.")


            # 6. Opcional: Verificar el resultado en la página después de la interacción
            # Es crucial para confirmar que la acción en el diálogo tuvo el efecto esperado en la UI.
            # Asumo un selector '#demo' y textos específicos, ajusta esto a tu aplicación real.
            # --- Medición de rendimiento: Inicio de verificación del resultado en la página ---
            start_time_post_action_verification = time.time()
            if accion_confirmacion == 'accept':
                # Esto es un ejemplo, ajusta el selector y el texto esperado
                expect(self.page.locator("#demo")).to_have_text("You pressed OK!", timeout=5000)
                self.logger.info("\n  ✅  --> Resultado en página: 'You pressed OK!' verificado.")
            elif accion_confirmacion == 'dismiss':
                # Esto es un ejemplo, ajusta el selector y el texto esperado
                expect(self.page.locator("#demo")).to_have_text("You pressed Cancel!", timeout=5000)
                self.logger.info("\n  ✅  --> Resultado en página: 'You pressed Cancel!' verificado.")
            
            # --- Medición de rendimiento: Fin de verificación del resultado en la página ---
            end_time_post_action_verification = time.time()
            duration_post_action_verification = end_time_post_action_verification - start_time_post_action_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación del resultado en la página: {duration_post_action_verification:.4f} segundos.")


            self.base.tomar_captura(f"{nombre_base}_confirmacion_exitosa_{accion_confirmacion}", directorio)
            self.logger.info(f"\n✅  --> ÉXITO: La confirmación se mostró, mensaje verificado y '{accion_confirmacion}' correctamente.")
            
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (verificación de confirmación): {duration_total_operation:.4f} segundos.")

            return True

        except TimeoutError as e:
            # Captura si el selector no está listo o si la confirmación no aparece a tiempo, o la verificación post-acción falla.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Tiempo de espera excedido): El elemento '{selector}' no estuvo listo, "
                f"la confirmación no apareció/fue detectada a tiempo ({tiempo_espera_elemento}s para elemento, {tiempo_espera_confirmacion}s para confirmación), "
                f"o la verificación del resultado en la página falló.\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_confirmacion_NO_aparece_timeout", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nTimeout al verificar confirmación para selector '{selector}'") from e

        except Error as e:
            # Captura errores específicos de Playwright (ej. click fallido, problemas con el diálogo).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al interactuar con el botón o la confirmación.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nError de Playwright al verificar confirmación para selector '{selector}'") from e

        except AssertionError as e:
            # Captura las AssertionError lanzadas internamente por la función (tipo de diálogo, mensaje incorrecto, acción inválida).
            self.logger.critical(f"\n❌ FALLO (Validación de Confirmación): {e}", exc_info=True)
            # La captura ya se tomó en la lógica interna donde se lanzó el AssertionError
            raise # Re-lanzar la excepción original para que el framework la maneje

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al verificar la confirmación.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise AssertionError(f"\nError inesperado al verificar confirmación para selector '{selector}'") from e
        
    # 43- Función para verificar una alerta de confirmación
    def verificar_confirmacion_on_dialog(self, selector: Locator, mensaje_esperado: str, accion_confirmacion: str, nombre_base: str, directorio: str, tiempo_espera_elemento: Union[int, float] = 5.0, tiempo_max_deteccion_confirmacion: Union[int, float] = 7.0) -> bool:
        """
        Verifica una confirmación de tipo 'confirm' que aparece después de un clic,
        manejando el diálogo de forma instantánea usando un event handler.

        Args:
            selector (Locator): El Locator del elemento que dispara la confirmación.
            mensaje_esperado (str): El mensaje esperado dentro de la confirmación.
            accion_confirmacion (str): La acción a realizar: 'accept' o 'dismiss'.
            nombre_base (str): Nombre base para las capturas de pantalla.
            directorio (str): Ruta del directorio para las capturas.
            tiempo_espera_elemento (Union[int, float]): Tiempo máximo de espera para que el selector esté listo.
            tiempo_max_deteccion_confirmacion (Union[int, float]): Tiempo máximo de espera para que el diálogo aparezca.

        Returns:
            bool: True si la confirmación se manejó correctamente.
        
        Raises:
            AssertionError: Si el elemento no está disponible, el tipo de diálogo es incorrecto o el mensaje no coincide.
        """
        self.logger.info(f"\n--- Ejecutando verificación de confirmación (Manejo de Eventos Instantáneo): {nombre_base} ---")
        self.logger.info(f"\nVerificando confirmación al hacer clic en '{selector}' para '{accion_confirmacion}'")
        self.logger.info(f"\n  --> Mensaje de confirmación esperado: '{mensaje_esperado}'")

        if accion_confirmacion not in ['accept', 'dismiss']:
            error_msg = f"\n❌ FALLO: Acción de confirmación no válida: '{accion_confirmacion}'. Use 'accept' o 'dismiss'."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_accion_invalida", directorio)
            raise AssertionError(error_msg)

        start_time_total_operation = time.time()
        dialog_handler = None  # Definir antes para el ámbito del bloque finally

        def on_dialog(dialog):
            """Manejador de eventos que se ejecuta al instante de aparecer el diálogo."""
            nonlocal dialog_handler  # Para acceder a la variable de ámbito superior
            try:
                self.logger.debug(f"\n  --> Diálogo detectado instantáneamente. Tipo: '{dialog.type}', Mensaje: '{dialog.message}'")
                if dialog.type != "confirm":
                    self.logger.error(f"\n⚠️ Tipo de diálogo inesperado: '{dialog.type}'. Se esperaba 'confirm'.")
                    raise AssertionError(f"Tipo de diálogo inesperado: '{dialog.type}'. Se esperaba 'confirm'.")

                if mensaje_esperado not in dialog.message:
                    self.base.tomar_captura(f"{nombre_base}_confirmacion_mensaje_incorrecto", directorio)
                    error_msg = (
                        f"\n❌ FALLO: Mensaje de confirmación incorrecto.\n"
                        f"  --> Esperado (contiene): '{mensaje_esperado}'\n"
                        f"  --> Obtenido: '{dialog.message}'"
                    )
                    self.logger.error(error_msg)
                    raise AssertionError(error_msg)

                self.logger.debug(f"\n  --> Realizando la acción '{accion_confirmacion}' en el diálogo.")
                if accion_confirmacion == 'accept':
                    dialog.accept()
                elif accion_confirmacion == 'dismiss':
                    dialog.dismiss()
                
                self.logger.info(f"\n  ✅  --> Confirmación manejada (acción '{accion_confirmacion}').")

            except Exception as e:
                # Captura y registra errores dentro del manejador.
                self.logger.critical(f"\n❌ FALLO: Error dentro del manejador de diálogo: {e}", exc_info=True)
                raise e
            finally:
                # Asegúrate de limpiar el manejador para evitar futuras llamadas no deseadas.
                if dialog_handler:
                    self.page.off("dialog", dialog_handler)

        try:
            self.logger.debug("\n--- INICIO del bloque TRY ---")
            self.logger.debug(f"\n  --> Validando visibilidad y habilitación del botón '{selector}' (timeout: {tiempo_espera_elemento}s)...")
            expect(selector).to_be_visible()
            expect(selector).to_be_enabled()
            selector.highlight()
            self.base.esperar_fijo(0.2)
            self.base.tomar_captura(f"{nombre_base}_elemento_listo_para_confirmacion", directorio)

            self.logger.debug("\n  --> Estableciendo el manejador de eventos 'on_dialog' con page.once()...")
            self.page.once("dialog", on_dialog)
            
            self.logger.debug("\n  --> Haciendo clic en el botón para disparar el diálogo...")
            selector.click()

            # Usamos page.wait_for_timeout para esperar un tiempo prudencial a que el evento sea manejado.
            # No se recomienda, pero es una alternativa a wait_for_event cuando la acción
            # ya se realiza en el manejador.
            self.logger.debug(f"\n  --> Esperando {tiempo_max_deteccion_confirmacion}s para que el diálogo sea procesado.")
            self.page.wait_for_timeout(tiempo_max_deteccion_confirmacion * 1000)

            # 5. Verificar el resultado en la página después de la interacción
            self.logger.debug("\n  --> Verificando el resultado en la página.")
            if accion_confirmacion == 'accept':
                expect(self.page.locator("#demo")).to_have_text("You pressed OK!")
                self.logger.info("\n  ✅  --> Resultado en página: 'You pressed OK!' verificado.")
            elif accion_confirmacion == 'dismiss':
                expect(self.page.locator("#demo")).to_have_text("You pressed Cancel!")
                self.logger.info("\n  ✅  --> Resultado en página: 'You pressed Cancel!' verificado.")
            
            self.base.tomar_captura(f"{nombre_base}_confirmacion_exitosa_{accion_confirmacion}", directorio)
            self.logger.info(f"\n✅  --> ÉXITO: La confirmación se mostró y se manejó correctamente.")
            
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación: {duration_total_operation:.4f} segundos.")
            
            return True

        except Exception as e:
            self.logger.debug("\n--- INICIO del bloque EXCEPT ---")
            if dialog_handler:
                self.page.off("dialog", dialog_handler)
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO: Ocurrió un error al verificar la confirmación.\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise AssertionError(f"Error inesperado al verificar confirmación para selector '{selector}'") from e
    
    # 44- Función para verificar_prompt_expect_event (Implementación para Prompt Alert con expect_event).
    # Integra pruebas de rendimiento para medir la aparición, interacción y manejo de un diálogo prompt.
    def verificar_prompt_expect_event(self, selector: Locator, mensaje_prompt_esperado: str, input_text: Optional[str], accion_prompt: str, nombre_base: str, directorio: str, tiempo_espera_elemento: Union[int, float] = 0.5, tiempo_espera_prompt: Union[int, float] = 0.7) -> bool:
        """
        Verifica un cuadro de diálogo 'prompt' que aparece después de hacer clic en un selector dado.
        Utiliza `page.expect_event("dialog")` de Playwright para esperar y capturar el diálogo.
        Comprueba el tipo de diálogo y su mensaje. Si la acción es 'accept', introduce el texto
        proporcionado; de lo contrario, cancela el prompt.
        Integra mediciones de rendimiento para cada fase de la operación.

        Args:
            selector (Locator): El **Locator de Playwright** del elemento (ej. botón)
                                que, al ser clicado, dispara el diálogo prompt.
            mensaje_prompt_esperado (str): El **mensaje esperado** dentro del cuerpo del prompt.
                                           Se verifica si este mensaje está contenido en el texto del prompt.
            input_text (Optional[str]): El **texto a introducir** en el prompt si `accion_prompt` es 'accept'.
                                        Debe ser `None` si `accion_prompt` es 'dismiss'.
            accion_prompt (str): La **acción a realizar** en el prompt:
                                 'accept' para introducir texto y aceptar, o 'dismiss' para cancelar.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_elemento (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                        para que el `selector` esté visible y habilitado
                                                        antes de intentar hacer clic. Por defecto, `5.0` segundos.
            tiempo_espera_prompt (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                     para que el prompt aparezca después de hacer clic en el selector.
                                                     Debe ser mayor que el tiempo de procesamiento esperado.
                                                     Por defecto, `7.0` segundos.

        Returns:
            bool: `True` si el prompt apareció, es del tipo 'prompt', contiene el mensaje esperado
                  y fue manejado correctamente; `False` en caso contrario o si ocurre un Timeout.

        Raises:
            AssertionError: Si el elemento disparador no está disponible, si el prompt no aparece,
                            si el tipo de diálogo es incorrecto, si el mensaje no coincide,
                            si la acción del prompt no es válida, si `input_text` es incorrecto
                            para la acción, o si ocurre un error inesperado de Playwright o genérico.
        """
        self.logger.info(f"\n--- Ejecutando verificación de prompt con expect_event: {nombre_base} ---")
        self.logger.info(f"\nVerificando prompt al hacer clic en '{selector}' para '{accion_prompt}'")
        self.logger.info(f"\n  --> Mensaje del prompt esperado: '{mensaje_prompt_esperado}'")
        if accion_prompt == 'accept':
            self.logger.info(f"\n  --> Texto a introducir: '{input_text}'")

        # Validar la acción y el input_text antes de iniciar la operación
        if accion_prompt not in ['accept', 'dismiss']:
            error_msg = f"\n❌ FALLO: Acción de prompt no válida: '{accion_prompt}'. Use 'accept' o 'dismiss'."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_accion_invalida", directorio)
            raise AssertionError(error_msg)
        if accion_prompt == 'accept' and input_text is None:
            error_msg = "\n❌ FALLO: 'input_text' no puede ser None cuando 'accion_prompt' es 'accept'."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_input_text_missing", directorio)
            raise AssertionError(error_msg)
        if accion_prompt == 'dismiss' and input_text is not None:
            self.logger.warning("\n⚠️ ADVERTENCIA: 'input_text' se ignora cuando 'accion_prompt' es 'dismiss'.")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Validar visibilidad y habilitación del selector que disparará el prompt
            self.logger.debug(f"\n  --> Validando visibilidad y habilitación del botón '{selector}' (timeout: {tiempo_espera_elemento}s)...")
            # --- Medición de rendimiento: Inicio de visibilidad y habilitación del elemento ---
            start_time_element_ready = time.time()
            expect(selector).to_be_visible()
            expect(selector).to_be_enabled()
            selector.highlight()
            self.base.esperar_fijo(0.2) # Pequeña pausa visual antes del clic
            # --- Medición de rendimiento: Fin de visibilidad y habilitación del elemento ---
            end_time_element_ready = time.time()
            duration_element_ready = end_time_element_ready - start_time_element_ready
            self.logger.info(f"PERFORMANCE: Tiempo para que el elemento disparador esté listo: {duration_element_ready:.4f} segundos.")
            
            self.base.tomar_captura(f"{nombre_base}_elemento_listo_para_prompt", directorio)

            # 2. Esperar el evento de diálogo (prompt) y hacer clic en el selector
            self.logger.debug(f"\n  --> Preparando expect_event para el prompt y haciendo clic (timeout de prompt: {tiempo_espera_prompt}s)...")
            
            # Se usa `timeout` en `expect_event` para el tiempo máximo de aparición del prompt.
            # Se usa `timeout` en `click` para el tiempo máximo de clic en el elemento.
            with self.page.expect_event("dialog") as info_dialogo:
                # --- Medición de rendimiento: Inicio de click y espera de prompt ---
                start_time_prompt_detection = time.time()
                self.logger.debug(f"\n  --> Haciendo clic en el botón '{selector}' para disparar el prompt...")
                selector.click()
            
            dialogo: Dialog = info_dialogo.value # Obtener el objeto Dialog del prompt
            # --- Medición de rendimiento: Fin de click y espera de prompt ---
            end_time_prompt_detection = time.time()
            duration_prompt_detection = end_time_prompt_detection - start_time_prompt_detection
            self.logger.info(f"PERFORMANCE: Tiempo desde el clic hasta la detección del prompt: {duration_prompt_detection:.4f} segundos.")

            self.logger.info(f"\n  --> Prompt detectado. Tipo: '{dialogo.type}', Mensaje: '{dialogo.message}', Valor por defecto: '{dialogo.default_value}'")
            self.base.tomar_captura(f"{nombre_base}_prompt_detectado", directorio)

            # 3. Validar el tipo de diálogo
            if dialogo.type != "prompt":
                # Si el tipo es inesperado, intenta cerrarlo para no bloquear el test antes de fallar.
                if accion_prompt == 'accept':
                    dialogo.accept(input_text if input_text is not None else "") # Aceptar con o sin texto
                else:
                    dialogo.dismiss()
                self.logger.error(f"\n⚠️ Tipo de diálogo inesperado: '{dialogo.type}'. Se esperaba 'prompt'.")
                # Re-lanzar como AssertionError para un fallo claro de la prueba
                raise AssertionError(f"\nTipo de diálogo inesperado: '{dialogo.type}'. Se esperaba 'prompt'.")

            # 4. Validar el mensaje del prompt
            # --- Medición de rendimiento: Inicio de verificación del mensaje ---
            start_time_message_verification = time.time()
            if mensaje_prompt_esperado not in dialogo.message:
                self.base.tomar_captura(f"{nombre_base}_prompt_mensaje_incorrecto", directorio)
                error_msg = (
                    f"\n❌ FALLO: Mensaje del prompt incorrecto.\n"
                    f"  --> Esperado (contiene): '{mensaje_prompt_esperado}'\n"
                    f"  --> Obtenido: '{dialogo.message}'"
                )
                self.logger.error(error_msg)
                # Intenta cerrar el diálogo antes de fallar
                if accion_prompt == 'accept':
                    dialogo.accept(input_text if input_text is not None else "")
                else:
                    dialogo.dismiss()
                # Re-lanzar como AssertionError para un fallo claro de la prueba
                raise AssertionError(error_msg)
            # --- Medición de rendimiento: Fin de verificación del mensaje ---
            end_time_message_verification = time.time()
            duration_message_verification = end_time_message_verification - start_time_message_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación del mensaje del prompt: {duration_message_verification:.4f} segundos.")

            # 5. Realizar la acción solicitada (Introducir texto y Aceptar, o Cancelar)
            # --- Medición de rendimiento: Inicio de la acción sobre el prompt ---
            start_time_prompt_action = time.time()
            if accion_prompt == 'accept':
                # El método `accept()` para prompts puede tomar un argumento `promptText`
                dialogo.accept(input_text)
                self.logger.info(f"\n  ✅  --> Texto '{input_text}' introducido en el prompt y ACEPTADO.")
            elif accion_prompt == 'dismiss':
                dialogo.dismiss()
                self.logger.info("\n  ✅  --> Prompt CANCELADO.")
            # No se necesita 'else' aquí, ya se validó 'accion_prompt' al principio
            # --- Medición de rendimiento: Fin de la acción sobre el prompt ---
            end_time_prompt_action = time.time()
            duration_prompt_action = end_time_prompt_action - start_time_prompt_action
            self.logger.info(f"PERFORMANCE: Tiempo de acción ('{accion_prompt}') sobre el prompt: {duration_prompt_action:.4f} segundos.")


            # 6. Opcional: Verificar el resultado en la página después de la interacción
            # Es crucial para confirmar que la acción en el diálogo tuvo el efecto esperado en la UI.
            # Asumo un selector '#demo' y textos específicos, ajusta esto a tu aplicación real.
            # --- Medición de rendimiento: Inicio de verificación del resultado en la página ---
            start_time_post_action_verification = time.time()
            if accion_prompt == 'accept':
                # Ejemplo: Si el texto introducido se muestra en un elemento de la página
                expect(self.page.locator("#demo")).to_have_text(f"You entered: {input_text}")
                self.logger.info(f"\n  ✅  --> Resultado en página: 'You entered: {input_text}' verificado.")
            elif accion_prompt == 'dismiss':
                # Ejemplo: Si se muestra un mensaje de cancelación
                expect(self.page.locator("#demo")).to_have_text("You cancelled the prompt.")
                self.logger.info("\n  ✅  --> Resultado en página: 'You cancelled the prompt.' verificado.")
            
            # --- Medición de rendimiento: Fin de verificación del resultado en la página ---
            end_time_post_action_verification = time.time()
            duration_post_action_verification = end_time_post_action_verification - start_time_post_action_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación del resultado en la página: {duration_post_action_verification:.4f} segundos.")

            self.base.tomar_captura(f"{nombre_base}_prompt_exitosa_{accion_prompt}", directorio)
            self.logger.info(f"\n✅  --> ÉXITO: El prompt se mostró, mensaje verificado, texto introducido y '{accion_prompt}' correctamente.")
            
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (verificación de prompt): {duration_total_operation:.4f} segundos.")

            return True

        except TimeoutError as e:
            # Captura si el selector no está listo o si el prompt no aparece a tiempo, o la verificación post-acción falla.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Tiempo de espera excedido): El elemento '{selector}' no estuvo listo, "
                f"el prompt no apareció/fue detectado a tiempo ({tiempo_espera_elemento}s para elemento, {tiempo_espera_prompt}s para prompt), "
                f"o la verificación del resultado en la página falló.\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_prompt_NO_aparece_timeout", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nTimeout al verificar prompt para selector '{selector}'") from e

        except Error as e:
            # Captura errores específicos de Playwright (ej. click fallido, problemas con el diálogo).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al interactuar con el botón o el prompt.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nError de Playwright al verificar prompt para selector '{selector}'") from e

        except AssertionError as e:
            # Captura las AssertionError lanzadas internamente por la función (acción inválida, tipo de diálogo, mensaje incorrecto).
            self.logger.critical(f"\n❌ FALLO (Validación de Prompt): {e}", exc_info=True)
            # La captura ya se tomó en la lógica interna donde se lanzó el AssertionError
            raise # Re-lanzar la excepción original para que el framework la maneje

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al verificar el prompt.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise AssertionError(f"\nError inesperado al verificar prompt para selector '{selector}'") from e

    # 45- Función para verificar una alerta de tipo 'prompt' utilizando page.on("dialog") con page.once().
    # Este método registra un oyente de eventos para manejar el diálogo antes de hacer clic.
    def verificar_prompt_on_dialog(self, selector: Locator, mensaje_prompt_esperado: str, input_text: Optional[str], accion_prompt: str, nombre_base: str, directorio: str, tiempo_espera_elemento: Union[int, float] = 5.0, tiempo_max_deteccion_prompt: Union[int, float] = 7.0) -> bool:
        """
        Verifica un cuadro de diálogo 'prompt' que aparece después de hacer clic en un selector.
        Utiliza `page.once("dialog", ...)` para esperar de forma asíncrona a que el diálogo aparezca.

        Args:
            selector (Locator): El **Locator de Playwright** del elemento que dispara el prompt.
            mensaje_prompt_esperado (str): El **mensaje esperado** dentro del cuerpo del prompt.
            input_text (Optional[str]): El **texto a introducir** en el prompt si `accion_prompt` es 'accept'.
                                        Debe ser `None` si `accion_prompt` es 'dismiss'.
            accion_prompt (str): La **acción a realizar**: 'accept' o 'dismiss'.
            nombre_base (str): Nombre base para las capturas de pantalla.
            directorio (str): Ruta del directorio para las capturas.
            tiempo_espera_elemento (Union[int, float]): Tiempo máximo para que el selector esté listo.
            tiempo_max_deteccion_prompt (Union[int, float]): Tiempo máximo para que el diálogo aparezca.

        Returns:
            bool: `True` si el prompt fue manejado correctamente.

        Raises:
            AssertionError: Si el elemento no está disponible, el prompt no aparece, el tipo de diálogo es
                            incorrecto, el mensaje no coincide, o el texto de entrada es incorrecto.
        """
        self.logger.info(f"\n--- Ejecutando verificación de prompt con page.once('dialog'): {nombre_base} ---")
        self.logger.info(f"\nVerificando prompt al hacer clic en '{selector}' para '{accion_prompt}'")
        self.logger.info(f"\n  --> Mensaje del prompt esperado: '{mensaje_prompt_esperado}'")
        if accion_prompt == 'accept':
            self.logger.info(f"\n  --> Texto a introducir: '{input_text}'")

        # Resetear el estado para cada ejecución del test
        self._alerta_detectada = False
        self._alerta_mensaje_capturado = ""
        self._alerta_tipo_capturado = ""
        self._alerta_input_capturado = ""

        # Validar la acción y el input_text antes de la operación
        if accion_prompt not in ['accept', 'dismiss']:
            error_msg = f"\n❌ FALLO: Acción de prompt no válida: '{accion_prompt}'. Use 'accept' o 'dismiss'."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_accion_invalida", directorio)
            raise AssertionError(error_msg)
        if accion_prompt == 'accept' and input_text is None:
            error_msg = "\n❌ FALLO: 'input_text' no puede ser None cuando 'accion_prompt' es 'accept'."
            self.logger.error(error_msg)
            self.base.tomar_captura(f"{nombre_base}_input_text_missing", directorio)
            raise AssertionError(error_msg)
        if accion_prompt == 'dismiss' and input_text is not None:
            self.logger.warning("\n⚠️ ADVERTENCIA: 'input_text' se ignora cuando 'accion_prompt' es 'dismiss'.")

        start_time_total_operation = time.time()

        try:
            self.logger.debug("\n--- INICIO del bloque TRY ---")
            
            # 1. Validar visibilidad y habilitación del selector
            self.logger.debug(f"\n  --> Validando visibilidad y habilitación del botón '{selector}' (timeout: {tiempo_espera_elemento}s)...")
            start_time_element_ready = time.time()
            expect(selector).to_be_visible()
            expect(selector).to_be_enabled()
            selector.highlight()
            self.logger.debug("\n  --> Elemento resaltado.")
            self.base.esperar_fijo(0.2)
            end_time_element_ready = time.time()
            duration_element_ready = end_time_element_ready - start_time_element_ready
            self.logger.info(f"PERFORMANCE: Tiempo para que el elemento disparador esté listo: {duration_element_ready:.4f} segundos.")
            self.base.tomar_captura(f"{nombre_base}_elemento_listo_para_prompt", directorio)

            # 2. Establecer el oyente del evento y disparar la acción
            self.logger.debug(f"\n  --> Preparando la espera del evento 'dialog' y haciendo clic en '{selector}'...")
            start_time_click_and_prompt_detection = time.time()

            # El orden es crucial: registrar el oyente antes de hacer clic
            # CORRECCIÓN AQUÍ: Se llama al método _get_prompt_dialog_handler_for_on
            self.page.once("dialog", self._get_prompt_dialog_handler_for_on(input_text, accion_prompt))

            # Hacer clic en el botón que dispara el prompt. Usamos `no_wait_after=True` para prevenir el deadlock.
            self.logger.debug(f"\n  --> Oyente 'dialog' registrado. Haciendo clic en el botón ahora...")
            selector.click(timeout=15000, no_wait_after=True)

            # Esperar a que el listener haya detectado y manejado el prompt. 
            # Se puede usar una espera fija si se sabe que el prompt aparece rápido,
            # o un bucle de polling como en la versión original si es necesario.
            self.logger.debug("\n  --> Esperando a que el prompt sea detectado y manejado por el oyente...")
            self.page.wait_for_timeout(tiempo_max_deteccion_prompt * 1000)

            # 3. Validaciones después de que el oyente ha actuado
            if self._alerta_tipo_capturado != "prompt":
                error_msg = f"\n⚠️ Tipo de diálogo inesperado: '{self._alerta_tipo_capturado}'. Se esperaba 'prompt'."
                self.logger.error(error_msg)
                raise AssertionError(error_msg)

            if mensaje_prompt_esperado not in self._alerta_mensaje_capturado:
                self.tomar_captura(f"{nombre_base}_prompt_mensaje_incorrecto", directorio)
                error_msg = (
                    f"\n❌ FALLO: Mensaje del prompt incorrecto.\n"
                    f"  --> Esperado (contiene): '{mensaje_prompt_esperado}'\n"
                    f"  --> Obtenido: '{self._alerta_mensaje_capturado}'"
                )
                self.logger.error(error_msg)
                raise AssertionError(error_msg)
            
            # 4. Verificar que el texto introducido (si es el caso) se ha guardado correctamente
            if accion_prompt == 'accept' and self._alerta_input_capturado != input_text:
                self.base.tomar_captura(f"{nombre_base}_prompt_input_incorrecto", directorio)
                error_msg = (
                    f"\n❌ FALLO: Texto introducido en el prompt incorrecto.\n"
                    f"  --> Esperado: '{input_text}'\n"
                    f"  --> Obtenido (capturado): '{self._alerta_input_capturado}'"
                )
                self.logger.error(error_msg)
                raise AssertionError(error_msg)

            self.base.tomar_captura(f"{nombre_base}_prompt_exitosa_{accion_prompt}", directorio)
            self.logger.info(f"\n✅  --> ÉXITO: El prompt se mostró, mensaje verificado, y acción '{accion_prompt}' completada correctamente.")
            
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación: {duration_total_operation:.4f} segundos.")
            
            return True

        except Exception as e:
            self.logger.debug("\n--- INICIO del bloque EXCEPT ---")
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO: Ocurrió un error inesperado al verificar el prompt.\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise AssertionError(f"Error inesperado al verificar prompt para selector '{selector}'") from e