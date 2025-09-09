import time
import random
from typing import Union, Optional, Dict, Any, List, Tuple
from playwright.sync_api import Page, Locator, expect, Error, TimeoutError

class TableActions:
    def __init__(self, base_page):
        self.base = base_page
        self.page: Page = base_page.page
        self.logger = base_page.logger
        
    # 27- Función para contar filas y columnas de una tabla con pruebas de rendimiento
    def obtener_dimensiones_tabla(self, selector: Locator, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5) -> Tuple[int, int]:
        """
        Obtiene las dimensiones (número de filas y columnas) de una tabla HTML
        identificada por un Playwright Locator. Mide el tiempo que toma esta operación.

        Prioriza el conteo de filas de `tbody tr` y columnas de `th` (encabezados).
        Si no hay encabezados, intenta contar las celdas `td` de la primera fila de datos.

        Args:
            selector (Locator): El **Locator de Playwright** que representa el elemento
                                `<table>` (o un elemento padre que contenga la tabla).
                                Es crucial que sea un Locator, no una cadena, para aprovechar
                                sus funcionalidades de espera y contexto.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que la tabla
                                        y sus elementos internos (filas/columnas) estén presentes
                                        y visibles antes de intentar contarlos.
                                        También es el tiempo de espera fijo después de la operación.
                                        Por defecto, `5.0` segundos (ajustado de 1.0 para robustez).

        Returns:
            tuple[int, int]: Una tupla `(num_filas, num_columnas)` representando las dimensiones de la tabla.
                             Retorna `(-1, -1)` en caso de `TimeoutError` si la tabla no está lista.

        Raises:
            Error: Si ocurre un problema específico de Playwright al interactuar con el selector
                   (ej., el selector no apunta a una tabla o un elemento válido).
            Exception: Para cualquier otro error inesperado.
        """
        # Intentar obtener información útil del selector para los logs y nombres de captura.
        # Esto ayuda a identificar la tabla en los logs, especialmente si no tiene ID/NAME.
        selector_info = selector.get_attribute('id') or selector.get_attribute('name')
        if not selector_info:
            try:
                # Si no hay id/name, intentar obtener el HTML externo de la etiqueta principal
                selector_info = selector.evaluate("el => el.outerHTML.split('>')[0] + '>'")
            except Exception:
                selector_info = f"Tabla con selector genérico: {selector}" # Fallback si evaluate falla

        self.logger.info(f"\nObteniendo dimensiones de la tabla con selector: '{selector_info}'. Tiempo máximo de espera: {tiempo}s.")

        # --- Medición de rendimiento: Inicio de la operación de obtener dimensiones ---
        # Registra el tiempo justo antes de iniciar la interacción para obtener las dimensiones.
        start_time_get_dimensions = time.time()

        try:
            # 1. Asegurar que la tabla principal esté visible
            # Es crucial que la tabla esté cargada y visible para poder contar sus elementos.
            self.logger.debug(f"\nEsperando que la tabla con selector '{selector_info}' esté visible (timeout: {tiempo}s).")
            expect(selector).to_be_visible()
            
            # Resaltar el elemento de la tabla para depuración visual.
            selector.highlight()
            self.logger.debug(f"\nTabla con selector '{selector_info}' resaltada.")
            self.base.tomar_captura(f"{nombre_base}_antes_obtener_dimensiones", directorio) # Captura antes de contar.

            # 2. Contar el número de filas de datos
            # Se buscan filas `<tr>` dentro de un `<tbody>` para contar solo las filas de datos,
            # excluyendo potencialmente encabezados o pies de tabla.
            filas_datos = selector.locator("tbody tr")
            num_filas = filas_datos.count()
            self.logger.debug(f"\nFilas de datos encontradas (tbody tr): {num_filas}.")

            # 3. Contar el número de columnas
            num_columnas = 0
            # Intentar contar desde los encabezados de la tabla (th) primero.
            headers = selector.locator("th")
            if headers.count() > 0:
                num_columnas = headers.count()
                self.logger.debug(f"\nColumnas contadas desde encabezados (th): {num_columnas}.")
            else:
                # Si no hay thead/th, intentar contar td's de la primera fila de datos.
                # Esto es útil para tablas que no usan thead o que son simples.
                first_row_tds = selector.locator("tr").first.locator("td")
                if first_row_tds.count() > 0:
                    num_columnas = first_row_tds.count()
                    self.logger.debug(f"\nColumnas contadas desde celdas de la primera fila (td): {num_columnas}.")
                else:
                    self.logger.warning(f"\nADVERTENCIA: No se pudieron encontrar encabezados (th) ni celdas (td) en la primera fila "
                                        f"para la tabla con selector '{selector_info}'. Asumiendo 0 columnas.")
                    # En este caso, num_columnas seguirá siendo 0.

            # --- Medición de rendimiento: Fin de la operación de obtener dimensiones ---
            # Registra el tiempo una vez que se han contado las filas y columnas.
            end_time_get_dimensions = time.time()
            duration_get_dimensions = end_time_get_dimensions - start_time_get_dimensions
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en obtener las dimensiones de la tabla '{selector_info}': {duration_get_dimensions:.4f} segundos.")

            self.base.tomar_captura(f"{nombre_base}_dimensiones_obtenidas", directorio)
            self.logger.info(f"\n✅ ÉXITO: Dimensiones de la tabla '{selector_info}' obtenidas.")
            self.logger.info(f"--> Filas encontradas: {num_filas}")
            self.logger.info(f"--> Columnas encontradas: {num_columnas}")
            return (num_filas, num_columnas)

        except TimeoutError as e:
            # Captura si la tabla principal o sus elementos internos no se hacen visibles a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_get_dimensions # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): No se pudo obtener las dimensiones de la tabla con selector '{selector_info}' "
                f"después de {duration_fail:.4f} segundos (timeout configurado: {tiempo}s).\n"
                f"La tabla o sus elementos internos no estuvieron disponibles a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.warning(error_msg, exc_info=True) # Usa 'warning' ya que devuelve un valor indicativo de fallo.
            self.base.tomar_captura(f"{nombre_base}_dimensiones_timeout", directorio)
            return (-1, -1) # Retorna valores indicativos de fallo.

        except Error as e:
            # Captura errores específicos de Playwright (ej., selector de tabla inválido, problema al interactuar con el DOM).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al intentar obtener las dimensiones de la tabla con selector '{selector_info}'.\n"
                f"Posibles causas: Selector de tabla inválido, estructura de tabla inesperada, elemento no es una tabla.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_dimensiones_error_playwright", directorio)
            raise # Relanzar porque es un error de ejecución de Playwright, no un fallo de aserción.

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al obtener las dimensiones de la tabla con selector '{selector_info}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Nivel crítico para errores muy graves.
            self.base.tomar_captura(f"{nombre_base}_dimensiones_error_inesperado", directorio)
            raise # Relanzar por ser un error inesperado.
        
    # 28- Función para buscar datos parcial e imprimir la fila con pruebas de rendimiento
    def busqueda_coincidencia_e_imprimir_fila(self, table_selector: Locator, texto_buscado: str, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5) -> bool:
        """
        Busca una **coincidencia parcial de texto** dentro de las filas de una tabla
        especificada por un Playwright Locator. Si encuentra el texto, resalta la fila
        y registra su contenido. Mide el rendimiento de esta operación de búsqueda.

        Args:
            table_selector (Locator): El **Locator de Playwright** que representa el elemento
                                      `<table>` (o un elemento padre que contenga la tabla).
                                      Es crucial que sea un Locator, no una cadena, para aprovechar
                                      sus funcionalidades de espera y contexto.
            texto_buscado (str): El **texto a buscar** dentro de las filas de la tabla.
                                 La búsqueda no es sensible a mayúsculas/minúsculas.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que la tabla
                                        esté visible antes de iniciar la búsqueda.
                                        También es el tiempo de espera fijo después de la operación.
                                        Por defecto, `5.0` segundos (ajustado de 1.0 para robustez).

        Returns:
            bool: `True` si se encuentra al menos una coincidencia parcial del `texto_buscado`
                  en alguna fila de la tabla; `False` en caso contrario o si ocurre un `TimeoutError`.

        Raises:
            Error: Si ocurre un problema específico de Playwright al interactuar con el selector
                   de la tabla (ej., el selector no apunta a una tabla válida).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nIniciando búsqueda de coincidencia parcial para '{texto_buscado}' en la tabla con selector: '{table_selector}'. Tiempo máximo de espera: {tiempo}s.")
        encontrado = False

        # --- Medición de rendimiento: Inicio de la búsqueda en la tabla ---
        # Registra el tiempo justo antes de iniciar la interacción con la tabla para la búsqueda.
        start_time_table_search = time.time()

        try:
            # 1. Esperar a que la tabla esté visible
            # Esto es fundamental antes de intentar iterar sobre sus filas.
            self.logger.debug(f"\nEsperando que la tabla con selector '{table_selector}' esté visible (timeout: {tiempo}s).")
            expect(table_selector).to_be_visible()
            self.logger.info(f"\nTabla con selector '{table_selector}' está visible.")
            
            # Resaltar la tabla completa para depuración visual.
            table_selector.highlight()
            self.base.tomar_captura(f"{nombre_base}_antes_busqueda_coincidencia", directorio) # Captura antes de buscar.

            # 2. Obtener todas las filas de datos de la tabla
            # Se buscan filas `<tr>` dentro de un `<tbody>` para enfocar la búsqueda en los datos.
            filas = table_selector.locator("tbody tr")
            num_filas = filas.count()
            self.logger.debug(f"\nNúmero de filas de datos encontradas en la tabla: {num_filas}.")

            # 3. Iterar sobre cada fila para buscar la coincidencia
            for i in range(num_filas):
                fila = filas.nth(i) # Obtiene el Locator para la fila actual.
                fila_texto = fila.text_content() # Obtiene todo el texto visible de la fila.
                self.logger.debug(f"\nAnalizando fila {i+1}: '{fila_texto}'.")

                # Realizar la búsqueda de coincidencia parcial sin distinguir mayúsculas/minúsculas.
                if texto_buscado.lower() in fila_texto.lower():
                    self.logger.info(f"\n✅ ÉXITO: Texto '{texto_buscado}' encontrado (coincidencia parcial) en la fila {i+1}.")
                    self.logger.info(f"Contenido completo de la fila: '{fila_texto}'")
                    fila.highlight() # Resalta la fila donde se encontró la coincidencia.
                    self.base.tomar_captura(f"{nombre_base}_coincidencia_parcial_encontrada_fila_{i+1}", directorio)
                    encontrado = True
                    # Si solo se necesita encontrar la primera coincidencia y terminar, descomentar el 'break'
                    # break 
            
            if not encontrado:
                self.logger.info(f"\nℹ️ Texto '{texto_buscado}' (coincidencia parcial) NO encontrado en ninguna fila de la tabla.")
                self.base.tomar_captura(f"{nombre_base}_coincidencia_parcial_no_encontrada", directorio)

            # --- Medición de rendimiento: Fin de la búsqueda en la tabla ---
            # Registra el tiempo una vez que se ha completado la iteración sobre todas las filas (o hasta la primera coincidencia si se usa break).
            end_time_table_search = time.time()
            duration_table_search = end_time_table_search - start_time_table_search
            self.logger.info(f"PERFORMANCE: Tiempo que tardó la búsqueda de '{texto_buscado}' en la tabla '{table_selector}': {duration_table_search:.4f} segundos.")

            return encontrado

        except TimeoutError as e:
            # Captura si la tabla principal o sus filas no se hacen visibles a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_table_search # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): No se pudo encontrar la tabla con selector '{table_selector}' "
                f"o sus filas no estuvieron disponibles a tiempo ({duration_fail:.4f}s, timeout configurado: {tiempo}s) "
                f"durante la búsqueda de '{texto_buscado}'.\n"
                f"Detalles: {e}"
            )
            self.logger.warning(error_msg, exc_info=True) # Usa 'warning' ya que devuelve False.
            self.base.tomar_captura(f"{nombre_base}_busqueda_coincidencia_timeout", directorio)
            return False

        except Error as e:
            # Captura errores específicos de Playwright (ej., selector de tabla inválido, problemas de interacción con el DOM).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al buscar coincidencia para '{texto_buscado}' "
                f"en la tabla con selector '{table_selector}'.\n"
                f"Posibles causas: Selector de tabla inválido, estructura de tabla inesperada, o problemas de interacción con el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_busqueda_coincidencia_error_playwright", directorio)
            raise # Relanzar porque es un error de ejecución de Playwright.

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al buscar coincidencia para '{texto_buscado}' "
                f"en la tabla con selector '{table_selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Nivel crítico para errores muy graves.
            self.base.tomar_captura(f"{nombre_base}_busqueda_coincidencia_error_inesperado", directorio)
            raise # Relanzar por ser un error inesperado.
        
    # 29- Función para buscar datos exacto e imprimir la fila con pruebas de rendimiento
    def busqueda_estricta_imprimir_fila(self, table_selector: Locator, texto_buscado: str, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5) -> bool:
        """
        Busca una **coincidencia exacta de texto** dentro de las celdas de una tabla
        especificada por un Playwright Locator. Si encuentra el texto, resalta la celda
        y la fila correspondiente, y registra el contenido completo de la fila.
        Mide el rendimiento de esta operación de búsqueda estricta.

        Args:
            table_selector (Locator): El **Locator de Playwright** que representa el elemento
                                      `<table>` (o un elemento padre que contenga la tabla).
                                      Es crucial que sea un Locator, no una cadena, para aprovechar
                                      sus funcionalidades de espera y contexto.
            texto_buscado (str): El **texto exacto a buscar** dentro de las celdas de la tabla.
                                 La búsqueda es sensible a mayúsculas/minúsculas y requiere una
                                 coincidencia exacta (después de eliminar espacios en blanco).
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que la tabla
                                        esté visible antes de iniciar la búsqueda.
                                        También es el tiempo de espera fijo después de la operación.
                                        Por defecto, `5.0` segundos (ajustado de 1.0 para robustez).

        Returns:
            bool: `True` si se encuentra al menos una coincidencia exacta del `texto_buscado`
                  en alguna celda de la tabla; `False` en caso contrario o si ocurre un `TimeoutError`.

        Raises:
            Error: Si ocurre un problema específico de Playwright al interactuar con el selector
                   de la tabla (ej., el selector no apunta a una tabla válida).
            Exception: Para cualquier otro error inesperado.
        """
        self.logger.info(f"\nIniciando búsqueda estricta para '{texto_buscado}' en la tabla con selector: '{table_selector}'. Tiempo máximo de espera: {tiempo}s.")
        encontrado = False

        # --- Medición de rendimiento: Inicio de la búsqueda estricta en la tabla ---
        # Registra el tiempo justo antes de iniciar la interacción con la tabla para la búsqueda.
        start_time_strict_search = time.time()

        try:
            # 1. Esperar a que la tabla esté visible
            # Esto es fundamental antes de intentar iterar sobre sus filas y celdas.
            self.logger.debug(f"\nEsperando que la tabla con selector '{table_selector}' esté visible (timeout: {tiempo}s).")
            expect(table_selector).to_be_visible()
            self.logger.info(f"\nTabla con selector '{table_selector}' está visible.")
            
            # Resaltar la tabla completa para depuración visual.
            table_selector.highlight()
            self.base.tomar_captura(f"{nombre_base}_antes_busqueda_estricta", directorio) # Captura antes de buscar.

            # 2. Obtener todas las filas de datos de la tabla
            # Se buscan filas `<tr>` dentro de un `tbody` para enfocar la búsqueda en los datos.
            filas = table_selector.locator("tbody tr")
            num_filas = filas.count()
            self.logger.debug(f"\nNúmero de filas de datos encontradas en la tabla: {num_filas}.")

            # 3. Iterar sobre cada fila y cada celda para buscar la coincidencia exacta
            for i in range(num_filas):
                fila = filas.nth(i) # Obtiene el Locator para la fila actual.
                celdas = fila.locator("td") # Asumiendo celdas de datos son 'td'.
                num_celdas = celdas.count()
                fila_texto_completo = "" # Para reconstruir y loggear el contenido completo de la fila.
                self.logger.debug(f"\nAnalizando fila {i+1} para búsqueda estricta.")

                for j in range(num_celdas):
                    celda = celdas.nth(j) # Obtiene el Locator para la celda actual.
                    celda_texto = celda.text_content().strip() # Obtiene el texto de la celda y elimina espacios en blanco alrededor.
                    fila_texto_completo += celda_texto + " | " # Concatenar para imprimir la fila completa en el log.

                    # Realizar la búsqueda de coincidencia estricta.
                    if celda_texto == texto_buscado: # Coincidencia estricta
                        self.logger.info(f"\n✅ ÉXITO: Texto '{texto_buscado}' encontrado (coincidencia estricta) en la celda {j+1} de la fila {i+1}.")
                        self.logger.info(f"Contenido completo de la fila: '{fila_texto_completo.strip(' | ')}'")
                        celda.highlight() # Resaltar la celda donde se encontró la coincidencia.
                        fila.highlight() # También resaltar la fila para mejor visibilidad.
                        self.base.tomar_captura(f"{nombre_base}_coincidencia_estricta_encontrada_fila_{i+1}_celda_{j+1}", directorio)
                        encontrado = True
                        # Si solo se necesita encontrar la primera coincidencia y terminar, descomentar ambos 'break'.
                        # break # Rompe el bucle de celdas.
                
                if encontrado:
                    # break # Rompe el bucle de filas si se encontró una coincidencia y se desea parar.
                    pass # Si se desea seguir buscando en otras filas, manteniendo el 'encontrado' en True.

            if not encontrado:
                self.logger.info(f"\nℹ️ Texto '{texto_buscado}' (coincidencia estricta) NO encontrado en ninguna celda de la tabla.")
                self.base.tomar_captura(f"{nombre_base}_coincidencia_estricta_no_encontrada", directorio)

            # --- Medición de rendimiento: Fin de la búsqueda estricta en la tabla ---
            # Registra el tiempo una vez que se ha completado la iteración sobre todas las celdas/filas.
            end_time_strict_search = time.time()
            duration_strict_search = end_time_strict_search - start_time_strict_search
            self.logger.info(f"PERFORMANCE: Tiempo que tardó la búsqueda estricta de '{texto_buscado}' en la tabla '{table_selector}': {duration_strict_search:.4f} segundos.")

            return encontrado

        except TimeoutError as e:
            # Captura si la tabla principal o sus elementos internos (filas/celdas) no se hacen visibles a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_strict_search # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): No se pudo encontrar la tabla con selector '{table_selector}' "
                f"o sus elementos internos no estuvieron disponibles a tiempo ({duration_fail:.4f}s, timeout configurado: {tiempo}s) "
                f"durante la búsqueda estricta de '{texto_buscado}'.\n"
                f"Detalles: {e}"
            )
            self.logger.warning(error_msg, exc_info=True) # Usa 'warning' ya que devuelve False.
            self.base.tomar_captura(f"{nombre_base}_busqueda_estricta_timeout", directorio)
            return False

        except Error as e:
            # Captura errores específicos de Playwright (ej., selector de tabla inválido, problemas de interacción con el DOM).
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al buscar estrictamente '{texto_buscado}' "
                f"en la tabla con selector '{table_selector}'.\n"
                f"Posibles causas: Selector de tabla inválido, estructura de tabla inesperada, o problemas de interacción con el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_busqueda_estricta_error_playwright", directorio)
            raise # Relanzar porque es un error de ejecución de Playwright.

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al buscar estrictamente '{texto_buscado}' "
                f"en la tabla con selector '{table_selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Nivel crítico para errores muy graves.
            self.base.tomar_captura(f"{nombre_base}_busqueda_estricta_error_inesperado", directorio)
            raise # Relanzar por ser un error inesperado.
        
    # 30- Función para validar que todos los valores en una columna específica de una tabla sean numéricos, con pruebas de rendimiento
    def verificar_precios_son_numeros(self, tabla_selector: Locator, columna_nombre: str, nombre_base: str, directorio: str, tiempo_espera_celda: Union[int, float] = 0.5, tiempo_general_timeout: Union[int, float] = 15.0) -> bool:
        """
        Verifica que todos los valores en una **columna específica** de una tabla HTML
        sean **numéricos válidos**. Esto es crucial para la integridad de los datos
        mostrados en la UI, especialmente para precios o cantidades.
        Mide el rendimiento de esta operación de validación.

        Args:
            tabla_selector (Locator): El **Locator de Playwright** que representa el elemento
                                      `<table>` (o un elemento padre que contenga la tabla).
                                      Es crucial que sea un Locator para aprovechar sus
                                      funcionalidades de espera y contexto.
            columna_nombre (str): El **nombre exacto de la columna** (texto del encabezado `<th>`)
                                  cuyos valores se desean verificar.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_celda (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                     para que una celda de precio individual
                                                     sea visible. Por defecto, `5.0` segundos.
            tiempo_general_timeout (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                        para que la tabla y su `<tbody>` estén
                                                        visibles y listos para la interacción.
                                                        Por defecto, `15.0` segundos.

        Returns:
            bool: `True` si todos los valores en la columna especificada son numéricos válidos;
                  `False` si se encuentra algún valor no numérico o si la columna no existe.

        Raises:
            AssertionError: Si la tabla o sus elementos clave no están disponibles a tiempo,
                            o si ocurre un error inesperado de Playwright o genérico.
        """
        self.logger.info(f"\n⚙️ Verificando que todos los precios en la columna '{columna_nombre}' de la tabla '{tabla_selector}' son números.")

        # --- Medición de rendimiento: Inicio de la validación de la tabla ---
        # Registra el tiempo justo antes de iniciar cualquier interacción con la tabla.
        start_time_validation = time.time()

        try:
            # 1. Asegurar que la tabla principal esté visible
            # Es el primer paso para garantizar que la tabla se ha cargado en el DOM.
            self.logger.debug(f"\nEsperando que la tabla con selector '{tabla_selector}' esté visible (timeout: {tiempo_general_timeout}s).")
            expect(tabla_selector).to_be_visible()
            tabla_selector.highlight()
            self.logger.debug(f"\nTabla resaltada para verificación: {tabla_selector}")

            # 2. Esperar a que el tbody exista y tenga contenido
            # Es crucial esperar por la sección de cuerpo de la tabla y al menos una fila,
            # ya que a menudo se cargan de forma asíncrona.
            tbody_locator = tabla_selector.locator("tbody")
            self.logger.debug(f"\nEsperando que el tbody de la tabla sea visible (timeout: {tiempo_general_timeout}s).")
            expect(tbody_locator).to_be_visible()
            self.logger.info("\n✅ El tbody de la tabla es visible.")
            
            self.logger.debug(f"\nEsperando que al menos la primera fila de datos sea visible (timeout: {tiempo_general_timeout}s).")
            expect(tbody_locator.locator("tr").first).to_be_visible()
            self.logger.info("\n✅ Al menos la primera fila de datos en la tabla es visible.")
            self.base.tomar_captura(f"{nombre_base}_tabla_visible_para_verificacion", directorio) # Captura el estado inicial.

            # 3. Encontrar el índice de la columna por su nombre
            # Primero, asegurar que los encabezados existan y sean visibles.
            headers = tabla_selector.locator("th")
            self.logger.debug(f"\nEsperando que los encabezados (th) de la tabla sean visibles (timeout: {tiempo_general_timeout}s).")
            expect(headers.first).to_be_visible()

            col_index = -1
            header_texts = []
            for i in range(headers.count()):
                header_text = headers.nth(i).text_content().strip()
                header_texts.append(header_text)
                if header_text == columna_nombre:
                    col_index = i
            
            self.logger.info(f"\n🔍 Cabeceras encontradas: {header_texts}")

            if col_index == -1:
                self.logger.error(f"\n❌ Error: No se encontró la columna '{columna_nombre}' en la tabla. Cabeceras disponibles: {header_texts}")
                self.base.tomar_captura(f"{nombre_base}_columna_no_encontrada", directorio)
                # No lanzamos una excepción aquí, ya que el retorno False es suficiente para indicar el fallo lógico.
                return False

            self.logger.info(f"\n🔍 Columna '{columna_nombre}' encontrada en el índice: {col_index}")

            # 4. Obtener todas las filas de la tabla (solo las de datos dentro de tbody)
            rows = tbody_locator.locator("tr")
            num_rows = rows.count()
            if num_rows == 0:
                self.logger.warning("\n⚠️ Advertencia: La tabla no contiene filas de datos para verificar.")
                self.base.tomar_captura(f"{nombre_base}_tabla_vacia_no_precios", directorio)
                return True # Considera esto un éxito si no hay datos que validar.

            self.logger.info(f"\n🔍 Se encontraron {num_rows} filas de datos para verificar precios.")

            all_prices_are_numbers = True
            for i in range(num_rows):
                row_locator = rows.nth(i)
                # Se busca la celda correspondiente al índice de la columna dentro de la fila actual.
                price_cell = row_locator.locator(f"td").nth(col_index)
                
                # Es crucial esperar a que la celda de precio sea visible si las filas se renderizan dinámicamente
                # o el contenido de las celdas aparece con un retardo.
                self.logger.debug(f"\n Esperando que la celda de precio en la fila {i+1} esté visible (timeout: {tiempo_espera_celda}s).")
                expect(price_cell).to_be_visible() # Convertir a milisegundos
                
                price_text = price_cell.text_content().strip() # Obtener texto y limpiar espacios.
                price_cell.highlight() # Resaltar la celda actual para depuración visual.

                self.logger.debug(f"\n Procesando fila {i+1}, texto de precio: '{price_text}'")

                try:
                    float(price_text) # Intentar convertir el texto a un número flotante.
                    self.logger.debug(f"\n ✅ '{price_text}' es un número válido.")
                except ValueError:
                    self.logger.error(f"\n ❌ Error: El valor '{price_text}' en la fila {i+1} de la columna '{columna_nombre}' no es un número válido.")
                    self.base.tomar_captura(f"{nombre_base}_precio_invalido_fila_{i+1}", directorio)
                    all_prices_are_numbers = False
                    # Continuamos el bucle para reportar todos los valores no numéricos, no solo el primero.

            # --- Medición de rendimiento: Fin de la validación ---
            end_time_validation = time.time()
            duration_validation = end_time_validation - start_time_validation
            self.logger.info(f"PERFORMANCE: Tiempo total de validación de precios en la columna '{columna_nombre}': {duration_validation:.4f} segundos.")

            if all_prices_are_numbers:
                self.logger.info(f"\n✅ Todos los precios en la columna '{columna_nombre}' son números válidos.")
                self.base.tomar_captura(f"{nombre_base}_precios_ok", directorio)
                return True
            else:
                self.logger.error(f"\n❌ Se encontraron precios no numéricos en la columna '{columna_nombre}'.")
                return False

        except TimeoutError as e:
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_validation
            error_msg = (
                f"\n❌ FALLO (Timeout): La tabla o sus elementos (tbody, filas, celdas) no se volvieron visibles a tiempo "
                f"después de {duration_fail:.4f} segundos (timeout general configurado: {tiempo_general_timeout}s, celda: {tiempo_espera_celda}s). "
                f"Error: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_timeout_verificacion_precios", directorio)
            # Elevar AssertionError para que la prueba falle claramente cuando la tabla no está lista.
            raise AssertionError(f"\nElementos de la tabla no disponibles a tiempo para verificación de precios: {tabla_selector}") from e
        
        except Error as e:
            # Captura errores específicos de Playwright (ej., selector inválido, DOM mal formado).
            error_msg = (
                f"\n❌ FALLO (Error de Playwright): Ocurrió un error de Playwright al verificar los precios en la tabla '{tabla_selector}'. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Nivel crítico porque un error de Playwright es un problema fundamental.
            self.base.tomar_captura(f"{nombre_base}_playwright_error_verificacion_precios", directorio)
            raise AssertionError(f"\nError de Playwright al verificar precios en la tabla: {tabla_selector}") from e
        
        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Error Inesperado): Ocurrió un error desconocido al verificar los precios en la tabla '{tabla_selector}'. "
                f"Error: {type(e).__name__}: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_excepcion_inesperada", directorio)
            raise AssertionError(f"\nError inesperado al verificar precios en la tabla: {tabla_selector}") from e
                
    # 32- Función para verificar que los encabezados de las columnas de una tabla sean correctos y estén presentes, con pruebas de rendimiento
    def verificar_encabezados_tabla(self, tabla_selector: Locator, encabezados_esperados: List[str], nombre_base: str, directorio: str, tiempo_espera_tabla: Union[int, float] = 1.0) -> bool:
        """
        Verifica que los encabezados (<th>) de las columnas de una tabla HTML
        sean correctos y estén presentes en el orden esperado.
        Mide el rendimiento de esta operación de verificación.

        Args:
            tabla_selector (Locator): El **Locator de Playwright** que representa el elemento
                                      `<table>` (o un elemento padre que contenga la tabla).
                                      Es crucial que sea un Locator para aprovechar sus
                                      funcionalidades de espera y contexto.
            encabezados_esperados (List[str]): Una **lista de cadenas de texto** que representan
                                               los encabezados esperados, en el orden en que
                                               deben aparecer en la tabla.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_tabla (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                     para que la tabla y su sección de encabezado
                                                     (`<thead>` y `<th>`) estén visibles y listos.
                                                     Por defecto, `10.0` segundos.

        Returns:
            bool: `True` si todos los encabezados de la tabla coinciden con los esperados
                  en cantidad y contenido; `False` en caso contrario o si la tabla/encabezados
                  no están disponibles a tiempo.

        Raises:
            AssertionError: Si la tabla o sus elementos de encabezado no están disponibles
                            a tiempo, o si ocurre un error inesperado de Playwright o genérico
                            que impida la verificación.
        """
        self.logger.info(f"\n⚙️ Verificando encabezados de la tabla con selector '{tabla_selector}'...")
        self.logger.info(f"\nEncabezados esperados: {encabezados_esperados}. Tiempo máximo de espera: {tiempo_espera_tabla}s.")
        
        # --- Medición de rendimiento: Inicio de la verificación de encabezados ---
        # Registra el tiempo justo antes de iniciar cualquier interacción con la tabla.
        start_time_header_verification = time.time()

        try:
            # 1. Verificar la presencia y visibilidad de la tabla misma
            # Esto es crucial para asegurar que la tabla se ha cargado en el DOM.
            self.logger.debug(f"\nEsperando que la tabla con selector '{tabla_selector}' esté visible (timeout: {tiempo_espera_tabla}s).")
            expect(tabla_selector).to_be_visible()
            tabla_selector.highlight()
            self.logger.debug(f"\nTabla resaltada para verificación: {tabla_selector}")

            # 2. Verificar la presencia y visibilidad del elemento thead (cabecera de la tabla)
            thead_locator = tabla_selector.locator("thead")
            self.logger.debug(f"\nEsperando que el thead de la tabla con selector '{tabla_selector} thead' esté visible (timeout: {tiempo_espera_tabla}s).")
            expect(thead_locator).to_be_visible()
            self.logger.info("\n✅ El elemento '<thead>' de la tabla es visible.")
            
            # 3. Obtener los locators de los encabezados (<th>) dentro del thead
            encabezados_actuales_locators = thead_locator.locator("th")
            self.logger.debug(f"\nEsperando que al menos un '<th>' dentro del '<thead>' sea visible (timeout: {tiempo_espera_tabla}s).")
            expect(encabezados_actuales_locators.first).to_be_visible()
            
            # Resaltar todos los encabezados encontrados para depuración visual.
            for i in range(encabezados_actuales_locators.count()):
                encabezados_actuales_locators.nth(i).highlight()
            self.base.tomar_captura(f"{nombre_base}_encabezados_encontrados_y_resaltados", directorio)

            num_encabezados_actuales = encabezados_actuales_locators.count()
            num_encabezados_esperados = len(encabezados_esperados)

            # 4. Comparar la cantidad de encabezados
            if num_encabezados_actuales != num_encabezados_esperados:
                actual_texts = [h.text_content().strip() for h in encabezados_actuales_locators.all_js_handles()] # Obtener todos los textos para el log de error
                self.logger.error(f"\n❌ --> FALLO: El número de encabezados '<th>' encontrados ({num_encabezados_actuales}) "
                                  f"no coincide con el número de encabezados esperados ({num_encabezados_esperados}).\n"
                                  f"Actuales: {actual_texts}\nEsperados: {encabezados_esperados}")
                self.base.tomar_captura(f"{nombre_base}_cantidad_encabezados_incorrecta", directorio)
                return False

            # 5. Iterar y comparar el texto de cada encabezado
            todos_correctos = True
            for i in range(num_encabezados_esperados):
                encabezado_locator = encabezados_actuales_locators.nth(i)
                # Obtenemos el texto de la celda del encabezado y eliminamos espacios en blanco.
                texto_encabezado_actual = encabezado_locator.text_content().strip()
                encabezado_esperado = encabezados_esperados[i]

                if texto_encabezado_actual == encabezado_esperado:
                    self.logger.info(f"\n ✅ Encabezado {i+1}: '{texto_encabezado_actual}' coincide con el esperado '{encabezado_esperado}'.")
                    # encabezado_locator.highlight() # Opcional: resaltar el encabezado individual si es necesario para cada uno.
                else:
                    self.logger.error(f"\n ❌ FALLO: Encabezado {i+1} esperado era '{encabezado_esperado}', pero se encontró '{texto_encabezado_actual}'.")
                    encabezado_locator.highlight() # Resaltar el encabezado incorrecto.
                    self.base.tomar_captura(f"{nombre_base}_encabezado_incorrecto_{i+1}", directorio)
                    todos_correctos = False
                    # No es necesario un time.sleep() aquí si solo queremos el log y la captura.

            # --- Medición de rendimiento: Fin de la verificación de encabezados ---
            end_time_header_verification = time.time()
            duration_header_verification = end_time_header_verification - start_time_header_verification
            self.logger.info(f"PERFORMANCE: Tiempo total de verificación de encabezados de tabla '{tabla_selector}': {duration_header_verification:.4f} segundos.")

            if todos_correctos:
                self.logger.info("\n✅ ÉXITO: Todos los encabezados de columna son correctos y están en el orden esperado.")
                self.base.tomar_captura(f"{nombre_base}_encabezados_verificados_ok", directorio)
                return True
            else:
                self.logger.error("\n❌ FALLO: Uno o más encabezados de columna son incorrectos o no están en el orden esperado.")
                self.base.tomar_captura(f"{nombre_base}_encabezados_verificados_fallo", directorio)
                return False

        except TimeoutError as e:
            # Captura si la tabla, el thead o los th no se vuelven visibles a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_header_verification
            error_msg = (
                f"\n❌ FALLO (Timeout): La tabla o sus encabezados con el selector '{tabla_selector}' no se volvieron visibles a tiempo "
                f"después de {duration_fail:.4f} segundos (timeout configurado: {tiempo_espera_tabla}s).\n"
                f"Posiblemente la tabla no estuvo disponible a tiempo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_verificar_encabezados_timeout", directorio)
            # Elevar AssertionError para que la prueba falle claramente cuando la tabla no está lista.
            raise AssertionError(f"\nElementos de encabezado de tabla no disponibles a tiempo: {tabla_selector}") from e

        except Error as e: # Catch Playwright-specific errors
            # Captura errores de Playwright que impiden la interacción con el DOM.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al intentar verificar la tabla o sus encabezados con el selector '{tabla_selector}'.\n"
                f"Posibles causas: Selector inválido, problemas de interacción con el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Nivel crítico para errores de Playwright.
            self.base.tomar_captura(f"{nombre_base}_verificar_encabezados_error_playwright", directorio)
            raise AssertionError(f"\nError de Playwright al verificar encabezados de tabla: {tabla_selector}") from e # Relanzar.

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error desconocido al verificar los encabezados de la tabla con el selector '{tabla_selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_verificar_encabezados_error_inesperado", directorio)
            raise AssertionError(f"\nError inesperado al verificar encabezados de tabla: {tabla_selector}") from e # Relanzar.
        
    # 33- Función para verificar los datos de las filas de una tabla, con pruebas de rendimiento integradas.
    def verificar_datos_filas_tabla(self, tabla_selector: Locator, datos_filas_esperados: List[Dict[str, Union[str, bool, int, float]]], nombre_base: str, directorio: str, tiempo_espera_general: Union[int, float] = 0.5) -> bool:
        """
        Verifica que los datos de las filas de una tabla HTML coincidan con los datos esperados.
        La función compara el número de filas, el texto de las celdas y el estado de los checkboxes
        en columnas específicas. Mide el rendimiento de todo el proceso de verificación.

        Args:
            tabla_selector (Locator): El **Locator de Playwright** que representa el elemento
                                      `<table>` que contiene las filas a verificar.
            datos_filas_esperados (List[Dict[str, Union[str, bool, int, float]]]): Una lista
                                      de diccionarios, donde cada diccionario representa una fila
                                      esperada. Las claves del diccionario deben ser los nombres
                                      de los encabezados de las columnas y los valores, los
                                      datos esperados para esa columna en la fila.
                                      Ejemplo: `[{'ID': '123', 'Name': 'Product A', 'Price': '10.50', 'Select': True}]`.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_general (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                        para que la tabla, sus encabezados y
                                                        las filas estén visibles y listos para
                                                        la interacción. Por defecto, `15.0` segundos.

        Returns:
            bool: `True` si todos los datos de las filas y los estados de los checkboxes
                  coinciden con los valores esperados; `False` en caso contrario o si
                  la tabla/datos no están disponibles a tiempo.

        Raises:
            AssertionError: Si la tabla o sus elementos clave (encabezados, filas) no están
                            disponibles a tiempo, o si ocurre un error inesperado de Playwright
                            o genérico que impida la verificación.
        """
        self.logger.info(f"\n--- Iniciando verificación de datos de las filas de la tabla con locator '{tabla_selector}' ---")
        self.logger.info(f"\nNúmero de filas esperadas: {len(datos_filas_esperados)}")
        self.base.tomar_captura(f"{nombre_base}_inicio_verificacion_datos_filas", directorio)

        # --- Medición de rendimiento: Inicio de la verificación de datos de filas ---
        # Registra el tiempo justo antes de iniciar cualquier interacción con la tabla.
        start_time_row_data_verification = time.time()

        try:
            # 1. Asegurarse de que la tabla esté visible y disponible
            self.logger.debug(f"\nEsperando que la tabla con selector '{tabla_selector}' esté visible (timeout: {tiempo_espera_general}s).")
            expect(tabla_selector).to_be_visible()
            tabla_selector.highlight()
            self.logger.info("\n✅ Tabla visible. Procediendo a verificar los datos.")

            # 2. Obtener los encabezados para mapear los índices de las columnas
            header_locators = tabla_selector.locator("thead th")
            self.logger.debug(f"\nEsperando que los encabezados (th) de la tabla sean visibles (timeout: {tiempo_espera_general}s).")
            expect(header_locators.first).to_be_visible()
            headers = [h.text_content().strip() for h in header_locators.all()]
            
            if not headers:
                self.logger.error(f"\n❌ --> FALLO: No se encontraron encabezados en la tabla con locator '{tabla_selector}'. No se pueden verificar los datos de las filas.")
                self.base.tomar_captura(f"{nombre_base}_no_headers_para_datos_filas", directorio)
                return False
            self.logger.info(f"\n🔍 Encabezados de la tabla encontrados: {headers}")

            # 3. Obtener todas las filas del cuerpo de la tabla (excluyendo thead)
            tbody_locator = tabla_selector.locator("tbody")
            self.logger.debug(f"\nEsperando que el tbody de la tabla sea visible (timeout: {tiempo_espera_general}s).")
            expect(tbody_locator).to_be_visible()

            row_locators = tbody_locator.locator("tr")
            # Esperar a que al menos la primera fila de datos sea visible si se esperan filas.
            if len(datos_filas_esperados) > 0:
                self.logger.debug(f"\nEsperando que al menos la primera fila de datos sea visible (timeout: {tiempo_espera_general}s).")
                expect(row_locators.first).to_be_visible()

            num_filas_actuales = row_locators.count()
            num_filas_esperadas = len(datos_filas_esperados)

            # 4. Comparar el número total de filas
            if num_filas_actuales == 0 and num_filas_esperadas == 0:
                self.logger.info("\n✅ ÉXITO: No se esperaban filas y no se encontraron filas en la tabla. Verificación completada.")
                self.base.tomar_captura(f"{nombre_base}_no_rows_expected_and_found", directorio)
                # No necesitamos detener el tiempo si no se hizo nada realmente.
                return True
            
            if num_filas_actuales != num_filas_esperadas:
                self.logger.error(f"\n❌ --> FALLO: El número de filas encontradas ({num_filas_actuales}) "
                                  f"no coincide con el número de filas esperadas ({num_filas_esperadas}).")
                self.base.tomar_captura(f"{nombre_base}_cantidad_filas_incorrecta", directorio)
                return False
            self.logger.info(f"\n🔍 Número de filas actual y esperado coinciden: {num_filas_actuales} filas.")

            # --- Variable principal para el retorno ---
            todos_los_datos_correctos = True 

            # 5. Iterar sobre cada fila esperada y verificar sus datos
            for i in range(num_filas_esperadas):
                fila_actual_locator = row_locators.nth(i)
                datos_fila_esperada = datos_filas_esperados[i]
                self.logger.info(f"\n  Verificando Fila {i+1} (Datos esperados: {datos_fila_esperada})...")
                fila_actual_locator.highlight() # Resaltar la fila actual en la captura para debug.

                # Bandera para saber si la fila actual tiene algún fallo
                fila_actual_correcta = True 

                # Iterar sobre las columnas esperadas para esta fila
                for col_name, expected_value in datos_fila_esperada.items():
                    try:
                        # Encontrar el índice de la columna por su nombre
                        if col_name not in headers:
                            self.logger.error(f"\n  ❌ FALLO: Columna '{col_name}' esperada para la Fila {i+1} no encontrada en los encabezados de la tabla. Encabezados actuales: {headers}")
                            self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_columna_{col_name}_no_encontrada", directorio)
                            todos_los_datos_correctos = False # Falla general
                            fila_actual_correcta = False # Falla en esta fila
                            continue # Pasa a la siguiente columna esperada o fila

                        col_index = headers.index(col_name)
                        
                        # Localizar la celda específica (td) dentro de la fila por su índice
                        celda_locator = fila_actual_locator.locator("td").nth(col_index)
                        
                        # Asegurarse de que la celda esté visible antes de interactuar.
                        expect(celda_locator).to_be_visible() # Timeout para celda individual

                        if col_name == "Select": # Lógica específica para el checkbox en la columna "Select"
                            checkbox_locator = celda_locator.locator("input[type='checkbox']")
                            if checkbox_locator.count() == 0: # Si no se encuentra el checkbox dentro de la celda
                                self.logger.error(f"\n  ❌ FALLO: Checkbox no encontrado en la columna '{col_name}' de la Fila {i+1}.")
                                celda_locator.highlight() # Resaltar la celda donde se esperaba el checkbox
                                self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_no_checkbox", directorio)
                                todos_los_datos_correctos = False
                                fila_actual_correcta = False
                            elif isinstance(expected_value, bool): # Si se espera un estado específico (True/False)
                                if checkbox_locator.is_checked() != expected_value:
                                    self.logger.error(f"\n  ❌ FALLO: El checkbox de la Fila {i+1}, Columna '{col_name}' estaba "
                                                      f"{'marcado' if checkbox_locator.is_checked() else 'desmarcado'}, se esperaba {'marcado' if expected_value else 'desmarcado'}.")
                                    checkbox_locator.highlight() # Resaltar el checkbox incorrecto
                                    self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_checkbox_estado_incorrecto", directorio)
                                    todos_los_datos_correctos = False
                                    fila_actual_correcta = False
                                else:
                                    self.logger.info(f"\n  ✅ Fila {i+1}, Columna '{col_name}': Checkbox presente y estado correcto ({'marcado' if expected_value else 'desmarcado'}).")
                            else: # Si se espera que el checkbox exista, pero no se especificó un estado booleano
                                self.logger.info(f"\n  ✅ Fila {i+1}, Columna '{col_name}': Checkbox presente (estado no verificado explícitamente).")
                        else: # Para otras columnas de texto (no checkbox)
                            actual_value = celda_locator.text_content().strip()
                            # Aseguramos que expected_value también sea una cadena para la comparación, eliminando espacios.
                            if actual_value != str(expected_value).strip(): 
                                self.logger.error(f"\n  ❌ FALLO: Fila {i+1}, Columna '{col_name}'. Se esperaba '{expected_value}', se encontró '{actual_value}'.")
                                celda_locator.highlight() # Resaltar la celda con el dato incorrecto
                                self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_col_{col_name}_incorrecta", directorio)
                                todos_los_datos_correctos = False
                                fila_actual_correcta = False
                            else:
                                self.logger.info(f"\n  ✅ Fila {i+1}, Columna '{col_name}': '{actual_value}' coincide con lo esperado.")
                        
                    except TimeoutError as cell_timeout_e:
                        self.logger.error(f"\n  ❌ FALLO (Timeout): La celda de la Fila {i+1}, Columna '{col_name}' no se volvió visible a tiempo. Detalles: {cell_timeout_e}")
                        self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_col_{col_name}_timeout", directorio)
                        todos_los_datos_correctos = False
                        fila_actual_correcta = False
                    except Error as col_playwright_e:
                        self.logger.error(f"\n  ❌ FALLO (Playwright): Error de Playwright al verificar la columna '{col_name}' de la Fila {i+1}. Detalles: {col_playwright_e}")
                        self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_col_{col_name}_playwright_error", directorio)
                        todos_los_datos_correctos = False
                        fila_actual_correcta = False
                    except Exception as col_e:
                        self.logger.error(f"\n  ❌ ERROR INESPERADO al verificar la columna '{col_name}' de la Fila {i+1}: {col_e}", exc_info=True)
                        self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_col_{col_name}_error_inesperado", directorio)
                        todos_los_datos_correctos = False
                        fila_actual_correcta = False
                        # Podrías decidir si quieres continuar con el resto de las columnas/filas
                        # o si este error debe detener la verificación.

                # Pausa solo si la fila actual tuvo algún fallo para que la captura sea más útil
                if not fila_actual_correcta:
                    self.base.esperar_fijo(1) # Pausa de 1 segundo para visualización si hay un fallo en la fila.

            # --- Medición de rendimiento: Fin de la verificación de datos de filas ---
            end_time_row_data_verification = time.time()
            duration_row_data_verification = end_time_row_data_verification - start_time_row_data_verification
            self.logger.info(f"PERFORMANCE: Tiempo total de verificación de datos de filas en la tabla '{tabla_selector}': {duration_row_data_verification:.4f} segundos.")

            # --- Retorno final basado en el estado acumulado ---
            if todos_los_datos_correctos:
                self.logger.info("\n✅ ÉXITO: Todos los datos de las filas y checkboxes son correctos y están presentes.")
                self.base.tomar_captura(f"{nombre_base}_datos_filas_verificados_ok", directorio)
                return True
            else:
                self.logger.error("\n❌ FALLO: Uno o más datos de las filas o checkboxes son incorrectos o faltan.")
                self.base.tomar_captura(f"{nombre_base}_datos_filas_verificados_fallo", directorio)
                return False

        except TimeoutError as e:
            # Captura si la tabla, el thead, el tbody o las filas no se vuelven visibles a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_row_data_verification
            error_msg = (
                f"\n❌ FALLO (Timeout): La tabla, sus encabezados o sus filas con el locator '{tabla_selector}' no se volvieron visibles a tiempo "
                f"después de {duration_fail:.4f} segundos (timeout general configurado: {tiempo_espera_general}s).\n"
                f"Posiblemente la tabla no estuvo disponible a tiempo o tardó demasiado en cargar su contenido.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_verificar_datos_filas_timeout", directorio)
            # Elevar AssertionError para que la prueba falle claramente cuando la tabla no está lista.
            raise AssertionError(f"\nElementos de tabla no disponibles a tiempo para verificación de datos de filas: {tabla_selector}") from e

        except Error as e:
            # Captura errores específicos de Playwright durante la interacción con el DOM de la tabla.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al intentar verificar las filas con el locator '{tabla_selector}'.\n"
                f"Posibles causas: Locator inválido, problemas de interacción con el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_verificar_datos_filas_error_playwright", directorio)
            raise AssertionError(f"\nError de Playwright al verificar datos de filas de tabla: {tabla_selector}") from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada durante la verificación.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error desconocido al verificar los datos de las filas con el locator '{tabla_selector}'.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_verificar_datos_filas_error_inesperado", directorio)
            raise AssertionError(f"\nError inesperado al verificar datos de filas de tabla: {tabla_selector}") from e
    
    # 34- Función para seleccionar y verificar el estado de checkboxes de filas aleatorias, con pruebas de rendimiento.
    def seleccionar_y_verificar_checkboxes_aleatorios(self, tabla_selector: Locator, num_checkboxes_a_interactuar: int, nombre_base: str, directorio: str, tiempo_espera_tabla: Union[int, float] = 1.0, pausa_interaccion: Union[int, float] = 0.5) -> bool:
        """
        Selecciona y verifica el estado de un número específico de checkboxes aleatorios
        dentro de una tabla. Mide el rendimiento de las operaciones de búsqueda e interacción.

        Args:
            tabla_selector (Locator): El **Locator de Playwright** que representa el elemento
                                      `<table>` que contiene los checkboxes a interactuar.
            num_checkboxes_a_interactuar (int): El **número de checkboxes aleatorios** a
                                                seleccionar y verificar.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_tabla (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                     para que la tabla y sus checkboxes estén
                                                     visibles y listos. Por defecto, `10.0` segundos.
            pausa_interaccion (Union[int, float]): **Pausa opcional** (en segundos) después de
                                                   cada interacción con un checkbox para permitir
                                                   que el DOM se actualice visualmente. Por defecto, `0.5` segundos.

        Returns:
            bool: `True` si todos los checkboxes seleccionados aleatoriamente fueron
                  interactuados y verificados correctamente; `False` en caso contrario.

        Raises:
            AssertionError: Si la tabla o sus checkboxes no están disponibles a tiempo,
                            o si ocurre un error inesperado de Playwright o genérico
                            que impida la interacción.
        """
        self.logger.info(f"\n--- Iniciando selección y verificación de {num_checkboxes_a_interactuar} checkbox(es) aleatorio(s) en la tabla con locator '{tabla_selector}' ---")
        self.base.tomar_captura(f"{nombre_base}_inicio_seleccion_checkbox", directorio)

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Asegurarse de que la tabla esté visible
            self.logger.debug(f"\nEsperando que la tabla con selector '{tabla_selector}' esté visible (timeout: {tiempo_espera_tabla}s).")
            expect(tabla_selector).to_be_visible()
            tabla_selector.highlight()
            self.logger.info("\n✅ Tabla visible. Procediendo a buscar checkboxes.")

            # --- Medición de rendimiento: Inicio del descubrimiento de checkboxes ---
            start_time_discovery = time.time()

            # 2. Obtener todos los locators de los checkboxes en las celdas del cuerpo de la tabla
            all_checkbox_locators = tabla_selector.locator("tbody tr td input[type='checkbox']")
            
            # Asegurarse de que al menos un checkbox sea visible si esperamos interactuar.
            if num_checkboxes_a_interactuar > 0:
                self.logger.debug(f"\nEsperando que al menos un checkbox en la tabla sea visible (timeout: {tiempo_espera_tabla}s).")
                expect(all_checkbox_locators.first).to_be_visible()

            num_checkboxes_disponibles = all_checkbox_locators.count()

            # --- Medición de rendimiento: Fin del descubrimiento de checkboxes ---
            end_time_discovery = time.time()
            duration_discovery = end_time_discovery - start_time_discovery
            self.logger.info(f"PERFORMANCE: Tiempo de descubrimiento de checkboxes disponibles: {duration_discovery:.4f} segundos. ({num_checkboxes_disponibles} encontrados)")

            if num_checkboxes_disponibles == 0:
                self.logger.error(f"\n❌ --> FALLO: No se encontraron checkboxes en la tabla con locator '{tabla_selector.locator('tbody tr td input[type=\"checkbox\"]')}'.")
                self.base.tomar_captura(f"{nombre_base}_no_checkboxes_encontrados", directorio)
                return False
            
            if num_checkboxes_a_interactuar <= 0:
                self.logger.warning("\n⚠️ ADVERTENCIA: El número de checkboxes a interactuar es 0 o negativo. No se realizará ninguna acción.")
                return True

            if num_checkboxes_a_interactuar > num_checkboxes_disponibles:
                self.logger.error(f"\n❌ --> FALLO: Se solicitaron {num_checkboxes_a_interactuar} checkboxes para interactuar, pero solo hay {num_checkboxes_disponibles} disponibles.")
                self.base.tomar_captura(f"{nombre_base}_no_suficientes_checkboxes", directorio)
                return False

            self.logger.info(f"\nSe encontraron {num_checkboxes_disponibles} checkboxes. Seleccionando {num_checkboxes_a_interactuar} aleatoriamente...")

            # 3. Seleccionar N índices de checkboxes aleatorios y únicos
            random_indices = random.sample(range(num_checkboxes_disponibles), num_checkboxes_a_interactuar)
            
            todos_correctos = True
            interaction_times = [] # Lista para almacenar tiempos de interacción individuales

            # 4. Iterar sobre los checkboxes seleccionados aleatoriamente e interactuar con ellos
            for i, idx in enumerate(random_indices):
                checkbox_to_interact = all_checkbox_locators.nth(idx)
                
                # --- Medición de rendimiento: Inicio de interacción individual ---
                start_time_interaction = time.time()

                # Resaltar el checkbox actual para la captura/visualización
                checkbox_to_interact.highlight()
                self.base.tomar_captura(f"{nombre_base}_checkbox_{i+1}_aleatorio_idx_{idx}_resaltado", directorio)
                self.base.esperar_fijo(pausa_interaccion) # Pausa para ver el resaltado

                # Obtener el ID del producto asociado a esta fila (asumiendo ID en la primera columna)
                product_id = "N/A" # Default en caso de error
                try:
                    # Encontrar la fila que contiene este checkbox para obtener información de contexto.
                    # Esto es un poco más complejo si el checkbox no está en la primera columna,
                    # pero si asumimos que está dentro de un 'td' de un 'tr' que representa una fila:
                    # Podemos buscar el ancestro 'tr' y luego el primer 'td' de ese 'tr'.
                    # Podría ser más robusto si el product ID estuviera en un atributo de datos,
                    # o si el checkbox tuviera un atributo id/name relacionado con el producto.
                    row_locator_for_id = checkbox_to_interact.locator("..").locator("..") # Sube dos niveles para llegar al 'tr'
                    # Asegurarse de que el 'td' existe en la primera posición.
                    if row_locator_for_id.locator("td").count() > 0:
                        product_id = row_locator_for_id.locator("td").nth(0).text_content().strip()
                    else:
                        self.logger.warning(f"No se pudo extraer el ID del producto para la fila del checkbox en el índice {idx}. La primera celda (td[0]) no fue encontrada o no tiene texto.")
                except Exception as id_e:
                    self.logger.warning(f"Error al intentar obtener el ID del producto para el checkbox en el índice {idx}: {id_e}")
                
                initial_state = checkbox_to_interact.is_checked()
                self.logger.info(f"\n  Checkbox del Producto ID: {product_id} (Fila índice: {idx}, Interacción {i+1}/{num_checkboxes_a_interactuar}): Estado inicial {'MARCADO' if initial_state else 'DESMARCADO'}.")

                # --- Lógica para asegurar que el click lo deje en estado 'seleccionado' (marcado) ---
                if initial_state: # Si ya está marcado, lo desmarcamos primero para asegurar la acción de marcar
                    self.logger.info(f"\n  El checkbox del Producto ID: {product_id} ya está MARCADO. Haciendo clic para desmarcar antes de seleccionar.")
                    checkbox_to_interact.uncheck()
                    self.base.esperar_fijo(pausa_interaccion) # Pausa para que el DOM se actualice

                    if checkbox_to_interact.is_checked(): # Si después de uncheck sigue marcado, es un fallo
                        self.logger.error(f"\n  ❌ FALLO: El checkbox del Producto ID: {product_id} no se desmarcó correctamente para la interacción.")
                        checkbox_to_interact.highlight()
                        self.base.tomar_captura(f"{nombre_base}_fila_{idx+1}_no_se_desmarco", directorio)
                        todos_correctos = False
                        # No es necesario continuar con la verificación de 'check' si el 'uncheck' ya falló.
                        # Continua al siguiente checkbox aleatorio.
                        continue 
                
                # Ahora el checkbox debería estar DESMARCADO (o siempre lo estuvo si initial_state era False)
                self.logger.info(f"\n  Haciendo clic en el checkbox del Producto ID: {product_id} para MARCARLO...")
                checkbox_to_interact.check() # Marca el checkbox
                self.base.esperar_fijo(pausa_interaccion) # Pausa para que el DOM se actualice

                final_state = checkbox_to_interact.is_checked()
                if not final_state: # Si no está marcado (seleccionado) después del clic
                    self.logger.error(f"\n  ❌ FALLO: El checkbox del Producto ID: {product_id} no cambió a MARCADO después del clic. Sigue DESMARCADO.")
                    checkbox_to_interact.highlight()
                    self.base.tomar_captura(f"{nombre_base}_fila_{idx+1}_no_se_marco", directorio)
                    todos_correctos = False
                else:
                    self.logger.info(f"\n  ✅ ÉXITO: El checkbox del Producto ID: {product_id} ahora está MARCADO (seleccionado).")
                    self.base.tomar_captura(f"{nombre_base}_fila_{idx+1}_marcado_ok", directorio)
                
                # --- Medición de rendimiento: Fin de interacción individual ---
                end_time_interaction = time.time()
                duration_interaction = end_time_interaction - start_time_interaction
                interaction_times.append(duration_interaction)
                self.logger.info(f"PERFORMANCE: Tiempo de interacción para checkbox {i+1} (Producto ID: {product_id}): {duration_interaction:.4f} segundos.")

            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación de selección y verificación de checkboxes: {duration_total_operation:.4f} segundos.")

            if interaction_times:
                avg_interaction_time = sum(interaction_times) / len(interaction_times)
                self.logger.info(f"PERFORMANCE: Tiempo promedio de interacción por checkbox: {avg_interaction_time:.4f} segundos.")

            if todos_correctos:
                self.logger.info(f"\n✅ ÉXITO: Todos los {num_checkboxes_a_interactuar} checkbox(es) aleatorio(s) fueron seleccionados y verificados correctamente.")
                self.base.tomar_captura(f"{nombre_base}_todos_seleccionados_ok", directorio)
                return True
            else:
                self.logger.error(f"\n❌ FALLO: Uno o más checkbox(es) aleatorio(s) no pudieron ser seleccionados o verificados.")
                self.base.tomar_captura(f"{nombre_base}_fallo_general_seleccion", directorio)
                return False

        except TimeoutError as e:
            # Captura si la tabla o los checkboxes no se vuelven visibles a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Timeout): No se pudo encontrar la tabla o los checkboxes con el locator '{tabla_selector}'.\n"
                f"Posiblemente los elementos no estuvieron disponibles a tiempo después de {duration_fail:.4f} segundos (timeout configurado: {tiempo_espera_tabla}s).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_seleccion_checkbox_timeout", directorio)
            raise AssertionError(f"\nElementos de tabla/checkboxes no disponibles a tiempo para interacción: {tabla_selector}") from e

        except Error as e:
            # Captura errores específicos de Playwright durante la interacción con los checkboxes.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al seleccionar y verificar checkboxes en la tabla '{tabla_selector}'.\n"
                f"Posibles causas: Locator inválido, problemas de interacción con el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_seleccion_checkbox_error_playwright", directorio)
            raise AssertionError(f"\nError de Playwright al interactuar con checkboxes: {tabla_selector}") from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al seleccionar y verificar checkboxes aleatorios.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_seleccion_checkbox_error_inesperado", directorio)
            raise AssertionError(f"\nError inesperado al interactuar con checkboxes: {tabla_selector}") from e
    
    # 35- Función para seleccionar y verificar el estado de checkboxes de filas CONSECUTIVAS, con pruebas de rendimiento.
    def seleccionar_y_verificar_checkboxes_consecutivos(self, tabla_selector: Locator, start_index: int, num_checkboxes_a_interactuar: int, nombre_base: str, directorio: str, tiempo_espera_tabla: Union[int, float] = 1.0, pausa_interaccion: Union[int, float] = 0.5) -> bool:
        """
        Selecciona y verifica el estado de un número específico de checkboxes en filas consecutivas
        dentro de una tabla, comenzando desde un índice dado. Mide el rendimiento de las
        operaciones de búsqueda e interacción.

        Args:
            tabla_selector (Locator): El **Locator de Playwright** que representa el elemento
                                      `<table>` que contiene los checkboxes a interactuar.
            start_index (int): El **índice de la primera fila** (basado en 0) donde se encuentra
                                el primer checkbox consecutivo a interactuar.
            num_checkboxes_a_interactuar (int): El **número de checkboxes consecutivos** a
                                                seleccionar y verificar a partir de `start_index`.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_tabla (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                     para que la tabla y sus checkboxes estén
                                                     visibles y listos. Por defecto, `10.0` segundos.
            pausa_interaccion (Union[int, float]): **Pausa opcional** (en segundos) después de
                                                   cada interacción con un checkbox para permitir
                                                   que el DOM se actualice visualmente. Por defecto, `0.5` segundos.

        Returns:
            bool: `True` si todos los checkboxes consecutivos fueron interactuados y
                  verificados correctamente; `False` en caso contrario.

        Raises:
            AssertionError: Si la tabla o sus checkboxes no están disponibles a tiempo,
                            o si ocurre un error inesperado de Playwright o genérico
                            que impida la interacción.
        """
        self.logger.info(f"\n--- Iniciando selección y verificación de {num_checkboxes_a_interactuar} checkbox(es) consecutivo(s) "
                         f"a partir del índice {start_index} en la tabla con locator '{tabla_selector}' ---")
        self.base.tomar_captura(f"{nombre_base}_inicio_seleccion_consecutiva_checkbox", directorio)

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Asegurarse de que la tabla esté visible
            self.logger.debug(f"\nEsperando que la tabla con selector '{tabla_selector}' esté visible (timeout: {tiempo_espera_tabla}s).")
            expect(tabla_selector).to_be_visible()
            tabla_selector.highlight()
            self.logger.info("\n✅ Tabla visible. Procediendo a buscar checkboxes.")

            # --- Medición de rendimiento: Inicio del descubrimiento de checkboxes ---
            start_time_discovery = time.time()

            # 2. Obtener todos los locators de los checkboxes en las celdas del cuerpo de la tabla
            all_checkbox_locators = tabla_selector.locator("tbody tr td input[type='checkbox']")
            
            # Asegurarse de que al menos un checkbox sea visible si esperamos interactuar.
            if num_checkboxes_a_interactuar > 0:
                self.logger.debug(f"\nEsperando que al menos el primer checkbox en el rango deseado sea visible (timeout: {tiempo_espera_tabla}s).")
                # Intentamos esperar al primer checkbox de la secuencia.
                if num_checkboxes_a_interactuar > 0 and start_index < all_checkbox_locators.count():
                    expect(all_checkbox_locators.nth(start_index)).to_be_visible()
                elif num_checkboxes_a_interactuar > 0: # Si el start_index es inválido, pero aún se esperan interacciones
                    # Esto será capturado por las validaciones de rango más adelante.
                    pass 

            num_checkboxes_disponibles = all_checkbox_locators.count()

            # --- Medición de rendimiento: Fin del descubrimiento de checkboxes ---
            end_time_discovery = time.time()
            duration_discovery = end_time_discovery - start_time_discovery
            self.logger.info(f"PERFORMANCE: Tiempo de descubrimiento de checkboxes disponibles: {duration_discovery:.4f} segundos. ({num_checkboxes_disponibles} encontrados)")

            # 3. Validaciones de precondición
            if num_checkboxes_disponibles == 0:
                self.logger.error(f"\n❌ --> FALLO: No se encontraron checkboxes en la tabla con locator '{tabla_selector.locator('tbody tr td input[type=\"checkbox\"]')}'.")
                self.base.tomar_captura(f"{nombre_base}_no_checkboxes_encontrados_consec", directorio)
                return False
            
            if num_checkboxes_a_interactuar <= 0:
                self.logger.warning("\n⚠️ ADVERTENCIA: El número de checkboxes a interactuar es 0 o negativo. No se realizará ninguna acción.")
                return True # Consideramos éxito si no hay nada que hacer

            if start_index < 0 or start_index >= num_checkboxes_disponibles:
                self.logger.error(f"\n❌ --> FALLO: El 'posición de inicio' ({start_index}) está fuera del rango válido de checkboxes disponibles (0 a {num_checkboxes_disponibles - 1}).")
                self.base.tomar_captura(f"{nombre_base}_start_index_invalido_consec", directorio)
                return False
            
            if (start_index + num_checkboxes_a_interactuar) > num_checkboxes_disponibles:
                self.logger.error(f"\n❌ --> FALLO: Se solicitaron {num_checkboxes_a_interactuar} checkboxes a partir del índice {start_index}, "
                                  f"pero solo hay {num_checkboxes_disponibles} disponibles. El rango excede los límites de la tabla.")
                self.base.tomar_captura(f"{nombre_base}_rango_excedido_consec", directorio)
                return False

            self.logger.info(f"\nInteractuando con {num_checkboxes_a_interactuar} checkbox(es) consecutivo(s) "
                             f"desde el índice {start_index} hasta el {start_index + num_checkboxes_a_interactuar - 1}...")
            
            todos_correctos = True
            interaction_times = [] # Lista para almacenar tiempos de interacción individuales

            # 4. Iterar sobre los checkboxes consecutivos e interactuar con ellos
            for i in range(num_checkboxes_a_interactuar):
                current_idx = start_index + i
                checkbox_to_interact = all_checkbox_locators.nth(current_idx)
                
                # --- Medición de rendimiento: Inicio de interacción individual ---
                start_time_interaction = time.time()

                # Resaltar el checkbox actual para la captura/visualización
                checkbox_to_interact.highlight()
                self.base.tomar_captura(f"{nombre_base}_checkbox_consecutivo_{i+1}_idx_{current_idx}_resaltado", directorio)
                self.base.esperar_fijo(pausa_interaccion) # Pausa para ver el resaltado

                # Obtener el ID del producto asociado a esta fila (asumiendo ID en la primera columna)
                product_id = "N/A" # Default en caso de error
                try:
                    # Se asume que el checkbox está dentro de un 'td' y este 'td' está dentro de un 'tr'.
                    # Se suben dos niveles para llegar al 'tr' y luego se busca el primer 'td'.
                    row_locator_for_id = checkbox_to_interact.locator("..").locator("..") 
                    if row_locator_for_id.locator("td").count() > 0:
                        product_id = row_locator_for_id.locator("td").nth(0).text_content().strip()
                    else:
                        self.logger.warning(f"No se pudo extraer el ID del producto para la fila del checkbox en el índice {current_idx}. La primera celda (td[0]) no fue encontrada o no tiene texto.")
                except Exception as id_e:
                    self.logger.warning(f"Error al intentar obtener el ID del producto para el checkbox en el índice {current_idx}: {id_e}")
                
                initial_state = checkbox_to_interact.is_checked()
                self.logger.info(f"\n  Checkbox del Producto ID: {product_id} (Fila índice: {current_idx}, Interacción {i+1}/{num_checkboxes_a_interactuar}): Estado inicial {'MARCADO' if initial_state else 'DESMARCADO'}.")

                # --- Lógica para asegurar que el click lo deje en estado 'seleccionado' (marcado) ---
                if initial_state: # Si ya está marcado, lo desmarcamos primero para asegurar la acción de marcar
                    self.logger.info(f"\n  El checkbox del Producto ID: {product_id} ya está MARCADO. Haciendo clic para desmarcar antes de seleccionar.")
                    checkbox_to_interact.uncheck()
                    self.base.esperar_fijo(pausa_interaccion) # Pausa para que el DOM se actualice

                    if checkbox_to_interact.is_checked(): # Si después de uncheck sigue marcado, es un fallo
                        self.logger.error(f"\n  ❌ FALLO: El checkbox del Producto ID: {product_id} no se desmarcó correctamente para la interacción.")
                        checkbox_to_interact.highlight()
                        self.base.tomar_captura(f"{nombre_base}_fila_{current_idx+1}_no_se_desmarco_consec", directorio)
                        todos_correctos = False
                        # No es necesario continuar con la verificación de 'check' si el 'uncheck' ya falló.
                        continue 
                
                # Ahora el checkbox debería estar DESMARCADO (o siempre lo estuvo si initial_state era False)
                self.logger.info(f"\n  Haciendo clic en el checkbox del Producto ID: {product_id} para MARCARLO...")
                checkbox_to_interact.check() # Marca el checkbox
                self.base.esperar_fijo(pausa_interaccion) # Pausa para que el DOM se actualice

                final_state = checkbox_to_interact.is_checked()
                if not final_state: # Si no está marcado (seleccionado) después del clic
                    self.logger.error(f"\n  ❌ FALLO: El checkbox del Producto ID: {product_id} no cambió a MARCADO después del clic. Sigue DESMARCADO.")
                    checkbox_to_interact.highlight()
                    self.base.tomar_captura(f"{nombre_base}_fila_{current_idx+1}_no_se_marco_consec", directorio)
                    todos_correctos = False
                else:
                    self.logger.info(f"\n  ✅ ÉXITO: El checkbox del Producto ID: {product_id} ahora está MARCADO (seleccionado).")
                    self.base.tomar_captura(f"{nombre_base}_fila_{current_idx+1}_marcado_ok_consec", directorio)
                
                # --- Medición de rendimiento: Fin de interacción individual ---
                end_time_interaction = time.time()
                duration_interaction = end_time_interaction - start_time_interaction
                interaction_times.append(duration_interaction)
                self.logger.info(f"PERFORMANCE: Tiempo de interacción para checkbox {i+1} (Producto ID: {product_id}): {duration_interaction:.4f} segundos.")

            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación de selección y verificación de checkboxes consecutivos: {duration_total_operation:.4f} segundos.")

            if interaction_times:
                avg_interaction_time = sum(interaction_times) / len(interaction_times)
                self.logger.info(f"PERFORMANCE: Tiempo promedio de interacción por checkbox: {avg_interaction_time:.4f} segundos.")

            if todos_correctos:
                self.logger.info(f"\n✅ ÉXITO: Todos los {num_checkboxes_a_interactuar} checkbox(es) consecutivo(s) fueron seleccionados y verificados correctamente.")
                self.base.tomar_captura(f"{nombre_base}_todos_seleccionados_ok_consec", directorio)
                return True
            else:
                self.logger.error(f"\n❌ FALLO: Uno o más checkbox(es) consecutivo(s) no pudieron ser seleccionados o verificados.")
                self.base.tomar_captura(f"{nombre_base}_fallo_general_seleccion_consec", directorio)
                return False

        except TimeoutError as e:
            # Captura si la tabla o los checkboxes no se vuelven visibles a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Timeout): No se pudo encontrar la tabla o los checkboxes con el locator '{tabla_selector}'.\n"
                f"Posiblemente los elementos no estuvieron disponibles a tiempo después de {duration_fail:.4f} segundos (timeout configurado: {tiempo_espera_tabla}s).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_seleccion_consec_checkbox_timeout", directorio)
            raise AssertionError(f"\nElementos de tabla/checkboxes no disponibles a tiempo para interacción: {tabla_selector}") from e

        except Error as e:
            # Captura errores específicos de Playwright durante la interacción con los checkboxes.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al seleccionar y verificar checkboxes consecutivos en la tabla '{tabla_selector}'.\n"
                f"Posibles causas: Locator inválido, problemas de interacción con el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_seleccion_consec_checkbox_error_playwright", directorio)
            raise AssertionError(f"\nError de Playwright al interactuar con checkboxes: {tabla_selector}") from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al seleccionar y verificar checkboxes consecutivos.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_seleccion_consec_checkbox_error_inesperado", directorio)
            raise AssertionError(f"\nError inesperado al interactuar con checkboxes: {tabla_selector}") from e
        
    # 36- Función para deseleccionar todos los checkboxes actualmente marcados y verificar su estado.
    def deseleccionar_y_verificar_checkbox_marcado(self, tabla_selector: Locator, nombre_base: str, directorio: str, tiempo_espera_tabla: Union[int, float] = 1.0, pausa_interaccion: Union[int, float] = 0.5) -> bool:
        """
        Deselecciona y verifica el estado de **todos** los checkboxes que se encuentren
        actualmente marcados dentro de una tabla específica. Mide el rendimiento de
        las operaciones de búsqueda y deselección.

        Args:
            tabla_selector (Locator): El **Locator de Playwright** que representa el elemento
                                      `<table>` que contiene los checkboxes a interactuar.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_tabla (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                     para que la tabla y sus checkboxes estén
                                                     visibles y listos. Por defecto, `10.0` segundos.
            pausa_interaccion (Union[int, float]): **Pausa opcional** (en segundos) después de
                                                   cada deselección con un checkbox para permitir
                                                   que el DOM se actualice visualmente. Por defecto, `0.5` segundos.

        Returns:
            bool: `True` si todos los checkboxes que estaban marcados fueron deseleccionados
                  y verificados correctamente; `False` en caso contrario.

        Raises:
            AssertionError: Si la tabla o sus checkboxes no están disponibles a tiempo,
                            o si ocurre un error inesperado de Playwright o genérico
                            que impida la interacción.
        """
        self.logger.info(f"\n--- Iniciando deselección y verificación de TODOS los checkboxes marcados "
                         f"en la tabla con locator '{tabla_selector}' ---")
        self.base.tomar_captura(f"{nombre_base}_inicio_deseleccion_todos_marcados", directorio)

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Asegurarse de que la tabla esté visible
            self.logger.debug(f"\nEsperando que la tabla con selector '{tabla_selector}' esté visible (timeout: {tiempo_espera_tabla}s).")
            expect(tabla_selector).to_be_visible()
            tabla_selector.highlight()
            self.logger.info("\n✅ Tabla visible. Procediendo a buscar checkboxes.")

            # --- Medición de rendimiento: Inicio del descubrimiento de checkboxes ---
            start_time_discovery = time.time()

            # 2. Obtener todos los locators de los checkboxes en las celdas de la tabla
            all_checkbox_locators = tabla_selector.locator("tbody tr td input[type='checkbox']")
            
            # Asegurarse de que al menos un checkbox sea visible si esperamos interactuar (si no hay ninguno, lo gestionamos)
            if all_checkbox_locators.count() > 0:
                self.logger.debug(f"\nEsperando que al menos un checkbox en la tabla sea visible (timeout: {tiempo_espera_tabla}s).")
                expect(all_checkbox_locators.first).to_be_visible()

            num_checkboxes_disponibles = all_checkbox_locators.count()

            if num_checkboxes_disponibles == 0:
                self.logger.error(f"\n❌ --> FALLO: No se encontraron checkboxes en la tabla con locator '{tabla_selector.locator('tbody tr td input[type=\"checkbox\"]')}'.")
                self.base.tomar_captura(f"{nombre_base}_no_checkboxes_encontrados_todos", directorio)
                return False
            
            # 3. Recolectar todos los checkboxes que están actualmente marcados para deseleccionar
            checkboxes_to_deselect = []
            for i in range(num_checkboxes_disponibles):
                checkbox = all_checkbox_locators.nth(i)
                if checkbox.is_checked():
                    checkboxes_to_deselect.append({"locator": checkbox, "original_index": i})
            
            # --- Medición de rendimiento: Fin del descubrimiento de checkboxes ---
            end_time_discovery = time.time()
            duration_discovery = end_time_discovery - start_time_discovery
            self.logger.info(f"PERFORMANCE: Tiempo de descubrimiento de checkboxes y filtrado de marcados: {duration_discovery:.4f} segundos. ({len(checkboxes_to_deselect)} marcados encontrados de {num_checkboxes_disponibles} disponibles)")

            if not checkboxes_to_deselect:
                self.logger.warning("\n⚠️ ADVERTENCIA: No se encontró ningún checkbox actualmente MARCADO en la tabla para deseleccionar. La función finaliza sin acciones de deselección.")
                self.base.tomar_captura(f"{nombre_base}_no_marcados_para_deseleccionar", directorio)
                return True # Consideramos éxito si no hay nada que deseleccionar

            self.logger.info(f"\nSe encontraron {len(checkboxes_to_deselect)} checkbox(es) marcado(s) para deseleccionar. Iniciando el proceso...")

            todos_deseleccionados_correctamente = True
            interaction_times = [] # Lista para almacenar tiempos de interacción individuales

            # 4. Iterar sobre los checkboxes marcados y deseleccionarlos
            for i, checkbox_info in enumerate(checkboxes_to_deselect):
                checkbox_to_interact = checkbox_info["locator"]
                original_idx = checkbox_info["original_index"]
                
                # --- Medición de rendimiento: Inicio de interacción individual ---
                start_time_interaction = time.time()

                # Resaltar el checkbox actual
                checkbox_to_interact.highlight()
                self.base.tomar_captura(f"{nombre_base}_deseleccion_actual_{i+1}_idx_{original_idx}_resaltado", directorio)
                self.base.esperar_fijo(pausa_interaccion)

                # Obtener el ID del producto asociado a esta fila (asumiendo ID en la primera columna)
                product_id = "N/A" # Default en caso de error
                try:
                    # Se asume que el checkbox está dentro de un 'td' y este 'td' dentro de un 'tr'.
                    # Se suben dos niveles para llegar al 'tr' y luego se busca el primer 'td'.
                    row_locator_for_id = checkbox_to_interact.locator("..").locator("..")
                    if row_locator_for_id.locator("td").count() > 0:
                        product_id = row_locator_for_id.locator("td").nth(0).text_content().strip()
                    else:
                        self.logger.warning(f"No se pudo extraer el ID del producto para la fila del checkbox en el índice {original_idx}. La primera celda (td[0]) no fue encontrada o no tiene texto.")
                except Exception as id_e:
                    self.logger.warning(f"Error al intentar obtener el ID del producto para el checkbox en el índice {original_idx}: {id_e}")
                
                self.logger.info(f"\n  Procesando checkbox del Producto ID: {product_id} (Fila índice: {original_idx}, Interacción {i+1}/{len(checkboxes_to_deselect)}). Estado inicial: MARCADO (esperado).")

                # --- Interacción: Clic para deseleccionar ---
                self.logger.info(f"\n  Haciendo clic en el checkbox del Producto ID: {product_id} para DESMARCARLO...")
                # Usar .uncheck() es más directo para desmarcar que .click() si ya sabes el estado esperado.
                checkbox_to_interact.uncheck()
                self.base.esperar_fijo(pausa_interaccion) # Pausa para que el DOM se actualice

                final_state = checkbox_to_interact.is_checked()
                if final_state: # Si sigue marcado después de .uncheck()
                    self.logger.error(f"\n  ❌ FALLO: El checkbox del Producto ID: {product_id} no cambió a DESMARCADO después del clic. Sigue MARCADO.")
                    checkbox_to_interact.highlight()
                    self.base.tomar_captura(f"{nombre_base}_fila_{original_idx+1}_no_desmarcado", directorio)
                    todos_deseleccionados_correctamente = False
                else:
                    self.logger.info(f"\n  ✅ ÉXITO: El checkbox del Producto ID: {product_id} ahora está DESMARCADO (deseleccionado).")
                    self.base.tomar_captura(f"{nombre_base}_fila_{original_idx+1}_desmarcado_ok", directorio)
                
                # --- Medición de rendimiento: Fin de interacción individual ---
                end_time_interaction = time.time()
                duration_interaction = end_time_interaction - start_time_interaction
                interaction_times.append(duration_interaction)
                self.logger.info(f"PERFORMANCE: Tiempo de deselección para checkbox {i+1} (Producto ID: {product_id}): {duration_interaction:.4f} segundos.")

            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación de deselección y verificación de checkboxes: {duration_total_operation:.4f} segundos.")

            if interaction_times:
                avg_interaction_time = sum(interaction_times) / len(interaction_times)
                self.logger.info(f"PERFORMANCE: Tiempo promedio de deselección por checkbox: {avg_interaction_time:.4f} segundos.")


            if todos_deseleccionados_correctamente:
                self.logger.info(f"\n✅ ÉXITO: Todos los {len(checkboxes_to_deselect)} checkbox(es) marcados fueron deseleccionados y verificados correctamente.")
                self.base.tomar_captura(f"{nombre_base}_todos_deseleccionados_ok", directorio)
                return True
            else:
                self.logger.error(f"\n❌ FALLO: Uno o más checkbox(es) marcados no pudieron ser deseleccionados o verificados.")
                self.base.tomar_captura(f"{nombre_base}_fallo_general_deseleccion_todos", directorio)
                return False

        except TimeoutError as e:
            # Captura si la tabla o los checkboxes no se vuelven visibles a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Timeout): No se pudo encontrar la tabla o los checkboxes con el locator '{tabla_selector}'.\n"
                f"Posiblemente los elementos no estuvieron disponibles a tiempo después de {duration_fail:.4f} segundos (timeout configurado: {tiempo_espera_tabla}s).\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_deseleccion_todos_timeout", directorio)
            raise AssertionError(f"\nElementos de tabla/checkboxes no disponibles a tiempo para interacción: {tabla_selector}") from e

        except Error as e:
            # Captura errores específicos de Playwright durante la interacción con los checkboxes.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al deseleccionar y verificar todos los checkboxes marcados en la tabla '{tabla_selector}'.\n"
                f"Posibles causas: Locator inválido, problemas de interacción con el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_deseleccion_todos_error_playwright", directorio)
            raise AssertionError(f"\nError de Playwright al interactuar con checkboxes: {tabla_selector}") from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al deseleccionar y verificar todos los checkboxes marcados.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_deseleccion_todos_error_inesperado", directorio)
            raise AssertionError(f"\nError inesperado al interactuar con checkboxes: {tabla_selector}") from e
    
    # 37- Función para buscar un 'texto_a_buscar' en las celdas de una tabla (tbody) y, si lo encuentra,
    # intenta marcar el checkbox asociado en la misma fila. Incluye pruebas de rendimiento.
    def seleccionar_checkbox_por_contenido_celda(self, tabla_selector: Locator, texto_a_buscar: str, nombre_base: str, directorio: str, case_sensitive: bool = False, tiempo_espera_tabla: Union[int, float] = 1.0, pausa_interaccion: Union[int, float] = 0.5) -> bool:
        """
        Busca un 'texto_a_buscar' en todas las celdas (<td>) del cuerpo de una tabla (<tbody>).
        Si encuentra el texto en una celda, intenta localizar y marcar el checkbox
        asociado en la misma fila. Mide el rendimiento de la búsqueda y la interacción.

        Args:
            tabla_selector (Locator): El **Locator de Playwright** que representa el elemento
                                      `<table>` que contiene las filas y checkboxes.
            texto_a_buscar (str): El **texto exacto o parcial** a buscar dentro de las celdas de la tabla.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            case_sensitive (bool): Si es `True`, la búsqueda de texto será **sensible a mayúsculas y minúsculas**.
                                   Por defecto, `False` (insensible).
            tiempo_espera_tabla (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                     para que la tabla esté visible y cargada.
                                                     Por defecto, `10.0` segundos.
            pausa_interaccion (Union[int, float]): **Pausa opcional** (en segundos) después de
                                                   resaltar la fila y de marcar el checkbox,
                                                   para permitir la actualización visual. Por defecto, `0.5` segundos.

        Returns:
            bool: `True` si se encontró al menos una coincidencia y se pudo marcar un checkbox asociado;
                  `False` si no se encontraron coincidencias o si hubo errores críticos.

        Raises:
            AssertionError: Si la tabla no está disponible a tiempo, o si ocurre un error
                            inesperado de Playwright o genérico durante la interacción.
        """
        self.logger.info(f"\n--- Iniciando búsqueda de '{texto_a_buscar}' en la tabla '{tabla_selector}' para marcar checkboxes ---")
        self.base.tomar_captura(f"{nombre_base}_inicio_busqueda_celdas", directorio)

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Asegurarse de que la tabla está visible y cargada
            self.logger.debug(f"Esperando que la tabla con selector '{tabla_selector}' esté visible (timeout: {tiempo_espera_tabla}s).")
            # Convertir timeout de segundos a milisegundos para expect()
            expect(tabla_selector).to_be_visible() 
            tabla_selector.highlight()
            self.logger.info("\n✅ Tabla visible. Comenzando a iterar por filas y celdas.")

            # --- Medición de rendimiento: Inicio del escaneo de la tabla ---
            start_time_scan = time.time()

            # Obtener todas las filas del cuerpo de la tabla
            filas = tabla_selector.locator("tbody tr")
            num_filas = filas.count()

            if num_filas == 0:
                self.logger.error(f"\n❌ --> FALLO: No se encontraron filas en el 'tbody' de la tabla con locator '{tabla_selector}'.")
                self.base.tomar_captura(f"{nombre_base}_no_filas_encontradas", directorio)
                return False

            self.logger.info(f"\nSe encontraron {num_filas} filas en la tabla. Iniciando escaneo de celdas...")
            
            checkboxes_marcados_exitosamente = 0
            
            # Normalizar el texto de búsqueda si no es sensible a mayúsculas/minúsculas
            search_text_normalized = texto_a_buscar if case_sensitive else texto_a_buscar.lower()
            
            found_any_match = False # Bandera para saber si se encontró al menos una coincidencia
            interaction_times = [] # Para medir el tiempo de marcado de cada checkbox

            for i in range(num_filas):
                fila_actual = filas.nth(i)
                # Obtener todas las celdas (td) de la fila actual
                celdas = fila_actual.locator("td")
                num_celdas = celdas.count()

                if num_celdas == 0:
                    self.logger.warning(f"\n  ADVERTENCIA: La fila {i+1} no contiene celdas (td). Saltando.")
                    continue

                celda_encontrada_en_fila = False
                for j in range(num_celdas):
                    celda_actual = celdas.nth(j)
                    celda_texto = celda_actual.text_content().strip()
                    
                    # Normalizar el texto de la celda para la comparación
                    celda_texto_normalized = celda_texto if case_sensitive else celda_texto.lower()

                    if search_text_normalized in celda_texto_normalized:
                        self.logger.info(f"\n  ✅ Coincidencia encontrada en Fila {i+1}, Celda {j+1}: '{celda_texto}' contiene '{texto_a_buscar}'.")
                        celda_encontrada_en_fila = True
                        found_any_match = True
                        
                        # Buscar el checkbox dentro de la misma fila
                        checkbox_locator = fila_actual.locator("input[type='checkbox']")
                        
                        if checkbox_locator.count() > 0:
                            checkbox = checkbox_locator.first
                            checkbox.highlight()
                            self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_coincidencia_resaltada", directorio)
                            self.base.esperar_fijo(pausa_interaccion)

                            # --- Medición de rendimiento: Inicio de interacción de checkbox ---
                            start_time_checkbox_interaction = time.time()

                            if not checkbox.is_checked():
                                self.logger.info(f"\n  --> Marcando checkbox en Fila {i+1} (texto '{celda_texto}')...")
                                checkbox.check()
                                self.base.esperar_fijo(pausa_interaccion) # Pausa para que el DOM se actualice
                                
                                if checkbox.is_checked():
                                    self.logger.info(f"\n  ✅ Checkbox en Fila {i+1} marcado correctamente.")
                                    checkboxes_marcados_exitosamente += 1
                                    self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_checkbox_marcado", directorio)
                                else:
                                    self.logger.error(f"\n  ❌ FALLO: No se pudo marcar el checkbox en Fila {i+1} (texto '{celda_texto}').")
                                    self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_checkbox_no_marcado", directorio)
                            else:
                                self.logger.warning(f"\n  ⚠️ Checkbox en Fila {i+1} (texto '{celda_texto}') ya estaba marcado. No se requiere acción.")
                                self.base.tomar_captura(f"{nombre_base}_fila_{i+1}_checkbox_ya_marcado", directorio)
                            
                            # --- Medición de rendimiento: Fin de interacción de checkbox ---
                            end_time_checkbox_interaction = time.time()
                            duration_checkbox_interaction = end_time_checkbox_interaction - start_time_checkbox_interaction
                            interaction_times.append(duration_checkbox_interaction)
                            self.logger.info(f"PERFORMANCE: Tiempo de interacción con checkbox en Fila {i+1}: {duration_checkbox_interaction:.4f} segundos.")

                        else:
                            self.logger.warning(f"\n  ⚠️ ADVERTENCIA: No se encontró un checkbox en la Fila {i+1} a pesar de la coincidencia del texto.")
                        break # Salir del bucle de celdas una vez encontrada la coincidencia en la fila

                if not celda_encontrada_en_fila:
                    self.logger.debug(f"\n  No se encontró '{texto_a_buscar}' en la Fila {i+1}. Continuando con la siguiente fila.")

            # --- Medición de rendimiento: Fin del escaneo de la tabla ---
            end_time_scan = time.time()
            duration_scan = end_time_scan - start_time_scan
            self.logger.info(f"PERFORMANCE: Tiempo total de escaneo de {num_filas} filas en la tabla: {duration_scan:.4f} segundos.")

            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (búsqueda y marcado): {duration_total_operation:.4f} segundos.")

            if interaction_times:
                avg_interaction_time = sum(interaction_times) / len(interaction_times)
                self.logger.info(f"PERFORMANCE: Tiempo promedio de marcado por checkbox: {avg_interaction_time:.4f} segundos.")


            if checkboxes_marcados_exitosamente > 0:
                self.logger.info(f"\n✅ ÉXITO: Se marcaron {checkboxes_marcados_exitosamente} checkbox(es) basados en la búsqueda de '{texto_a_buscar}'.")
                self.base.tomar_captura(f"{nombre_base}_busqueda_finalizada_exito", directorio)
                return True
            elif found_any_match and checkboxes_marcados_exitosamente == 0:
                 self.logger.warning(f"\n⚠️ ADVERTENCIA: Se encontraron coincidencias para '{texto_a_buscar}', pero no se pudo marcar ningún checkbox. Posiblemente ya estaban marcados o hubo un problema al interactuar.")
                 self.base.tomar_captura(f"{nombre_base}_busqueda_finalizada_coincidencia_sin_marcados", directorio)
                 return True # Consideramos éxito si se encontró la coincidencia, aunque no se marcaran nuevos.
            else:
                self.logger.warning(f"\n⚠️ ADVERTENCIA: No se encontraron coincidencias para '{texto_a_buscar}' en ninguna celda de la tabla.")
                self.base.tomar_captura(f"{nombre_base}_busqueda_finalizada_sin_coincidencias", directorio)
                return False # Falla si no se encuentra ninguna coincidencia.

        except TimeoutError as e:
            # Captura si la tabla no se vuelve visible a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Timeout): La tabla con el locator '{tabla_selector}' no estuvo visible a tiempo (timeout configurado: {tiempo_espera_tabla}s).\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_timeout_tabla", directorio)
            raise AssertionError(f"\nTabla no disponible a tiempo: {tabla_selector}") from e

        except Error as e:
            # Captura errores específicos de Playwright durante la interacción con la tabla o checkboxes.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error al interactuar con la tabla o los checkboxes.\n"
                f"Posibles causas: Locator inválido, problemas de interacción con el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            raise AssertionError(f"\nError de Playwright durante la búsqueda/marcado: {tabla_selector}") from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado durante la búsqueda y marcado de checkboxes.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            raise AssertionError(f"\nError inesperado durante la búsqueda/marcado: {tabla_selector}") from e