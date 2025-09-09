import time
from typing import Union
from playwright.sync_api import Page, Locator, expect, Error, TimeoutError

class KeyboardActions:
    def __init__(self, base_page):
        self.base = base_page
        self.page: Page = base_page.page
        self.logger = base_page.logger
        
    # 55- Función para presionar la tecla TAB en el teclado
    # Integra pruebas de rendimiento para medir el tiempo de ejecución de la acción.
    def presionar_tecla_tab(self, tiempo_espera_post_tab: float = 0.5, nombre_paso: str = "") -> None:
        """
        Simula la acción de presionar la tecla 'TAB' en el teclado.
        Esta función es útil para navegar entre elementos interactivos (inputs, botones, enlaces)
        en una página web, moviendo el foco al siguiente elemento tabulable.
        Integra mediciones de rendimiento para la operación.

        Args:
            tiempo_espera_post_tab (float, opcional): Tiempo en segundos para esperar *después* de presionar 'TAB'.
                                                      Útil para dar tiempo a que la UI procese el cambio de foco
                                                      o se carguen elementos dinámicamente. Por defecto `0.5` segundos.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para los logs. Por defecto "".

        Raises:
            Exception: Si ocurre algún error inesperado durante la simulación de la tecla TAB.
        """
        self.logger.info(f"\n--- {nombre_paso}: Presionando la tecla TAB y esperando {tiempo_espera_post_tab} segundos ---")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # --- Medición de rendimiento: Inicio de la acción 'keyboard.press' ---
            start_time_press_action = time.time()
            self.page.keyboard.press("Tab")
            # --- Medición de rendimiento: Fin de la acción 'keyboard.press' ---
            end_time_press_action = time.time()
            duration_press_action = end_time_press_action - start_time_press_action
            self.logger.info(f"PERFORMANCE: Tiempo de la acción 'keyboard.press(\"Tab\")': {duration_press_action:.4f} segundos.")
            
            self.logger.info("\nTecla TAB presionada exitosamente.")

            # Espera fija después de presionar TAB (configuracion por parametro)
            if tiempo_espera_post_tab > 0:
                self.base.esperar_fijo(tiempo_espera_post_tab)

        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado) - {nombre_paso}: Ocurrió un error inesperado al presionar la tecla TAB.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            # En este caso, una captura de pantalla podría no ser tan útil,
            # ya que es una acción de teclado global, pero se podría añadir
            # si el contexto lo amerita (e.g., para ver el estado del foco).
            # self.tomar_captura(f"error_tab_press", "directorio_errores") # Descomentar si se desea una captura
            raise AssertionError(f"\nError al presionar la tecla TAB: {e}") from e
        finally:
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (Tab_Press): {duration_total_operation:.4f} segundos.")
    
    # 74- Función para presionar la tecla TAB y verificar que el foco cambie al elemento esperado.
    # Combina la acción de TAB con una validación directa del foco, aceptando tanto selectores como objetos Locator.
    def presionar_tab_y_verificar_foco(self, selector_o_locator_esperado: Union[str, Locator], nombre_base: str, direccion: str, tiempo_espera_post_tab: float = 0.5, nombre_paso: str = "") -> None:
        """
        Simula la acción de presionar la tecla 'TAB' y verifica que el foco del navegador
        se mueva al elemento especificado, **resaltando el elemento de destino** para
        confirmación visual en la captura de pantalla o durante la ejecución.

        Esta función es flexible, ya que puede recibir el selector del elemento
        como una cadena de texto (str) o como un objeto Locator de Playwright.

        Args:
            selector_o_locator_esperado (str | Locator): El selector del elemento (str)
                                                        o el objeto Locator (Locator) que se espera
                                                        que reciba el foco después de presionar 'TAB'.
                                                        Ejemplo: '#input-contrasena' o self.page.locator('#input-contrasena').
            nombre_base (str): Nombre base para las capturas de pantalla en caso de error.
            direccion (str): Directorio donde se guardarán las capturas de pantalla.
            tiempo_espera_post_tab (float, opcional): Tiempo en segundos para esperar después de presionar 'TAB'.
                                                    Por defecto `0.5` segundos.
            nombre_paso (str, opcional): Descripción del paso para los logs. Por defecto "".

        Raises:
            AssertionError: Si el foco no se encuentra en el elemento esperado.
            Exception: Si ocurre un error inesperado.
        """
        # 1. Convertir el selector o el Locator a un objeto Locator.
        if isinstance(selector_o_locator_esperado, str):
            localizador = self.page.locator(selector_o_locator_esperado)
        else:
            localizador = selector_o_locator_esperado

        paso_descripcion = nombre_paso if nombre_paso else f"Verificando el cambio de foco a '{localizador}' después de presionar TAB."
        self.logger.info(f"\n--- {paso_descripcion} ---")

        try:
            # 2. Resaltar el elemento esperado para una confirmación visual.
            self.logger.info(f"✨ Resaltando el elemento esperado para el foco: '{localizador}'...")
            localizador.highlight()
            
            # 3. Presionar la tecla TAB utilizando la función existente.
            self.presionar_tecla_tab(tiempo_espera_post_tab=tiempo_espera_post_tab, nombre_paso="Presionando TAB para cambiar de foco")
            
            # 4. La verificación clave con `expect` para asegurar que el foco se movió correctamente.
            expect(localizador).to_be_focused()
            
            self.logger.info(f"\n✅ ÉXITO - El foco se encuentra en el elemento esperado: '{localizador}'.")

        except AssertionError as ae:
            mensaje_error = f"\n❌ FALLO de Verificación - {paso_descripcion}\n{ae}"
            self.logger.error(mensaje_error)
            self.base.tomar_captura(f"{nombre_base}_foco_fallido", direccion)
            raise ae
        except Exception as e:
            mensaje_error = (
                f"\n❌ FALLO (Inesperado) - {paso_descripcion}: Ocurrió un error inesperado durante la verificación.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", direccion)
            raise AssertionError(f"\nError inesperado al verificar el foco: {e}") from e
                
    # 75- Función para presionar la combinación de teclas SHIFT + TAB en el teclado
    # Integra pruebas de rendimiento para medir el tiempo de ejecución de la acción.
    def presionar_shift_tab(self, tiempo_espera_post_shift_tab: float = 0.5, nombre_paso: str = "") -> None:
        """
        Simula la acción de presionar la combinación de teclas 'Shift + Tab' en el teclado.
        Esta función es útil para navegar *hacia atrás* entre elementos interactivos (inputs,
        botones, enlaces) en una página web, moviendo el foco al elemento tabulable anterior.
        Integra mediciones de rendimiento para la operación.

        Args:
            tiempo_espera_post_shift_tab (float, opcional): Tiempo en segundos para esperar *después*
                                                            de presionar 'Shift + Tab'. Útil para dar
                                                            tiempo a que la UI procese el cambio de foco
                                                            o se carguen elementos dinámicamente. Por defecto
                                                            `0.5` segundos.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para los logs.
                                        Por defecto "".

        Raises:
            Exception: Si ocurre algún error inesperado durante la simulación de la combinación de teclas.
        """
        self.logger.info(f"\n--- {nombre_paso}: Presionando la combinación de teclas SHIFT + TAB y esperando {tiempo_espera_post_shift_tab} segundos ---")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # --- Medición de rendimiento: Inicio de la acción 'keyboard.press' ---
            start_time_press_action = time.time()
            self.page.keyboard.press("Shift+Tab")
            # --- Medición de rendimiento: Fin de la acción 'keyboard.press' ---
            end_time_press_action = time.time()
            duration_press_action = end_time_press_action - start_time_press_action
            self.logger.info(f"\nPERFORMANCE: Tiempo de la acción 'keyboard.press(\"Shift+Tab\")': {duration_press_action:.4f} segundos.")
            
            self.logger.info("\nCombinación de teclas SHIFT + TAB presionada exitosamente.")

            # Espera fija después de presionar SHIFT + TAB (configuracion por parametro)
            if tiempo_espera_post_shift_tab > 0:
                self.base.esperar_fijo(tiempo_espera_post_shift_tab)

        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado) - {nombre_paso}: Ocurrió un error inesperado al presionar la combinación de teclas SHIFT + TAB.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            # Se lanza la excepción para que el framework de pruebas maneje el fallo.
            raise AssertionError(f"\nError al presionar la combinación de teclas SHIFT + TAB: {e}") from e
        finally:
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"\nPERFORMANCE: Tiempo total de la operación (Shift_Tab_Press): {duration_total_operation:.4f} segundos.")
    
    # 76- Función para presionar la combinación de teclas SHIFT + TAB y verificar que el foco cambie al elemento esperado.
    # Combina la acción de SHIFT + TAB con una validación directa del foco, aceptando
    # selectores o objetos Locator.
    def presionar_shift_tab_y_verificar_foco(self, selector_o_locator_esperado: Union[str, Locator], nombre_base: str, direccion: str, tiempo_espera_post_shift_tab: float = 0.5, nombre_paso: str = "") -> None:
        """
        Simula la acción de presionar la combinación de teclas 'Shift + Tab' y verifica
        que el foco del navegador se mueva al elemento especificado, **resaltando el elemento de destino** para
        confirmación visual en la captura de pantalla o durante la ejecución.

        Esta función es flexible, ya que puede recibir el selector del elemento
        como una cadena de texto (str) o como un objeto Locator de Playwright.

        Args:
            selector_o_locator_esperado (str | Locator): El selector del elemento (str) o
                                                        el objeto Locator (Locator) que se espera
                                                        que reciba el foco después de presionar
                                                        'Shift + Tab'.
                                                        Ejemplo: '#input-contrasena' o self.page.locator('#input-contrasena').
            nombre_base (str): Nombre base para las capturas de pantalla en caso de error.
            direccion (str): Directorio donde se guardarán las capturas de pantalla.
            tiempo_espera_post_shift_tab (float, opcional): Tiempo en segundos para esperar después de presionar
                                                            'Shift + Tab'. Por defecto `0.5` segundos.
            nombre_paso (str, opcional): Descripción del paso para los logs. Por defecto "".

        Raises:
            AssertionError: Si el foco no se encuentra en el elemento esperado.
            Exception: Si ocurre un error inesperado.
        """
        # 1. Convertir el selector o el Locator a un objeto Locator.
        if isinstance(selector_o_locator_esperado, str):
            localizador = self.page.locator(selector_o_locator_esperado)
        else:
            localizador = selector_o_locator_esperado

        paso_descripcion = nombre_paso if nombre_paso else f"Verificando el cambio de foco a '{localizador}' después de presionar SHIFT + TAB."
        self.logger.info(f"\n--- {paso_descripcion} ---")

        try:
            self.logger.info(f"✨ Resaltando el elemento esperado para el foco: '{localizador}'...")
            localizador.highlight()
            # 2. Presionar la combinación de teclas SHIFT + TAB utilizando la función existente.
            self.presionar_shift_tab(tiempo_espera_post_shift_tab=tiempo_espera_post_shift_tab, nombre_paso="Presionando SHIFT + TAB para cambiar de foco")

            # 3. Resaltar el elemento esperado para una confirmación visual.
            self.logger.info(f"\nVerificando que el foco se haya movido al elemento: '{localizador}'...")
            
            # 4. La verificación clave con `expect` de Playwright.
            #    `to_be_focused()` verifica si el elemento actualmente tiene el foco.
            expect(localizador).to_be_focused()
            
            self.logger.info(f"\n✅ ÉXITO - El foco se encuentra en el elemento esperado: '{localizador}'.")

        except AssertionError as ae:
            mensaje_error = f"\n❌ FALLO de Verificación - {paso_descripcion}\n{ae}"
            self.logger.error(mensaje_error)
            self.tomar_captura(f"{nombre_base}_foco_fallido", direccion)
            raise ae
        except Exception as e:
            mensaje_error = (
                f"\n❌ FALLO (Inesperado) - {paso_descripcion}: Ocurrió un error inesperado durante la verificación.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.tomar_captura(f"{nombre_base}_error_inesperado", direccion)
            raise AssertionError(f"\nError inesperado al verificar el foco: {e}") from e