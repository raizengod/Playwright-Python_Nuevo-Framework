import time
from typing import Union, Optional, Dict, Any, List
from playwright.sync_api import Page, Locator, expect, Error, TimeoutError

class DropdownActions:
    def __init__(self, base_page):
        self.base = base_page
        self.page: Page = base_page.page
        self.logger = base_page.logger
        
        # 53- Función para seleccionar una opción en un ComboBox (elemento <select>) por su atributo 'value'.
    # Integra pruebas de rendimiento para las fases de validación, selección y verificación.
    def seleccionar_opcion_por_valor(self, combobox_locator: Locator, valor_a_seleccionar: str, nombre_base: str, directorio: str, nombre_paso: str = "", timeout_ms: int = 15000) -> None:
        """
        Selecciona una opción dentro de un elemento ComboBox (`<select>`) utilizando su atributo 'value'.
        La función valida la visibilidad y habilitación del ComboBox, realiza la selección y
        verifica que la opción haya sido aplicada correctamente.
        Integra mediciones de rendimiento para cada fase de la operación.

        Args:
            combobox_locator (Locator): El **Locator** del elemento `<select>` (ComboBox).
            valor_a_seleccionar (str): El **valor del atributo 'value'** de la opción `<option>` que se desea seleccionar.
            nombre_base (str): Nombre base para las **capturas de pantalla** tomadas durante la ejecución.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para los logs y nombres de capturas. Por defecto "".
            timeout_ms (int, opcional): Tiempo máximo en milisegundos para esperar la visibilidad,
                                        habilitación y verificación de la selección. Por defecto `15000`ms (15 segundos).

        Raises:
            AssertionError: Si el ComboBox no es visible/habilitado, la opción no se puede seleccionar,
                            la selección no se verifica correctamente o si ocurre un error inesperado.
        """
        self.logger.info(f"\n--- {nombre_paso}: Iniciando selección de '{valor_a_seleccionar}' en ComboBox por valor: '{combobox_locator}' ---")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Asegurarse de que el ComboBox esté visible y habilitado
            self.logger.info(f"\n🔍 Esperando que el ComboBox '{combobox_locator}' sea visible y habilitado...")
            # --- Medición de rendimiento: Inicio validación/espera ---
            start_time_validation = time.time()
            expect(combobox_locator).to_be_visible()
            combobox_locator.highlight() # Para visualización durante la ejecución
            expect(combobox_locator).to_be_enabled()
            # --- Medición de rendimiento: Fin validación/espera ---
            end_time_validation = time.time()
            duration_validation = end_time_validation - start_time_validation
            self.logger.info(f"PERFORMANCE: Tiempo de validación de visibilidad y habilitación: {duration_validation:.4f} segundos.")
            
            self.logger.info(f"\n✅ ComboBox '{combobox_locator}' es visible y habilitado.")
            
            # 2. Tomar captura antes de la selección
            self.base.tomar_captura(f"{nombre_base}_antes_de_seleccionar_combo", directorio)

            # 3. Seleccionar la opción por su valor
            self.logger.info(f"\n🔄 Seleccionando opción '{valor_a_seleccionar}' en '{combobox_locator}'...")
            # --- Medición de rendimiento: Inicio selección ---
            start_time_selection = time.time()
            combobox_locator.select_option(value=valor_a_seleccionar, timeout=timeout_ms) # Asegúrate de pasar el 'value=' explícitamente si es necesario
            # --- Medición de rendimiento: Fin selección ---
            end_time_selection = time.time()
            duration_selection = end_time_selection - start_time_selection
            self.logger.info(f"PERFORMANCE: Tiempo de selección de la opción: {duration_selection:.4f} segundos.")
            
            self.logger.info(f"\n✅ Opción '{valor_a_seleccionar}' seleccionada exitosamente en '{combobox_locator}'.")

            # 4. Verificar que la opción fue seleccionada correctamente
            self.logger.info(f"\n🔍 Verificando que ComboBox '{combobox_locator}' tenga el valor '{valor_a_seleccionar}'...")
            # --- Medición de rendimiento: Inicio verificación ---
            start_time_verification = time.time()
            expect(combobox_locator).to_have_value(valor_a_seleccionar, timeout=timeout_ms)
            # --- Medición de rendimiento: Fin verificación ---
            end_time_verification = time.time()
            duration_verification = end_time_verification - start_time_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación de la selección: {duration_verification:.4f} segundos.")
            
            self.logger.info(f"\n✅ ComboBox '{combobox_locator}' verificado con valor '{valor_a_seleccionar}'.")

            # 5. Tomar captura después de la selección exitosa
            self.base.tomar_captura(f"{nombre_base}_despues_de_seleccionar_combo_exito", directorio)
            
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (seleccionar ComboBox): {duration_total_operation:.4f} segundos.")

        except TimeoutError as e:
            # Captura TimeoutError específicamente para mensajes más claros
            mensaje_error = (
                f"\n❌ FALLO (Timeout) - {nombre_paso}: El ComboBox '{combobox_locator}' "
                f"no se volvió visible/habilitado o la opción '{valor_a_seleccionar}' no se pudo seleccionar/verificar a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_combo", directorio)
            raise AssertionError(mensaje_error) from e

        except Error as e:
            # Captura otros errores de Playwright
            mensaje_error = (
                f"\n❌ FALLO (Error de Playwright) - {nombre_paso}: Ocurrió un error de Playwright al intentar seleccionar la opción '{valor_a_seleccionar}' en '{combobox_locator}'.\n"
                f"Posibles causas: Selector inválido, elemento no es un <select>, opción no existe, o ComboBox no interactuable.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_playwright_error_combo", directorio)
            raise AssertionError(mensaje_error) from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada
            mensaje_error = (
                f"\n❌ FALLO (Error Inesperado) - {nombre_paso}: Ocurrió un error desconocido al manejar el ComboBox '{combobox_locator}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_inesperado_combo", directorio)
            raise AssertionError(mensaje_error) from e
        
    # 54- Función para seleccionar una opción en un ComboBox (elemento <select>) por su texto visible (label).
    # Integra pruebas de rendimiento para las fases de validación, selección y verificación.
    def seleccionar_opcion_por_label(self, combobox_locator: Locator, label_a_seleccionar: str, nombre_base: str, directorio: str, value_esperado: Optional[str] = None, nombre_paso: str = "", timeout_ms: int = 15000) -> None:
        """
        Selecciona una opción dentro de un elemento ComboBox (`<select>`) utilizando su texto visible (label).
        La función valida la visibilidad y habilitación del ComboBox, realiza la selección y
        verifica que la opción haya sido aplicada correctamente, ya sea por su 'value' esperado
        o asumiendo que el 'value' es igual al 'label'.
        Integra mediciones de rendimiento para cada fase de la operación.

        Args:
            combobox_locator (Locator): El **Locator** del elemento `<select>` (ComboBox).
            label_a_seleccionar (str): El **texto visible (label)** de la opción `<option>` que se desea seleccionar.
            nombre_base (str): Nombre base para las **capturas de pantalla** tomadas durante la ejecución.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            value_esperado (str, opcional): El **valor del atributo 'value'** que se espera que tenga el ComboBox
                                            después de seleccionar la opción por su label. Si no se proporciona,
                                            se asume que `value_esperado` es igual a `label_a_seleccionar`.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para los logs y nombres de capturas. Por defecto "".
            timeout_ms (int, opcional): Tiempo máximo en milisegundos para esperar la visibilidad,
                                        habilitación y verificación de la selección. Por defecto `15000`ms (15 segundos).

        Raises:
            AssertionError: Si el ComboBox no es visible/habilitado, la opción no se puede seleccionar,
                            la selección no se verifica correctamente o si ocurre un error inesperado.
        """
        self.logger.info(f"\n--- {nombre_paso}: Iniciando selección de '{label_a_seleccionar}' en ComboBox por label: '{combobox_locator}' ---")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Asegurarse de que el ComboBox esté visible y habilitado
            self.logger.info(f"\n🔍 Esperando que el ComboBox '{combobox_locator}' sea visible y habilitado...")
            # --- Medición de rendimiento: Inicio validación/espera ---
            start_time_validation = time.time()
            expect(combobox_locator).to_be_visible()
            combobox_locator.highlight() # Para visualización durante la ejecución
            expect(combobox_locator).to_be_enabled()
            # --- Medición de rendimiento: Fin validación/espera ---
            end_time_validation = time.time()
            duration_validation = end_time_validation - start_time_validation
            self.logger.info(f"PERFORMANCE: Tiempo de validación de visibilidad y habilitación: {duration_validation:.4f} segundos.")
            
            self.logger.info(f"\n✅ ComboBox '{combobox_locator}' es visible y habilitado.")
            
            # 2. Tomar captura antes de la selección
            self.base.tomar_captura(f"{nombre_base}_antes_de_seleccionar_combo_label", directorio)

            # 3. Seleccionar la opción por su texto visible (label)
            self.logger.info(f"\n🔄 Seleccionando opción con texto '{label_a_seleccionar}' en '{combobox_locator}'...")
            # --- Medición de rendimiento: Inicio selección ---
            start_time_selection = time.time()
            # El método select_option() espera automáticamente a que el elemento
            # sea visible, habilitado y con la opción disponible.
            combobox_locator.select_option(label=label_a_seleccionar) # Usa 'label=' para claridad
            # --- Medición de rendimiento: Fin selección ---
            end_time_selection = time.time()
            duration_selection = end_time_selection - start_time_selection
            self.logger.info(f"PERFORMANCE: Tiempo de selección de la opción por label: {duration_selection:.4f} segundos.")
            
            self.logger.info(f"\n✅ Opción '{label_a_seleccionar}' seleccionada exitosamente en '{combobox_locator}' por label.")

            # 4. Verificar que la opción fue seleccionada correctamente
            # Usamos to_have_value() para asegurar que el valor del select cambió al esperado.
            # Esto es más robusto que to_have_text() para <select>, ya que el texto visible puede variar
            # o incluir espacios, mientras que el 'value' es el dato real subyacente.
            valor_para_comparar_verificacion = value_esperado if value_esperado is not None else label_a_seleccionar
            
            self.logger.info(f"\n🔍 Verificando que ComboBox '{combobox_locator}' tenga el valor esperado '{valor_para_comparar_verificacion}'...")
            # --- Medición de rendimiento: Inicio verificación ---
            start_time_verification = time.time()
            expect(combobox_locator).to_have_value(valor_para_comparar_verificacion)
            # --- Medición de rendimiento: Fin verificación ---
            end_time_verification = time.time()
            duration_verification = end_time_verification - start_time_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación de la selección: {duration_verification:.4f} segundos.")
            
            self.logger.info(f"\n✅ ComboBox '{combobox_locator}' verificado con valor seleccionado '{valor_para_comparar_verificacion}'.")

            # 5. Tomar captura después de la selección exitosa
            # Asegura que la captura refleje el estado final y el valor seleccionado
            self.base.tomar_captura(f"{nombre_base}_despues_de_seleccionar_combo_label_exito", directorio)
            
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (seleccionar ComboBox por label): {duration_total_operation:.4f} segundos.")

        except TimeoutError as e:
            mensaje_error = (
                f"\n❌ FALLO (Timeout) - {nombre_paso}: El ComboBox '{combobox_locator}' "
                f"no se volvió visible/habilitado o la opción con label '{label_a_seleccionar}' no se pudo seleccionar/verificar a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_combo_label", directorio)
            raise AssertionError(mensaje_error) from e

        except Error as e:
            mensaje_error = (
                f"\n❌ FALLO (Error de Playwright) - {nombre_paso}: Ocurrió un error al intentar seleccionar la opción con label '{label_a_seleccionar}' en '{combobox_locator}'.\n"
                f"Posibles causas: Selector inválido, elemento no es un <select>, opción con ese label no existe, o ComboBox no interactuable.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_playwright_error_combo_label", directorio)
            raise AssertionError(mensaje_error) from e

        except Exception as e:
            mensaje_error = (
                f"\n❌ FALLO (Error Inesperado) - {nombre_paso}: Ocurrió un error desconocido al manejar el ComboBox '{combobox_locator}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_inesperado_combo_label", directorio)
            raise AssertionError(mensaje_error) from e
            
    # 56- Función optimizada para seleccionar múltiples opciones en un ComboBox múltiple.
    # Integra pruebas de rendimiento utilizando mediciones de tiempo para cada fase clave.
    def seleccionar_multiples_opciones_combo(self, combobox_multiple_locator: Locator, valores_a_seleccionar: List[str], nombre_base: str, directorio: str, nombre_paso: str = "", timeout_ms: int = 15000) -> None:
        """
        Selecciona múltiples opciones en un ComboBox (`<select multiple>`) por sus valores o labels.
        La función valida la visibilidad y habilitación del ComboBox, realiza la selección de
        todas las opciones especificadas y verifica que todas ellas hayan sido aplicadas correctamente.
        Integra mediciones de rendimiento detalladas para cada fase de la operación.

        Args:
            combobox_multiple_locator (Locator): El **Locator** del elemento `<select multiple>` (ComboBox múltiple).
            valores_a_seleccionar (List[str]): Una **lista de cadenas** que representan los 'value' o 'label'
                                              de las opciones que se desean seleccionar.
            nombre_base (str): Nombre base para las **capturas de pantalla** tomadas durante la ejecución.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para los logs y nombres de capturas. Por defecto "".
            timeout_ms (int, opcional): Tiempo máximo en milisegundos para esperar la visibilidad,
                                        habilitación y verificación de la selección. Por defecto `15000`ms (15 segundos).

        Raises:
            AssertionError: Si el ComboBox no es visible/habilitado, las opciones no se pueden seleccionar,
                            la verificación de las selecciones falla o si ocurre un error inesperado.
        """
        self.logger.info(f"\n--- {nombre_paso}: Iniciando selección de múltiples opciones {valores_a_seleccionar} en ComboBox: '{combobox_multiple_locator}' ---")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Asegurarse de que el ComboBox esté visible y habilitado
            self.logger.info(f"\n🔍 Esperando que el ComboBox múltiple '{combobox_multiple_locator}' sea visible y habilitado...")
            # --- Medición de rendimiento: Inicio validación/espera ---
            start_time_validation = time.time()
            expect(combobox_multiple_locator).to_be_visible()
            combobox_multiple_locator.highlight() # Para visualización durante la ejecución
            expect(combobox_multiple_locator).to_be_enabled()
            # --- Medición de rendimiento: Fin validación/espera ---
            end_time_validation = time.time()
            duration_validation = end_time_validation - start_time_validation
            self.logger.info(f"PERFORMANCE: Tiempo de validación de visibilidad y habilitación: {duration_validation:.4f} segundos.")
            
            self.logger.info(f"\n✅ ComboBox múltiple '{combobox_multiple_locator}' es visible y habilitado.")
            
            # Opcional: Verificar que sea un select múltiple.
            # Esta aserción es útil para fallar temprano si el locator no apunta al tipo de elemento correcto.
            self.logger.debug(f"\nVerificando que '{combobox_multiple_locator}' sea un <select multiple>...")
            expect(combobox_multiple_locator).to_have_attribute("multiple") # El atributo 'multiple' existe
            self.logger.debug("\n  > ComboBox verificado como select múltiple.")

            # 2. Tomar captura antes de la selección
            self.base.tomar_captura(f"{nombre_base}_antes_de_seleccionar_multi_combo", directorio)

            # 3. Seleccionar las opciones
            self.logger.info(f"\n🔄 Seleccionando opciones '{valores_a_seleccionar}' en '{combobox_multiple_locator}'...")
            # --- Medición de rendimiento: Inicio selección de múltiples opciones ---
            start_time_selection = time.time()
            # Playwright's select_option() para listas maneja tanto valores como labels.
            # Pasando una lista de strings seleccionará las opciones correspondientes.
            combobox_multiple_locator.select_option(valores_a_seleccionar)
            # --- Medición de rendimiento: Fin selección de múltiples opciones ---
            end_time_selection = time.time()
            duration_selection = end_time_selection - start_time_selection
            self.logger.info(f"PERFORMANCE: Tiempo de selección de las múltiples opciones: {duration_selection:.4f} segundos.")
            
            self.logger.info(f"\n✅ Opciones '{valores_a_seleccionar}' seleccionadas exitosamente en '{combobox_multiple_locator}'.")

            # 4. Verificar que las opciones fueron seleccionadas correctamente
            self.logger.info(f"\n🔍 Verificando que ComboBox múltiple '{combobox_multiple_locator}' tenga los valores seleccionados: {valores_a_seleccionar}...")
            # --- Medición de rendimiento: Inicio verificación de selecciones ---
            start_time_verification = time.time()
            # to_have_values() es la aserción correcta para verificar múltiples selecciones por su 'value'.
            expect(combobox_multiple_locator).to_have_values(valores_a_seleccionar)
            # --- Medición de rendimiento: Fin verificación de selecciones ---
            end_time_verification = time.time()
            duration_verification = end_time_verification - start_time_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación de las selecciones: {duration_verification:.4f} segundos.")
            
            self.logger.info(f"\n✅ ComboBox múltiple '{combobox_multiple_locator}' verificado con valores seleccionados: {valores_a_seleccionar}.")

            # 5. Tomar captura después de la selección exitosa
            self.base.tomar_captura(f"{nombre_base}_despues_de_seleccionar_multi_combo_exito", directorio)
            
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (seleccionar ComboBox múltiple): {duration_total_operation:.4f} segundos.")

        except TimeoutError as e:
            mensaje_error = (
                f"\n❌ FALLO (Timeout) - {nombre_paso}: El ComboBox múltiple '{combobox_multiple_locator}' "
                f"no se volvió visible/habilitado o las opciones '{valores_a_seleccionar}' no se pudieron seleccionar/verificar a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_timeout_multi_combo", directorio)
            raise AssertionError(mensaje_error) from e

        except Error as e:
            mensaje_error = (
                f"\n❌ FALLO (Error de Playwright) - {nombre_paso}: Ocurrió un error al intentar seleccionar las opciones '{valores_a_seleccionar}' en '{combobox_multiple_locator}'.\n"
                f"Posibles causas: Selector inválido, elemento no es un <select multiple>, alguna opción no existe o el ComboBox no es interactuable.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_playwright_error_multi_combo", directorio)
            raise AssertionError(mensaje_error) from e

        except Exception as e:
            mensaje_error = (
                f"\n❌ FALLO (Error Inesperado) - {nombre_paso}: Ocurrió un error desconocido al manejar el ComboBox múltiple '{combobox_multiple_locator}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_inesperado_multi_combo", directorio)
            raise AssertionError(mensaje_error) from e
        
    # 57- Función que obtiene y imprime los valores y el texto de todas las opciones en un dropdown list.
    # Integra pruebas de rendimiento para medir el tiempo de extracción de datos del dropdown.
    def obtener_valores_dropdown(self, selector_dropdown: Locator, nombre_base: str, directorio: str, nombre_paso: str = "", timeout_ms: int = 15000) -> Optional[List[Dict[str, str]]]:
        """
        Obtiene los atributos 'value' y el texto visible de todas las opciones (`<option>`)
        dentro de un elemento dropdown (`<select>`).
        La función valida la visibilidad y habilitación del dropdown antes de extraer los datos.
        Integra mediciones de rendimiento para cada fase clave de la extracción.

        Args:
            selector_dropdown (Locator): El **Locator** del elemento `<select>` (dropdown list).
            nombre_base (str): Nombre base para las **capturas de pantalla** tomadas durante la ejecución.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para los logs y nombres de capturas. Por defecto "".
            timeout_ms (int, opcional): Tiempo máximo en milisegundos para esperar la visibilidad
                                        y habilitación del dropdown. Por defecto `15000`ms (15 segundos).

        Returns:
            Optional[List[Dict[str, str]]]: Una lista de diccionarios, donde cada diccionario contiene
                                           'value' y 'text' de una opción. Retorna `None` si no se
                                           encuentran opciones.

        Raises:
            AssertionError: Si el dropdown no es visible/habilitado, o si ocurre un error inesperado
                            durante la extracción de los datos.
        """
        self.logger.info(f"\n--- {nombre_paso}: Extrayendo valores del dropdown '{selector_dropdown}' ---")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()
        valores_opciones: List[Dict[str, str]] = []

        try:
            # 1. Asegurar que el dropdown es visible y habilitado
            self.logger.info(f"\n🔍 Esperando que el dropdown '{selector_dropdown}' sea visible y habilitado...")
            # --- Medición de rendimiento: Inicio validación/espera ---
            start_time_validation = time.time()
            expect(selector_dropdown).to_be_visible()
            selector_dropdown.highlight() # Para visualización durante la ejecución
            expect(selector_dropdown).to_be_enabled()
            # --- Medición de rendimiento: Fin validación/espera ---
            end_time_validation = time.time()
            duration_validation = end_time_validation - start_time_validation
            self.logger.info(f"PERFORMANCE: Tiempo de validación de visibilidad y habilitación del dropdown: {duration_validation:.4f} segundos.")
            
            self.logger.info(f"\n✅ Dropdown '{selector_dropdown}' es visible y habilitado.")
            self.base.tomar_captura(f"{nombre_base}_dropdown_antes_extraccion", directorio)

            # 2. Obtener todos los locators de las opciones dentro del dropdown
            self.logger.info(f"\n🔄 Obteniendo locators de todas las opciones dentro de '{selector_dropdown}'...")
            # --- Medición de rendimiento: Inicio obtención de option locators ---
            start_time_get_options = time.time()
            option_locators = selector_dropdown.locator("option").all()
            # --- Medición de rendimiento: Fin obtención de option locators ---
            end_time_get_options = time.time()
            duration_get_options = end_time_get_options - start_time_get_options
            self.logger.info(f"PERFORMANCE: Tiempo de obtención de todos los option locators: {duration_get_options:.4f} segundos.")

            if not option_locators:
                self.logger.warning(f"\n⚠️ No se encontraron opciones dentro del dropdown '{selector_dropdown}'.")
                self.base.tomar_captura(f"{nombre_base}_dropdown_sin_opciones", directorio)
                return None

            self.logger.info(f"\n Encontradas {len(option_locators)} opciones para '{selector_dropdown}':")

            # 3. Iterar sobre cada opción y extraer su 'value' y 'text_content'
            self.logger.info("\n📊 Extrayendo valores y textos de cada opción...")
            # --- Medición de rendimiento: Inicio iteración y extracción ---
            start_time_extract_loop = time.time()
            for i, option_locator in enumerate(option_locators):
                value = option_locator.get_attribute("value")
                text = option_locator.text_content()

                # Limpieza de espacios en blanco
                clean_value = value.strip() if value is not None else "" # Manejo de None para get_attribute
                clean_text = text.strip() if text is not None else "" # Manejo de None para text_content

                valores_opciones.append({'value': clean_value, 'text': clean_text})
                self.logger.info(f"  Opción {i+1}: Value='{clean_value}', Text='{clean_text}'")
            # --- Medición de rendimiento: Fin iteración y extracción ---
            end_time_extract_loop = time.time()
            duration_extract_loop = end_time_extract_loop - start_time_extract_loop
            self.logger.info(f"PERFORMANCE: Tiempo de iteración y extracción de {len(option_locators)} opciones: {duration_extract_loop:.4f} segundos.")


            self.logger.info(f"\n✅ Valores obtenidos exitosamente del dropdown '{selector_dropdown}'.")
            self.base.tomar_captura(f"{nombre_base}_dropdown_valores_extraidos", directorio)
            return valores_opciones

        except TimeoutError as e:
            mensaje_error = (
                f"\n❌ FALLO (Timeout) - {nombre_paso}: El dropdown '{selector_dropdown}' "
                f"no se volvió visible/habilitado o sus opciones no cargaron a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_dropdown_fallo_timeout", directorio)
            raise AssertionError(mensaje_error) from e

        except Error as e:
            mensaje_error = (
                f"\n❌ FALLO (Error de Playwright) - {nombre_paso}: Ocurrió un error de Playwright al intentar obtener los valores del dropdown '{selector_dropdown}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_dropdown_fallo_playwright_error", directorio)
            raise AssertionError(mensaje_error) from e

        except Exception as e:
            mensaje_error = (
                f"\n❌ FALLO (Error Inesperado) - {nombre_paso}: Ocurrió un error desconocido al intentar obtener los valores del dropdown '{selector_dropdown}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_dropdown_fallo_inesperado", directorio)
            raise AssertionError(mensaje_error) from e
        finally:
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (obtener valores dropdown): {duration_total_operation:.4f} segundos.")
        
    # 58- Función que obtiene y compara los valores y el texto de todas las opciones en un dropdown list.
    # Integra pruebas de rendimiento para medir el tiempo de extracción y comparación de datos.
    def obtener_y_comparar_valores_dropdown(self, dropdown_locator: Locator, nombre_base: str, directorio: str, expected_options: Optional[List[Union[str, Dict[str, str]]]] = None, compare_by_text: bool = True, compare_by_value: bool = False, nombre_paso: str = "", timeout_ms: int = 15000) -> Optional[List[Dict[str, str]]]:
        """
        Obtiene los atributos 'value' y el texto visible de todas las opciones (`<option>`)
        dentro de un elemento dropdown (`<select>`). Opcionalmente, compara las opciones obtenidas
        con una lista de opciones esperadas.
        La función valida la visibilidad y habilitación del dropdown y mide el rendimiento
        de la extracción y, si aplica, de la comparación.

        Args:
            dropdown_locator (Locator): El **Locator** de Playwright para el elemento `<select>` del dropdown.
            nombre_base (str): Nombre base para las **capturas de pantalla**.
            directorio (str): Directorio donde se guardarán las **capturas de pantalla**.
            expected_options (List[Union[str, Dict[str, str]]], optional):
                Lista de opciones esperadas para la comparación. Puede ser:
                - `List[str]`: Si solo se desea comparar por el texto visible de las opciones.
                - `List[Dict[str, str]]`: Si se desea comparar por 'value' y 'text'.
                  Ej: `[{'value': 'usa', 'text': 'Estados Unidos'}]`.
                Por defecto es `None` (no se realiza comparación).
            compare_by_text (bool): Si es `True`, compara el texto visible de las opciones.
                                  Usado si `expected_options` es `List[str]` o `List[Dict]`.
            compare_by_value (bool): Si es `True`, compara el atributo 'value' de las opciones.
                                   Usado si `expected_options` es `List[Dict]`.
            nombre_paso (str, opcional): Una descripción del paso que se está ejecutando para los logs y nombres de capturas. Por defecto "".
            timeout_ms (int): Tiempo máximo de espera en milisegundos para la visibilidad,
                              habilitación y la obtención de opciones. Por defecto `15000`ms (15 segundos).

        Returns:
            Optional[List[Dict[str, str]]]: Una lista de diccionarios con las opciones reales extraídas
                                           ({'value': '...', 'text': '...'}).
                                           Retorna `None` si no se encuentran opciones o si ocurre un error.

        Raises:
            AssertionError: Si el dropdown no es visible/habilitado, las opciones no se cargan,
                            si no se encuentran opciones cuando se esperaban,
                            o si la comparación de opciones falla.
        """
        self.logger.info(f"\n--- {nombre_paso}: Extrayendo y comparando valores del dropdown '{dropdown_locator}' ---")

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()
        valores_opciones_reales: List[Dict[str, str]] = []

        try:
            # 1. Asegurar que el dropdown es visible y habilitado
            self.logger.info(f"\n🔍 Esperando que el dropdown '{dropdown_locator}' sea visible y habilitado...")
            # --- Medición de rendimiento: Inicio validación/espera ---
            start_time_validation = time.time()
            expect(dropdown_locator).to_be_visible()
            dropdown_locator.highlight() # Para visualización durante la ejecución
            expect(dropdown_locator).to_be_enabled()
            # --- Medición de rendimiento: Fin validación/espera ---
            end_time_validation = time.time()
            duration_validation = end_time_validation - start_time_validation
            self.logger.info(f"PERFORMANCE: Tiempo de validación de visibilidad y habilitación del dropdown: {duration_validation:.4f} segundos.")
            
            self.logger.info(f"\n✅ Dropdown '{dropdown_locator}' es visible y habilitado.")
            self.base.tomar_captura(f"{nombre_base}_dropdown_antes_extraccion_y_comparacion", directorio)

            # 2. Obtener todos los locators de las opciones dentro del dropdown
            self.logger.info(f"\n🔄 Obteniendo locators de todas las opciones dentro de '{dropdown_locator}'...")
            # --- Medición de rendimiento: Inicio obtención de option locators ---
            start_time_get_options = time.time()
            option_locators = dropdown_locator.locator("option").all()
            # --- Medición de rendimiento: Fin obtención de option locators ---
            end_time_get_options = time.time()
            duration_get_options = end_time_get_options - start_time_get_options
            self.logger.info(f"PERFORMANCE: Tiempo de obtención de todos los option locators: {duration_get_options:.4f} segundos.")

            if not option_locators:
                self.logger.warning(f"\n⚠️ No se encontraron opciones dentro del dropdown '{dropdown_locator}'.")
                self.base.tomar_captura(f"{nombre_base}_dropdown_sin_opciones", directorio)
                # Si se esperaban opciones y no hay ninguna, esto es un fallo de aserción.
                if expected_options:
                    raise AssertionError(f"\n❌ FALLO: No se encontraron opciones en el dropdown '{dropdown_locator}', pero se esperaban {len(expected_options)}.")
                return None

            self.logger.info(f"\n Encontradas {len(option_locators)} opciones reales para '{dropdown_locator}':")

            # 3. Iterar sobre cada opción y extraer su 'value' y 'text_content'
            self.logger.info("\n📊 Extrayendo valores y textos de cada opción...")
            # --- Medición de rendimiento: Inicio iteración y extracción ---
            start_time_extract_loop = time.time()
            for i, option_locator in enumerate(option_locators):
                value = option_locator.get_attribute("value")
                text = option_locator.text_content()

                # Limpieza de espacios en blanco
                # Asegura que value y text no sean None antes de strip().
                clean_value = value.strip() if value is not None else ""
                clean_text = text.strip() if text is not None else ""

                valores_opciones_reales.append({'value': clean_value, 'text': clean_text})
                self.logger.info(f"\n  Opción Real {i+1}: Value='{clean_value}', Text='{clean_text}'")
            # --- Medición de rendimiento: Fin iteración y extracción ---
            end_time_extract_loop = time.time()
            duration_extract_loop = end_time_extract_loop - start_time_extract_loop
            self.logger.info(f"PERFORMANCE: Tiempo de iteración y extracción de {len(option_locators)} opciones: {duration_extract_loop:.4f} segundos.")

            self.logger.info(f"\n✅ Valores obtenidos exitosamente del dropdown '{dropdown_locator}'.")
            self.base.tomar_captura(f"{nombre_base}_dropdown_valores_extraidos", directorio)

            # 4. Comparar con las opciones esperadas (si se proporcionan)
            if expected_options is not None:
                self.logger.info("\n--- Realizando comparación de opciones ---")
                # --- Medición de rendimiento: Inicio de la fase de comparación ---
                start_time_comparison = time.time()
                try:
                    expected_set = set()
                    real_set = set()

                    # Preparar los conjuntos para la comparación (normalizando a minúsculas y sin espacios extra)
                    for opt in expected_options:
                        if isinstance(opt, str):
                            if compare_by_text:
                                expected_set.add(opt.strip().lower())
                            else:
                                self.logger.warning(f"\n⚠️ Advertencia: Opciones esperadas en formato `str` pero `compare_by_text` es `False`. Ignorando '{opt}'.")
                        elif isinstance(opt, dict):
                            if compare_by_text and 'text' in opt and opt['text'] is not None:
                                expected_set.add(opt['text'].strip().lower())
                            if compare_by_value and 'value' in opt and opt['value'] is not None:
                                expected_set.add(opt['value'].strip().lower())
                            if not (compare_by_text or compare_by_value):
                                self.logger.warning(f"\n⚠️ Advertencia: `compare_by_text` y `compare_by_value` son `False`. Ninguna comparación se realizará para la opción esperada: {opt}.")
                        else:
                            self.logger.warning(f"\n⚠️ Advertencia: Formato de opción esperada no reconocido: '{opt}'. Ignorando.")

                    # Construir el conjunto de opciones reales para comparación
                    for opt_real in valores_opciones_reales:
                        if compare_by_text and 'text' in opt_real and opt_real['text'] is not None:
                            real_set.add(opt_real['text'].strip().lower())
                        if compare_by_value and 'value' in opt_real and opt_real['value'] is not None:
                            real_set.add(opt_real['value'].strip().lower())

                    # Comprobar si los conjuntos son idénticos
                    if expected_set == real_set:
                        self.logger.info("\n✅ ÉXITO: Las opciones del dropdown coinciden con las opciones esperadas.")
                        self.base.tomar_captura(f"{nombre_base}_dropdown_comparacion_exitosa", directorio)
                    else:
                        missing_in_real = list(expected_set - real_set)
                        missing_in_expected = list(real_set - expected_set)
                        error_msg = f"\n❌ FALLO: Las opciones del dropdown NO coinciden con las esperadas.\n"
                        if missing_in_real:
                            error_msg += f"  - Opciones esperadas no encontradas en el dropdown: {missing_in_real}\n"
                        if missing_in_expected:
                            error_msg += f"  - Opciones encontradas en el dropdown que no estaban esperadas: {missing_in_expected}\n"
                        self.logger.error(error_msg)
                        self.base.tomar_captura(f"{nombre_base}_dropdown_comparacion_fallida", directorio)
                        raise AssertionError(f"\nComparación de opciones del dropdown fallida para '{dropdown_locator}'. {error_msg.strip()}")

                except Exception as e:
                    self.logger.critical(f"\n❌ FALLO: Ocurrió un error durante la comparación de opciones: {e}", exc_info=True)
                    self.base.tomar_captura(f"{nombre_base}_dropdown_error_comparacion", directorio)
                    raise AssertionError(f"\nError al comparar opciones del dropdown '{dropdown_locator}': {e}") from e
                # --- Medición de rendimiento: Fin de la fase de comparación ---
                end_time_comparison = time.time()
                duration_comparison = end_time_comparison - start_time_comparison
                self.logger.info(f"PERFORMANCE: Tiempo de la fase de comparación: {duration_comparison:.4f} segundos.")

            return valores_opciones_reales

        except TimeoutError as e:
            mensaje_error = (
                f"\n❌ FALLO (Timeout) - {nombre_paso}: El dropdown '{dropdown_locator}' "
                f"no se volvió visible/habilitado o sus opciones no cargaron a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.tomar_captura(f"{nombre_base}_dropdown_fallo_timeout", directorio)
            raise AssertionError(mensaje_error) from e

        except Error as e:
            mensaje_error = (
                f"\n❌ FALLO (Error de Playwright) - {nombre_paso}: Ocurrió un error de Playwright al intentar obtener los valores del dropdown '{dropdown_locator}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_dropdown_fallo_playwright_error", directorio)
            raise AssertionError(mensaje_error) from e

        except Exception as e:
            mensaje_error = (
                f"\n❌ FALLO (Error Inesperado) - {nombre_paso}: Ocurrió un error desconocido al intentar obtener los valores del dropdown '{dropdown_locator}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(mensaje_error, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_dropdown_fallo_inesperado", directorio)
            raise AssertionError(mensaje_error) from e
        finally:
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (obtener y comparar valores dropdown): {duration_total_operation:.4f} segundos.")