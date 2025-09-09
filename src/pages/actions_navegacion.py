import time
import re
from typing import Union, Optional, Dict, Any, List
from playwright.sync_api import Page, Locator, expect, Error, TimeoutError

class NavigationActions:
    def __init__(self, base_page):
        self.base = base_page
        self.page: Page = base_page.page
        self.logger = base_page.logger

    def ir_a_url(self, url: str, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Navega a una URL específica y mide el tiempo que tarda la operación.
        Incluye manejo de excepciones y la posibilidad de tomar capturas de pantalla.

        Args:
            url (str): La URL a la que se desea navegar.
            nombre_base (str): Nombre base para las capturas de pantalla.
            directorio (str): Ruta del directorio para guardar las capturas.
            tiempo (Union[int, float]): Tiempo de espera después de la navegación.
        """
        nombre_paso = f"Navegar a la URL: '{url}'"
        self.logger.info(f"\n--- {nombre_paso} ---")

        # --- Medición de rendimiento: Inicio de la acción de navegación ---
        start_time = time.time()

        try:
            # Navega a la URL. El `wait_until='domcontentloaded'` espera a que el DOM esté listo,
            # lo que es útil para la mayoría de los casos.
            self.page.goto(url, wait_until="domcontentloaded")
            
            # --- Medición de rendimiento: Fin de la acción de navegación ---
            end_time = time.time()
            duration = end_time - start_time
            
            # Registra el éxito y las métricas de rendimiento.
            self.logger.info(f"PERFORMANCE: La navegación a '{url}' tardó {duration:.4f} segundos.")
            self.logger.info(f"\n✔ ÉXITO: Navegación completada a la URL: '{self.page.url}'.")
            self.base.tomar_captura(f"{nombre_base}_navegacion_exitosa", directorio)

        except Error as e:
            # Captura errores específicos de Playwright, como timeouts o errores de red.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time
            error_msg = (
                f"\n❌ FALLO (Playwright Error) - {nombre_paso}: Ocurrió un error de Playwright al navegar a la URL.\\n"
                f"La operación falló después de {duration_fail:.4f} segundos.\\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_navegacion_playwright", directorio)
            raise # Re-lanza la excepción para que el test falle.

        except Exception as e:
            # Captura cualquier otro error inesperado.
            error_msg = (
                f"\n❌ FALLO (Inesperado) - {nombre_paso}: Ocurrió un error inesperado al navegar a la URL.\\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_navegacion", directorio)
            raise # Re-lanza la excepción.
    
    def volver_a_pagina_anterior(self, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Simula la acción de volver a la página anterior en el historial del navegador.
        
        Esta función utiliza el método `page.go_back()` de Playwright y está diseñada
        con robustez para manejar posibles fallos, medir el tiempo de la operación
        y tomar capturas de pantalla para documentar el estado.
        
        Args:
            nombre_base (str): Nombre base para las capturas de pantalla tomadas durante la validación.
            directorio (str): Ruta del directorio para guardar las capturas.
            tiempo (Union[int, float]): Tiempo de espera opcional después de completar la acción.
        
        Raises:
            TimeoutError: Si el navegador no puede volver a la página anterior dentro del tiempo límite.
            Error: Si ocurre un error específico de Playwright durante la operación.
            Exception: Para cualquier otro error inesperado.
        """
        nombre_paso = "Volver a la página anterior"
        self.logger.info(f"\n--- {nombre_paso} ---")

        # Almacena la URL actual para verificar el cambio posterior.
        url_actual = self.page.url
        self.logger.info(f"URL actual antes de la acción: '{url_actual}'.")

        # --- Medición de rendimiento: Inicio de la acción de 'volver atrás' ---
        start_time = time.time()

        try:
            # Intenta volver a la página anterior. Playwright espera implícitamente
            # a que la navegación se complete.
            self.page.go_back()
            
            # --- Medición de rendimiento: Fin de la acción ---
            end_time = time.time()
            duration = end_time - start_time
            
            # Registra el éxito y las métricas de rendimiento.
            self.logger.info(f"PERFORMANCE: La acción de 'volver atrás' tardó {duration:.4f} segundos.")
            
            # Verifica que la URL haya cambiado, asegurando que la navegación fue exitosa.
            if self.page.url != url_actual:
                self.logger.info(f"\n✔ ÉXITO: Navegación de regreso completada. Nueva URL: '{self.page.url}'.")
                self.base.tomar_captura(f"{nombre_base}_volver_atras_exitoso", directorio)
            else:
                # Lanza una excepción si la URL no cambia, indicando un fallo en la navegación.
                raise Exception("La URL no cambió, lo que indica que la navegación de regreso falló o no había página anterior.")

        except Error as e:
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time
            error_msg = (
                f"\n❌ FALLO (Playwright Error) - {nombre_paso}: Ocurrió un error de Playwright al intentar volver a la página anterior.\\n"
                f"La operación falló después de {duration_fail:.4f} segundos.\\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_volver_atras_playwright", directorio)
            raise

        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado) - {nombre_paso}: Ocurrió un error inesperado al intentar volver a la página anterior.\\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_volver_atras", directorio)
            raise
    
    def avanzar_a_pagina_siguiente(self, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Simula la acción de avanzar a la página siguiente en el historial del navegador.
        
        Esta función utiliza el método `page.go_forward()` de Playwright y está diseñada
        con robustez para manejar posibles fallos, medir el tiempo de la operación
        y tomar capturas de pantalla para documentar el estado.
        
        Args:
            nombre_base (str): Nombre base para las capturas de pantalla tomadas durante la validación.
            directorio (str): Ruta del directorio para guardar las capturas.
            tiempo (Union[int, float]): Tiempo de espera opcional después de completar la acción.
        
        Raises:
            TimeoutError: Si el navegador no puede avanzar a la página siguiente dentro del tiempo límite.
            Error: Si ocurre un error específico de Playwright durante la operación.
            Exception: Para cualquier otro error inesperado.
        """
        nombre_paso = "Avanzar a la página siguiente"
        self.logger.info(f"\n--- {nombre_paso} ---")

        # Almacena la URL actual para verificar el cambio posterior.
        url_actual = self.page.url
        self.logger.info(f"\nURL actual antes de la acción: '{url_actual}'.")

        # --- Medición de rendimiento: Inicio de la acción de 'avanzar' ---
        start_time = time.time()

        try:
            # Intenta avanzar a la página siguiente. Playwright espera implícitamente
            # a que la navegación se complete.
            self.page.go_forward()
            
            # --- Medición de rendimiento: Fin de la acción ---
            end_time = time.time()
            duration = end_time - start_time
            
            # Registra el éxito y las métricas de rendimiento.
            self.logger.info(f"\nPERFORMANCE: La acción de 'avanzar' tardó {duration:.4f} segundos.")
            
            # Verifica que la URL haya cambiado, asegurando que la navegación fue exitosa.
            if self.page.url != url_actual:
                self.logger.info(f"\n✔ ÉXITO: Navegación avanzada completada. Nueva URL: '{self.page.url}'.")
                self.base.tomar_captura(f"{nombre_base}_avanzar_exitoso", directorio)
            else:
                # Lanza una excepción si la URL no cambia, indicando un fallo en la navegación.
                raise Exception("La URL no cambió, lo que indica que la navegación de avance falló o no había página siguiente.")

        except Error as e:
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time
            error_msg = (
                f"\n❌ FALLO (Playwright Error) - {nombre_paso}: Ocurrió un error de Playwright al intentar avanzar a la página siguiente.\\n"
                f"La operación falló después de {duration_fail:.4f} segundos.\\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_fallo_avanzar_playwright", directorio)
            raise

        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado) - {nombre_paso}: Ocurrió un error inesperado al intentar avanzar a la página siguiente.\\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_avanzar", directorio)
            raise
                    
    def validar_titulo_de_web(self, titulo_esperado: str, nombre_base: str, directorio: str, tiempo: Union[int, float] = 0.5):
        """
        Valida el título de la página web actual. Esta función espera hasta que el título
        de la página coincida con el `titulo_esperado` dentro de un tiempo límite,
        e integra una **medición de rendimiento** para registrar cuánto tiempo tarda esta validación.

        Args:
            titulo_esperado (str): El **título exacto** que se espera que tenga la página web.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla** tomadas
                               durante la ejecución, facilitando su identificación.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que el
                                        título de la página coincida. Si el título no coincide
                                        dentro de este plazo, la validación fallará.
                                        Por defecto, `5.0` segundos.

        Raises:
            TimeoutError: Si el título de la página no coincide con el `titulo_esperado`
                          dentro del `tiempo` límite.
            AssertionError: Si la aserción de título falla (aunque `TimeoutError` es más común
                            para esta aserción cuando se usa un timeout).
            Exception: Para cualquier otro error inesperado que ocurra durante la validación.
        """
        self.logger.info(f"\nValidando que el título de la página sea: '{titulo_esperado}'. Tiempo máximo de espera: {tiempo}s.")

        # --- Medición de rendimiento: Inicio de la espera por el título ---
        # Registra el tiempo justo antes de iniciar la espera activa de Playwright.
        start_time_title_check = time.time()

        try:
            # Playwright espera a que el título de la página coincida con el `titulo_esperado`.
            # El `timeout` se especifica en milisegundos.
            expect(self.page).to_have_title(titulo_esperado)
            
            # --- Medición de rendimiento: Fin de la espera por el título ---
            # Registra el tiempo una vez que el título ha sido validado con éxito.
            end_time_title_check = time.time()
            # Calcula la duración total que tardó la validación del título.
            # Esta métrica es importante para evaluar la **velocidad de carga y actualización**
            # del título de la página, un indicador clave del rendimiento de navegación.
            duration_title_check = end_time_title_check - start_time_title_check
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en validar el título de la página a '{titulo_esperado}': {duration_title_check:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: Título de la página '{self.page.title()}' validado exitosamente.")
            # Toma una captura de pantalla al validar el título con éxito.
            self.base.tomar_captura(f"{nombre_base}_exito_titulo", directorio)

        except TimeoutError as e:
            # Captura específica para cuando el título no coincide dentro del tiempo especificado.
            # Se registra el tiempo transcurrido hasta el fallo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_title_check # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): El título de la página no coincidió con '{titulo_esperado}' "
                f"después de {duration_fail:.4f} segundos (timeout configurado: {tiempo}s). Título actual: '{self.page.title()}'. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Toma una captura de pantalla en el momento del fallo por timeout.
            self.base.tomar_captura(f"{nombre_base}_fallo_titulo_timeout", directorio)
            raise # Re-lanza la excepción para que la prueba falle.

        except AssertionError as e:
            # Captura si la aserción de título falla por alguna otra razón (menos común con `to_have_title`
            # y timeout, ya que `TimeoutError` suele ser lo primero).
            error_msg = (
                f"\n❌ FALLO (Aserción): El título de la página NO coincide con '{titulo_esperado}'. "
                f"Título actual: '{self.page.title()}'. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Toma una captura de pantalla en el momento del fallo de aserción.
            self.base.tomar_captura(f"{nombre_base}_fallo_titulo_no_coincide", directorio)
            raise # Re-lanza la excepción.

        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir durante la validación del título.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al validar el título de la página. "
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Toma una captura para errores inesperados.
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_titulo", directorio)
            raise # Re-lanza la excepción.
        
    def validar_url_actual(self, patron_url: str, tiempo: Union[int, float] = 0.5):
        """
        Valida la URL actual de la página usando un patrón de expresión regular.
        Esta función espera hasta que la URL de la página coincida con el `patron_url`
        dentro de un tiempo límite, e integra una **medición de rendimiento** para registrar
        cuánto tiempo tarda esta validación.

        Args:
            patron_url (str): El **patrón de expresión regular** (regex) que se espera
                              que coincida con la URL actual de la página. Por ejemplo,
                              `r".*\\/dashboard.*"` para URLs que contengan "/dashboard".
            tiempo (Union[int, float]): **Tiempo máximo de espera** (en segundos) para que la
                                        URL de la página coincida con el patrón. Si la URL
                                        no coincide dentro de este plazo, la validación fallará.
                                        Por defecto, `5.0` segundos.

        Raises:
            TimeoutError: Si la URL actual de la página no coincide con el `patron_url`
                          dentro del `tiempo` límite especificado.
            AssertionError: Si la aserción de URL falla por alguna otra razón
                            (menos común con `to_have_url` y `timeout`, ya que `TimeoutError`
                            suele ser la excepción principal).
            Exception: Para cualquier otro error inesperado que ocurra durante la validación de la URL.
        """
        self.logger.info(f"\nValidando que la URL actual coincida con el patrón: '{patron_url}'. Tiempo máximo de espera: {tiempo}s.")

        # --- Medición de rendimiento: Inicio de la espera por la URL ---
        # Registra el tiempo justo antes de iniciar la espera activa de Playwright para la URL.
        start_time_url_check = time.time()

        try:
            # Playwright espera a que la URL de la página coincida con el patrón de expresión regular.
            # El `timeout` se especifica en milisegundos.
            # `re.compile(patron_url)` convierte la cadena del patrón en un objeto de expresión regular
            # que `to_have_url` puede utilizar.
            expect(self.page).to_have_url(re.compile(patron_url))
            
            # --- Medición de rendimiento: Fin de la espera por la URL ---
            # Registra el tiempo una vez que la URL ha sido validada con éxito.
            end_time_url_check = time.time()
            # Calcula la duración total que tardó la validación de la URL.
            # Esta métrica es crucial para evaluar la **velocidad de navegación y carga de la página**,
            # ya que la URL a menudo cambia una vez que la página está completamente cargada o enrutada.
            duration_url_check = end_time_url_check - start_time_url_check
            self.logger.info(f"PERFORMANCE: Tiempo que tardó en validar la URL a '{patron_url}': {duration_url_check:.4f} segundos.")

            self.logger.info(f"\n✔ ÉXITO: URL '{self.page.url}' validada exitosamente con el patrón: '{patron_url}'.")
            # Nota sobre capturas de pantalla para URL:
            # Generalmente, una captura de pantalla no es visualmente útil para validar una URL,
            # ya que la URL se encuentra en la barra de direcciones del navegador.
            # Sin embargo, si deseas tener un registro visual del estado de la página
            # en el momento de la validación exitosa, podrías descomentar la siguiente línea
            # y asegurarte de pasar `nombre_base` y `directorio` como argumentos a esta función.
            # self.tomar_captura(f"{nombre_base}_exito_url", directorio)

        except TimeoutError as e:
            # Captura específica para cuando la URL no coincide con el patrón dentro del tiempo especificado.
            # Se registra el tiempo transcurrido hasta el fallo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_url_check # Mide desde el inicio de la operación.
            error_msg = (
                f"\n❌ FALLO (Timeout): La URL actual '{self.page.url}' no coincidió con el patrón "
                f"'{patron_url}' después de {duration_fail:.4f} segundos (timeout configurado: {tiempo}s). Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True) # Registra el error con la traza completa.
            # Podrías añadir una captura de pantalla aquí en caso de fallo, si es necesario para depuración.
            # self.tomar_captura(f"{nombre_base}_fallo_url_timeout", directorio)
            raise # Re-lanza la excepción para asegurar que la prueba falle.

        except AssertionError as e:
            # Captura si la aserción de URL falla por alguna otra razón que no sea un timeout directo
            # (aunque con `to_have_url` y `timeout`, `TimeoutError` es más común).
            error_msg = (
                f"\n❌ FALLO (Aserción): La URL actual '{self.page.url}' NO coincide con el patrón: "
                f"'{patron_url}'. Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            # Podrías añadir una captura de pantalla aquí en caso de fallo de aserción.
            # self.tomar_captura(f"{nombre_base}_fallo_url_no_coincide", directorio)
            raise # Re-lanza la excepción.
        
        except Exception as e:
            # Captura cualquier otra excepción inesperada que pueda ocurrir durante la validación de la URL.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al validar la URL. "
                f"URL actual: '{self.page.url}', Patrón esperado: '{patron_url}'. Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True) # Usa nivel crítico para errores graves.
            # Podrías añadir una captura de pantalla aquí para errores inesperados.
            # self.tomar_captura(f"{nombre_base}_error_inesperado_url", directorio)
            raise # Re-lanza la excepción.
        
    def verificar_pagina_inicial_seleccionada(self, selector_paginado: Locator, texto_pagina_inicial: str, nombre_base: str, directorio: str, clase_resaltado: str = "active", tiempo_espera_componente: Union[int, float] = 1.0) -> bool:
        """
        Verifica que la página inicial esperada esté seleccionada y correctamente resaltada
        dentro de un componente de paginación. Mide el rendimiento de la localización y verificación.

        Args:
            selector_paginado (Locator): El **Locator de Playwright** que representa el
                                         contenedor principal del componente de paginación.
                                         (e.g., un `<div>` o `<nav>` que encierra el paginador).
            texto_pagina_inicial (str): El **texto exacto** de la página que se espera que sea
                                        la página inicial seleccionada (ej. "1", "Inicio").
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            clase_resaltado (str): La **clase CSS** que indica que un elemento de paginación
                                   está activo/seleccionado (ej. "active", "selected", "current-page").
                                   Por defecto, "active".
            tiempo_espera_componente (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                         para que el componente de paginación y
                                                         el elemento de la página inicial estén visibles.
                                                         Por defecto, `10.0` segundos.

        Returns:
            bool: `True` si la página inicial esperada está visible y tiene la clase de resaltado;
                  `False` en caso contrario.

        Raises:
            AssertionError: Si el componente de paginación o el elemento de la página inicial
                            no están disponibles a tiempo, o si ocurre un error inesperado
                            de Playwright o genérico.
        """
        self.logger.info(f"\n--- Iniciando verificación del estado inicial de la paginación ---")
        self.logger.info(f"\nContenedor de paginación locator: '{selector_paginado}'")
        self.logger.info(f"P\nágina inicial esperada: '{texto_pagina_inicial}'")
        self.base.tomar_captura(f"{nombre_base}_inicio_verificacion_paginacion", directorio)

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Asegurarse de que el contenedor de paginación esté visible
            self.logger.debug(f"\nEsperando que el contenedor de paginación '{selector_paginado}' esté visible (timeout: {tiempo_espera_componente}s).")
            # Convertir tiempo_espera_componente de segundos a milisegundos para expect()
            expect(selector_paginado).to_be_visible()
            selector_paginado.highlight()
            self.logger.info("\n✅ Contenedor de paginación visible. Procediendo a verificar la página inicial.")

            # --- Medición de rendimiento: Inicio de localización de la página inicial ---
            start_time_locator_page = time.time()

            # 2. Intentar encontrar el elemento de la página inicial por su texto dentro del contenedor
            # Se usa text= para una coincidencia exacta del texto visible del número de página.
            # Es crucial que el selector apunte al elemento que realmente tiene el texto de la página (ej. un <a> o <span> dentro de un <li>).
            # Si el texto '1' aparece en otros lugares, puede ser necesario un selector más específico,
            # como `selector_paginado.locator(f"li > a:has-text('{texto_pagina_inicial}')")` o similar.
            pagina_inicial_locator = selector_paginado.locator(f"text='{texto_pagina_inicial}'").first

            # Esperar a que el elemento de la página inicial esté visible y sea interactuable
            self.logger.debug(f"\nEsperando que el elemento de la página inicial '{texto_pagina_inicial}' esté visible (timeout: {tiempo_espera_componente}s).")
            expect(pagina_inicial_locator).to_be_visible()
            self.logger.info(f"\n✅ Elemento para la página '{texto_pagina_inicial}' encontrado y visible.")

            # --- Medición de rendimiento: Fin de localización de la página inicial ---
            end_time_locator_page = time.time()
            duration_locator_page = end_time_locator_page - start_time_locator_page
            self.logger.info(f"PERFORMANCE: Tiempo de localización del elemento de la página inicial: {duration_locator_page:.4f} segundos.")

            # --- Medición de rendimiento: Inicio de verificación de estado ---
            start_time_verification = time.time()

            # 3. Verificar que la página inicial esperada esté seleccionada (marcada con la clase de resaltado)
            self.logger.info(f"\nVerificando si la página '{texto_pagina_inicial}' tiene la clase de resaltado esperada '{clase_resaltado}'...")
            pagina_inicial_locator.highlight() # Resaltar el elemento para la captura visual
            self.base.tomar_captura(f"{nombre_base}_pagina_inicial_encontrada_resaltada", directorio)

            # Obtener todas las clases del elemento y verificar si la clase de resaltado está presente
            current_classes_attribute = pagina_inicial_locator.get_attribute("class")
            
            # Un elemento puede no tener atributo 'class' o puede ser una cadena vacía
            if current_classes_attribute is not None:
                current_classes_list = current_classes_attribute.split()
            else:
                current_classes_list = [] # Si no hay atributo 'class', la lista está vacía

            if clase_resaltado in current_classes_list:
                self.logger.info(f"\n  ✅ ÉXITO: La página '{texto_pagina_inicial}' está seleccionada y resaltada con la clase '{clase_resaltado}'.")
                self.base.tomar_captura(f"{nombre_base}_pagina_inicial_seleccionada_ok", directorio)
                success = True
            else:
                self.logger.error(f"\n  ❌ FALLO: La página '{texto_pagina_inicial}' no tiene la clase de resaltado esperada '{clase_resaltado}'.")
                self.logger.info(f"\n  Clases actuales del elemento: '{current_classes_attribute}'")
                self.base.tomar_captura(f"{nombre_base}_pagina_inicial_no_resaltada", directorio)
                success = False
            
            # --- Medición de rendimiento: Fin de verificación de estado ---
            end_time_verification = time.time()
            duration_verification = end_time_verification - start_time_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación de la clase de resaltado: {duration_verification:.4f} segundos.")

            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (verificación de paginación inicial): {duration_total_operation:.4f} segundos.")

            return success

        except TimeoutError as e:
            # Captura si el contenedor de paginación o el elemento de la página inicial no se vuelven visibles a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Timeout): El contenedor de paginación '{selector_paginado}' "
                f"o la página inicial '{texto_pagina_inicial}' no estuvieron visibles a tiempo "
                f"(timeout configurado: {tiempo_espera_componente}s).\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_timeout_paginacion", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nComponente de paginación o página inicial no disponibles a tiempo: {selector_paginado}") from e

        except Error as e:
            # Captura errores específicos de Playwright durante la interacción con el DOM.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error al interactuar con el componente de paginación.\n"
                f"Posibles causas: Locator inválido, problemas de interacción con el DOM.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nError de Playwright al verificar paginación: {selector_paginado}") from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al verificar la paginación.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nError inesperado al verificar paginación: {selector_paginado}") from e
        
    def navegar_y_verificar_pagina(self, selector_paginado: Locator, numero_pagina_a_navegar: str, nombre_base: str, directorio: str, clase_resaltado: str = "active", tiempo_espera_componente: Union[int, float] = 1.0, pausa_post_clic: Union[int, float] = 0.5) -> bool:
        """
        Navega a un número de página específico en un componente de paginación haciendo clic en el enlace
        correspondiente y verifica que la página de destino esté seleccionada y resaltada.
        Integra mediciones de rendimiento para cada fase de la operación.

        Args:
            selector_paginado (Locator): El **Locator de Playwright** que representa el
                                         contenedor principal del componente de paginación.
                                         (e.g., un `<div>` o `<nav>` que encierra el paginador).
            numero_pagina_a_navegar (str): El **número de la página** a la que se desea navegar (como cadena).
                                          Ej. "2", "5".
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            clase_resaltado (str): La **clase CSS** que indica que un elemento de paginación
                                   está activo/seleccionado (ej. "active", "selected", "current-page").
                                   Por defecto, "active".
            tiempo_espera_componente (Union[int, float]): **Tiempo máximo de espera** (en segundos)
                                                         para que el componente de paginación y
                                                         los elementos de página estén visibles.
                                                         Por defecto, `10.0` segundos.
            pausa_post_clic (Union[int, float]): **Pausa opcional** (en segundos) después de
                                                  hacer clic en un número de página, para permitir
                                                  que la página cargue y los estilos se apliquen.
                                                  Por defecto, `0.5` segundos.

        Returns:
            bool: `True` si la navegación fue exitosa y la página de destino está resaltada;
                  `False` en caso contrario.

        Raises:
            AssertionError: Si el componente de paginación o el elemento de la página de destino
                            no están disponibles a tiempo, o si ocurre un error inesperado
                            de Playwright o genérico.
        """
        self.logger.info(f"\n--- Iniciando navegación a la página '{numero_pagina_a_navegar}' y verificación de resaltado ---")
        self.logger.info(f"\nContenedor de paginación locator: '{selector_paginado}'")
        self.base.tomar_captura(f"{nombre_base}_inicio_navegacion_pagina_{numero_pagina_a_navegar}", directorio)

        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Asegurarse de que el contenedor de paginación está visible
            self.logger.debug(f"\nEsperando que el contenedor de paginación '{selector_paginado}' esté visible (timeout: {tiempo_espera_componente}s).")
            # Convertir tiempo_espera_componente de segundos a milisegundos para expect()
            expect(selector_paginado).to_be_visible()
            selector_paginado.highlight()
            self.logger.info("\n✅ Contenedor de paginación visible. Procediendo.")

            # --- Medición de rendimiento: Inicio detección de página actual y total ---
            start_time_detection = time.time()

            # Obtener la página actualmente seleccionada
            # Este locator debería apuntar al elemento que realmente tiene la clase 'active'
            # y cuyo texto es el número de página (ej. un <a> dentro de un <li>)
            pagina_actual_locator = selector_paginado.locator(f"a.{clase_resaltado}").first
            # O si el <li> es el que tiene la clase, y necesitas el texto del <a> dentro:
            # pagina_actual_locator = selector_paginado.locator(f"li.{clase_resaltado} a").first

            # Usar .is_visible() y .text_content() para obtener el texto de forma segura
            pagina_actual_texto = "Desconocida"
            if pagina_actual_locator.count() > 0 and pagina_actual_locator.is_visible():
                pagina_actual_texto = pagina_actual_locator.text_content().strip()
            self.logger.info(f"\n  Página actualmente seleccionada detectada: {pagina_actual_texto}")

            # Calcular el número total de páginas disponibles
            # Asumimos que los elementos de paginación son 'li' y que el último 'li' visible
            # que contenga un número representa la última página.
            todos_los_botones_pagina = selector_paginado.locator("li")
            num_botones = todos_los_botones_pagina.count()
            
            total_paginas = 0
            if num_botones > 0:
                for i in range(num_botones - 1, -1, -1): # Iterar al revés para encontrar el último número
                    btn = todos_los_botones_pagina.nth(i)
                    btn_text = btn.text_content().strip()
                    if btn_text.isdigit(): # Si el texto es un número válido
                        total_paginas = int(btn_text)
                        break
            
            self.logger.info(f"\n  Número total de páginas detectadas: {total_paginas}")
            
            # --- Medición de rendimiento: Fin detección de página actual y total ---
            end_time_detection = time.time()
            duration_detection = end_time_detection - start_time_detection
            self.logger.info(f"PERFORMANCE: Tiempo de detección de página actual y total: {duration_detection:.4f} segundos.")

            # 2. Validaciones previas a la navegación
            try:
                # Convertir a int para comparaciones numéricas
                num_pagina_int = int(numero_pagina_a_navegar)
                pagina_actual_int = int(pagina_actual_texto) if pagina_actual_texto.isdigit() else -1 # Usar -1 si es desconocido
            except ValueError:
                self.logger.error(f"\n❌ FALLO: El número de página a navegar '{numero_pagina_a_navegar}' no es un número válido.")
                self.base.tomar_captura(f"{nombre_base}_pagina_destino_invalida", directorio)
                return False

            # Condicional 1: Página de destino es mayor que el total de páginas
            if total_paginas > 0 and num_pagina_int > total_paginas:
                self.logger.warning(f"\n⚠️ ADVERTENCIA: La página de destino '{numero_pagina_a_navegar}' es mayor que el número total de páginas disponibles '{total_paginas}'.")
                self.base.tomar_captura(f"{nombre_base}_pagina_destino_fuera_rango", directorio)
                return False # Considerar como fallo si la página está fuera de rango

            # Condicional 2: La página de destino es la misma que la página actual
            if num_pagina_int == pagina_actual_int:
                self.logger.warning(f"\n⚠️ ADVERTENCIA: Ya estás en la página '{numero_pagina_a_navegar}'. No se requiere navegación.")
                # Opcional: Podrías verificar de nuevo que siga resaltada, pero si ya estaba, no es una "navegación".
                self.base.tomar_captura(f"{nombre_base}_pagina_destino_actual", directorio)
                return True # Considerar esto un éxito, ya que el estado es el esperado.

            # 3. Encontrar y hacer clic en el botón de la página deseada
            # Este selector busca un 'a' dentro de un 'li' que contenga el texto del número de página.
            # Ajusta esto si tu estructura HTML es diferente (ej. si el número está directamente en el 'li').
            pagina_destino_locator = selector_paginado.locator(
                f"li:has-text('{numero_pagina_a_navegar}') a" 
            ).first
            
            # --- Medición de rendimiento: Inicio de localización del botón de la página de destino ---
            start_time_locator_button = time.time()
            expect(pagina_destino_locator).to_be_visible()
            expect(pagina_destino_locator).to_be_enabled()
            self.logger.info(f"\n✅ Elemento de la página '{numero_pagina_a_navegar}' encontrado y habilitado para clic.")
            
            # --- Medición de rendimiento: Fin de localización del botón de la página de destino ---
            end_time_locator_button = time.time()
            duration_locator_button = end_time_locator_button - start_time_locator_button
            self.logger.info(f"PERFORMANCE: Tiempo de localización del botón de la página de destino: {duration_locator_button:.4f} segundos.")

            pagina_destino_locator.highlight()
            self.base.tomar_captura(f"{nombre_base}_pagina_a_navegar_encontrada", directorio)
            
            self.logger.info(f"\n  Haciendo clic en la página '{numero_pagina_a_navegar}'...")
            
            # --- Medición de rendimiento: Inicio de click y espera de carga ---
            start_time_click_and_wait = time.time()
            pagina_destino_locator.click()
            self.base.esperar_fijo(pausa_post_clic) # Pausa para permitir la carga de la página y la aplicación de estilos
            
            # --- Medición de rendimiento: Fin de click y espera de carga ---
            end_time_click_and_wait = time.time()
            duration_click_and_wait = end_time_click_and_wait - start_time_click_and_wait
            self.logger.info(f"PERFORMANCE: Tiempo de click y espera de carga para la página '{numero_pagina_a_navegar}': {duration_click_and_wait:.4f} segundos.")

            self.base.tomar_captura(f"{nombre_base}_pagina_{numero_pagina_a_navegar}_clic", directorio)

            # 4. Verificar que la página de destino se resalte
            self.logger.info(f"\nVerificando si la página '{numero_pagina_a_navegar}' tiene la clase de resaltado '{clase_resaltado}'...")
            
            # Asegurarse de que el elemento de destino aún esté visible y, opcionalmente, que sus atributos se hayan actualizado.
            expect(pagina_destino_locator).to_be_visible()
            pagina_destino_locator.highlight() # Resaltar el elemento para la captura final

            # --- Medición de rendimiento: Inicio de verificación de estado final ---
            start_time_final_verification = time.time()

            current_classes_attribute = pagina_destino_locator.get_attribute("class")
            
            if current_classes_attribute is not None:
                current_classes_list = current_classes_attribute.split()
            else:
                current_classes_list = []

            if clase_resaltado in current_classes_list:
                self.logger.info(f"\n  ✅ ÉXITO: La página '{numero_pagina_a_navegar}' está seleccionada y resaltada con la clase '{clase_resaltado}'.")
                self.base.tomar_captura(f"{nombre_base}_pagina_{numero_pagina_a_navegar}_seleccionada_ok", directorio)
                success = True
            else:
                self.logger.error(f"\n  ❌ FALLO: La página '{numero_pagina_a_navegar}' no tiene la clase de resaltado esperada '{clase_resaltado}'.")
                self.logger.info(f"\n  Clases actuales del elemento: '{current_classes_attribute}'")
                self.base.tomar_captura(f"{nombre_base}_pagina_{numero_pagina_a_navegar}_no_resaltada", directorio)
                success = False

            # --- Medición de rendimiento: Fin de verificación de estado final ---
            end_time_final_verification = time.time()
            duration_final_verification = end_time_final_verification - start_time_final_verification
            self.logger.info(f"PERFORMANCE: Tiempo de verificación de la clase de resaltado final: {duration_final_verification:.4f} segundos.")

            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (navegación y verificación de paginación): {duration_total_operation:.4f} segundos.")

            return success

        except TimeoutError as e:
            # Captura si el contenedor de paginación o el elemento de la página de destino no se vuelven visibles/interactuables a tiempo.
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Timeout): El contenedor de paginación '{selector_paginado}' "
                f"o la página '{numero_pagina_a_navegar}' no estuvieron visibles/interactuables a tiempo "
                f"(timeout configurado: {tiempo_espera_componente}s).\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_timeout_navegacion", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nComponente de paginación o página de destino no disponibles a tiempo: {selector_paginado} o página {numero_pagina_a_navegar}") from e

        except Error as e:
            # Captura errores específicos de Playwright durante la interacción con el DOM.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error al interactuar con el componente de paginación durante la navegación.\n"
                f"Posibles causas: Locator inválido, problemas de interacción con el DOM, elemento no clickable.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nError de Playwright al navegar/verificar paginación: {selector_paginado}") from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al navegar y verificar la paginación.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado", directorio)
            # Re-lanzar como AssertionError para que el framework de pruebas registre un fallo.
            raise AssertionError(f"\nError inesperado al navegar/verificar paginación: {selector_paginado}") from e
            
    def abrir_y_cambiar_a_nueva_pestana(self, selector_boton_apertura: Locator, nombre_base: str, directorio: str, tiempo_espera_max_total: Union[int, float] = 15.0, texto_esperado_en_boton: Optional[str] = None) -> Optional[Page]:
        """
        Esperar por la apertura de una nueva pestaña/página (popup) después de hacer clic
        en un elemento dado, cambiar el foco a esa nueva pestaña, y medir el rendimiento.

        Args:
            selector_boton_apertura (Locator): El **Locator de Playwright** del botón o elemento
                                            que, al ser clicado, dispara la apertura de una nueva pestaña/ventana.
            nombre_base (str): Nombre base para las capturas de pantalla.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_espera_max_total (Union[int, float]): **Tiempo máximo total de espera** (en segundos)
                                                        para el proceso completo. Por defecto, 15.0 segundos.
            texto_esperado_en_boton (Optional[str]): El **texto esperado** en el botón.
        Returns:
            Optional[Page]: El objeto `Page` de la nueva pestaña/ventana.
        Raises:
            AssertionError: Si el elemento disparador no está disponible, o si el proceso falla.
        """
        self.logger.info(f"\n🔄 Preparando para hacer clic en '{selector_boton_apertura}' y esperar nueva pestaña/popup. Esperando hasta {tiempo_espera_max_total} segundos...")

        # Reiniciar las banderas y variables de estado para esta operación
        self._popup_detectado = False
        self._popup_page = None

        start_time_total_operation = time.time()

        try:
            self.logger.debug("\n--- INICIO del bloque TRY ---")

            # 1. Hacer clic en el botón que abre la nueva pestaña
            self.logger.info(f"--> Haciendo clic en el botón '{selector_boton_apertura}' para disparar la apertura de la nueva página...")
            self.base.element.hacer_click_en_elemento(
                selector_boton_apertura, 
                f"{nombre_base}_click_para_nueva_pestana", 
                directorio, 
                texto_esperado=texto_esperado_en_boton
            )

            # 2. Esperar que la nueva página sea detectada por el oyente del constructor
            self.logger.info(f"--> Clic en el botón disparador completado. Esperando que el oyente permanente detecte la nueva página...")
            
            start_time_new_page_detection = time.time()
            
            # Bucle de espera para la detección del popup
            while not self._popup_detectado and (time.time() - start_time_total_operation) < tiempo_espera_max_total:
                time.sleep(0.1)  # Espera corta para no sobrecargar el CPU
            
            end_time_new_page_detection = time.time()
            duration_new_page_detection = end_time_new_page_detection - start_time_new_page_detection
            
            # Validar si el popup fue detectado y el objeto page no está vacío
            if not self._popup_detectado or self._popup_page is None or self._popup_page.is_closed():
                raise TimeoutError("No se detectó una nueva pestaña/página o se cerró inesperadamente dentro del tiempo de espera.")
                
            self.logger.info(f"PERFORMANCE: Tiempo de detección de la nueva página por el oyente: {duration_new_page_detection:.4f} segundos.")
            self.logger.info(f"--> Nueva página detectada. URL: {self._popup_page.url}")
            
            nueva_pagina = self._popup_page
            
            # 3. Esperar a que la nueva página cargue completamente el DOM y los recursos
            self.logger.debug(f"--> Esperando que la nueva página cargue completamente (Load state)...")
            #nueva_pagina.wait_for_load_state("load")
            nueva_pagina.wait_for_load_state("domcontentloaded")
            self.logger.info("--> Carga de la nueva página completada (Load state).")

            # 4. Esperar a que un elemento clave de la nueva página sea visible
            self.logger.debug(f"--> Esperando que el 'body' de la nueva página sea visible...")
            expect(nueva_pagina.locator("body")).to_be_visible()
            self.logger.info("--> El 'body' de la nueva página es visible.")

            self.logger.info(f"\n✅ Nueva pestaña abierta y detectada: URL = {nueva_pagina.url}, Título = {nueva_pagina.title()}")
            
            # 5. Actualizar self.page para que las subsiguientes operaciones usen la nueva página
            self.logger.info(f"--> Cambiando el foco de la instancia 'page' actual a la nueva pestaña...")
            self.page = nueva_pagina 
            
            self.base.tomar_captura(f"{nombre_base}_nueva_pestana_abierta_y_cargada", directorio)
            
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (apertura y cambio a nueva pestaña): {duration_total_operation:.4f} segundos.")
            
            return nueva_pagina

        except TimeoutError as e:
            end_time_fail = time.time()
            duration_fail = end_time_fail - start_time_total_operation
            error_msg = (
                f"\n❌ FALLO (Tiempo de espera excedido): No se detectó ninguna nueva pestaña/página después de {tiempo_espera_max_total} segundos.\n"
                f"La operación duró {duration_fail:.4f} segundos antes del fallo.\n"
                f"Detalles: {e}"
            )
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_no_se_detecto_popup_timeout", directorio)
            raise AssertionError(f"\nTimeout al abrir o cargar nueva pestaña para selector '{selector_boton_apertura}'") from e
        except Error as e:
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al interactuar con el botón o la nueva pestaña.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_abrir_pestana", directorio)
            raise AssertionError(f"\nError de Playwright al abrir y cambiar a nueva pestaña para selector '{selector_boton_apertura}'") from e
        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al intentar abrir y cambiar a la nueva pestaña.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_abrir_pestana", directorio)
            raise AssertionError(f"\nError inesperado al abrir y cambiar a nueva pestaña para selector '{selector_boton_apertura}'") from e

    def cerrar_pestana_actual(self, nombre_base: str, directorio: str, tiempo_post_cierre: Union[int, float] = 1.0) -> None:
        """
        Cierra la pestaña Playwright actualmente activa (`self.page`).
        Si quedan otras pestañas abiertas en el mismo contexto del navegador,
        cambia el foco (`self.page`) a la primera pestaña disponible.
        Mide el rendimiento de las operaciones de cierre y cambio de foco.

        Args:
            nombre_base (str): Nombre base utilizado para la **captura de pantalla**
                               tomada antes de cerrar la pestaña.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            tiempo_post_cierre (Union[int, float]): **Tiempo de espera** (en segundos) después de
                                                    cerrar la pestaña, antes de intentar cambiar el foco.
                                                    Por defecto, `1.0` segundos.

        Raises:
            AssertionError: Si ocurre un error inesperado durante el cierre o el cambio de foco.
                            Se lanza para asegurar que el test falle si la operación no es exitosa.
        """
        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        # Guardar la URL actual antes de cerrarla (para logging)
        current_page_url = "N/A (Página ya cerrada o no accesible)"
        try:
            current_page_url = self.page.url
            self.logger.info(f"\n🚪 Cerrando la pestaña actual: URL = {current_page_url}")
        except Exception as e:
            self.logger.warning(f"\nNo se pudo obtener la URL de la página actual antes de intentar cerrarla: {e}")


        try:
            # ¡IMPORTANTE! Tomar la captura *antes* de cerrar la página.
            self.base.tomar_captura(f"{nombre_base}_antes_de_cerrar", directorio) 
            
            self.logger.debug(f"\n  --> Iniciando cierre de la página: {current_page_url}")
            # --- Medición de rendimiento: Inicio del cierre de la pestaña ---
            start_time_close_page = time.time()
            self.page.close()
            # --- Medición de rendimiento: Fin del cierre de la pestaña ---
            end_time_close_page = time.time()
            duration_close_page = end_time_close_page - start_time_close_page
            self.logger.info(f"PERFORMANCE: Tiempo de cierre de la pestaña: {duration_close_page:.4f} segundos.")
            
            self.logger.info(f"\n✅ Pestaña con URL '{current_page_url}' cerrada exitosamente.")
            
            # Pequeña espera después de cerrar la pestaña para asegurar que el DOM se libere
            self.base.esperar_fijo(tiempo_post_cierre) 

            # Verificar si hay otras páginas abiertas en el contexto y cambiar el foco
            self.logger.debug("\n  --> Verificando otras pestañas en el contexto para cambiar el foco...")
            # --- Medición de rendimiento: Inicio del cambio de foco ---
            start_time_switch_focus = time.time()
            if self.page.context.pages:
                # Playwright mantiene automáticamente la lista de páginas abiertas.
                # Al cerrar una página, si era la única, la lista se vacía.
                # Si hay más, la primera página en la lista es generalmente la que queda activa o la primera en crearse.
                self.page = self.page.context.pages[0] # Cambia el foco a la primera página disponible
                # --- Medición de rendimiento: Fin del cambio de foco ---
                end_time_switch_focus = time.time()
                duration_switch_focus = end_time_switch_focus - start_time_switch_focus
                self.logger.info(f"PERFORMANCE: Tiempo de cambio de foco a la nueva pestaña activa: {duration_switch_focus:.4f} segundos.")

                self.logger.info(f"\n🔄 Foco cambiado automáticamente a la primera pestaña disponible: URL = {self.page.url}")
                # Opcional: Podrías tomar otra captura aquí si quieres mostrar el estado de la nueva pestaña activa.
                # self.tomar_captura(f"{nombre_base}_foco_cambiado", directorio)
            else:
                self.logger.warning("\n⚠️ No hay más pestañas abiertas en el contexto del navegador. La instancia 'self.page' ahora es None.")
                self.page = None # No hay página activa en este contexto

            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (cierre de pestaña y cambio de foco): {duration_total_operation:.4f} segundos.")

        except Error as e:
            # Captura errores específicos de Playwright, como si la página ya está cerrada o el contexto se cerró.
            error_msg = (
                f"\n❌ FALLO (Playwright): Error de Playwright al intentar cerrar la pestaña o cambiar de foco.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            # No se toma captura aquí porque la página podría estar inactiva/cerrada.
            raise AssertionError(f"\nError de Playwright al cerrar pestaña actual: {e}") from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada.
            error_msg = (
                f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al intentar cerrar la pestaña actual o cambiar el foco.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            # No se toma captura aquí porque la página podría estar inactiva/cerrada.
            raise AssertionError(f"\nError inesperado al cerrar pestaña actual: {e}") from e
        
    def hacer_clic_y_abrir_nueva_ventana(self, selector: Locator, nombre_base: str, directorio: str, nombre_paso: str = "", tiempo_espera_max_total: Union[int, float] = 30.0) -> List[Page]:
        """
        Hace clic en un selector y espera que se abran una o más nuevas ventanas/pestañas (popups).
        Esta versión utiliza un bucle con un listener de Playwright para capturar múltiples ventanas.
        """
        self.logger.info(f"\n--- {nombre_paso}: Iniciando operación de clic y espera de nueva ventana para el selector '{selector}' ---")
        self.base.tomar_captura(f"{nombre_base}_antes_clic_nueva_ventana", directorio)
        
        start_time_total_operation = time.time()
        all_pages = self.page.context.pages # Almacena las páginas existentes antes del clic
        loaded_pages = []

        try:
            # 1. Validar que el elemento es visible y habilitado antes de hacer clic
            self.logger.debug(f"Paso 1: Validando que el selector '{selector}' sea visible y habilitado.")
            expect(selector).to_be_visible(timeout=tiempo_espera_max_total * 1000)
            expect(selector).to_be_enabled(timeout=tiempo_espera_max_total * 1000)
            self.logger.info("El selector ha sido validado exitosamente. Está visible y habilitado.")
            selector.highlight()
            self.base.esperar_fijo(0.2)
            
            # 2. Realizar el clic
            self.logger.debug(f"--> Realizando clic en el selector '{selector}'...")
            start_time_click = time.time()
            selector.click()
            duration_click = time.time() - start_time_click
            self.logger.info(f"PERFORMANCE: Tiempo de la acción de clic: {duration_click:.4f} segundos.")
            
            # 3. Esperar que se abran las nuevas páginas
            end_time = time.time() + tiempo_espera_max_total
            self.logger.info("Paso 2: Esperando la(s) nueva(s) ventana(s) hasta que no se abran más o se agote el tiempo.")
            
            while time.time() < end_time:
                # Captura todas las nuevas páginas que aparecieron después del clic
                nuevas_paginas = [p for p in self.page.context.pages if p not in all_pages and p not in loaded_pages]
                
                if nuevas_paginas:
                    self.logger.info(f"✅ Se detectaron {len(nuevas_paginas)} nueva(s) ventana(s).")
                    for new_page in nuevas_paginas:
                        # Esperar a que cada nueva página cargue completamente
                        self.logger.info(f"Paso 3: Esperando la carga completa de la nueva página (URL: {new_page.url}).")
                        try:
                            new_page.wait_for_load_state("networkidle", timeout=(end_time - time.time()) * 1000)
                            self.logger.info(f"🌐 Nueva página cargada exitosamente: URL = {new_page.url}, Título = {new_page.title()}")
                            self.base.tomar_captura(f"{nombre_base}_pagina_abierta_{len(loaded_pages)+1}", directorio)
                            loaded_pages.append(new_page)
                        except TimeoutError as te:
                            self.logger.error(f"\n❌ FALLO: Tiempo de espera excedido al cargar la nueva página (URL: {new_page.url}). Detalles: {te}")
                            raise
                
                # Si no hay nuevas páginas, esperamos un momento y verificamos de nuevo
                if not nuevas_paginas:
                    time.sleep(0.5)
            
            # 4. Validación final
            if not loaded_pages:
                self.logger.error("\n❌ FALLO: No se cargó correctamente ninguna página.")
                raise AssertionError("No se detectaron nuevas ventanas/pestañas después del clic.")

            self.base.tomar_captura(f"{nombre_base}_despues_clic_nueva_ventana_final", directorio)
            self.logger.info(f"\n✅ Operación completada: se ha detectado y cargado {len(loaded_pages)} nueva(s) ventana(s) con éxito.")
            
            duration_total_operation = time.time() - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación: {duration_total_operation:.4f} segundos.")

            return loaded_pages

        except TimeoutError as e:
            error_msg = f"\n❌ FALLO (Tiempo de espera excedido): El elemento '{selector}' no estuvo visible/habilitado a tiempo o no se detectaron nuevas ventanas dentro de {tiempo_espera_max_total}s. Detalles: {e}"
            self.logger.error(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_no_nueva_ventana_timeout", directorio)
            raise AssertionError(error_msg) from e
        
        except Exception as e:
            error_msg = f"\n❌ FALLO (Inesperado): Ocurrió un error inesperado al intentar abrir nuevas ventanas. Detalles: {e}"
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_abrir_nueva_ventana", directorio)
            raise AssertionError(error_msg) from e

    def cambiar_foco_entre_ventanas(self, opcion_ventana: Union[int, str], nombre_base: str, directorio: str, nombre_paso: str = "") -> Page:
        """
        Cambia el foco de la instancia 'self.page' a una ventana/pestaña específica
        dentro del mismo contexto del navegador. La ventana objetivo puede ser identificada
        por su índice numérico o por una subcadena presente en su URL o título.
        Mide el rendimiento de la operación de cambio de foco.

        Args:
            opcion_ventana (Union[int, str]): El **criterio para seleccionar la ventana/pestaña objetivo**:
                                              - Si es `int`: el índice (0-basado) de la pestaña en la lista de páginas abiertas.
                                              - Si es `str`: una subcadena que debe coincidir con parte de la URL o el título de la pestaña.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            nombre_paso (str): Una descripción opcional del paso que se está ejecutando para los logs.

        Returns:
            Page: El objeto `Page` de la ventana/pestaña a la que se ha cambiado el foco exitosamente.

        Raises:
            IndexError: Si se proporciona un índice fuera de rango.
            ValueError: Si no se encuentra ninguna pestaña que coincida con la subcadena.
            TypeError: Si el tipo de `opcion_ventana` no es `int` ni `str`.
            AssertionError: Si ocurre un error inesperado durante el proceso de cambio de foco.
        """
        self.logger.info(f"\n--- {nombre_paso}: Intentando cambiar el foco a la ventana/pestaña: '{opcion_ventana}' ---")
        
        target_page_to_focus: Optional[Page] = None
        
        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            # 1. Obtener todas las páginas actuales en el contexto del navegador
            self.logger.debug("\n  --> Recuperando todas las páginas en el contexto del navegador...")
            # --- Medición de rendimiento: Inicio de recuperación de páginas ---
            start_time_get_pages = time.time()
            all_pages_in_context = self.page.context.pages
            # --- Medición de rendimiento: Fin de recuperación de páginas ---
            end_time_get_pages = time.time()
            duration_get_pages = end_time_get_pages - start_time_get_pages
            self.logger.info(f"PERFORMANCE: Tiempo de recuperación de todas las páginas en el contexto: {duration_get_pages:.4f} segundos.")

            self.logger.info(f"\n  Ventanas/pestañas abiertas actualmente: {len(all_pages_in_context)}")
            for i, p in enumerate(all_pages_in_context):
                try:
                    self.logger.info(f"\n    [{i}] URL: {p.url} | Título: {p.title()}")
                except Exception as e:
                    self.logger.warning(f"\n    [{i}] No se pudo obtener URL/Título: {e}")

            # 2. Buscar la página objetivo basada en la opción_ventana
            self.logger.debug(f"\n  --> Buscando la página objetivo '{opcion_ventana}'...")
            # --- Medición de rendimiento: Inicio de búsqueda de página objetivo ---
            start_time_find_target_page = time.time()

            if isinstance(opcion_ventana, int):
                if 0 <= opcion_ventana < len(all_pages_in_context):
                    target_page_to_focus = all_pages_in_context[opcion_ventana]
                    self.logger.info(f"  --> Seleccionada por índice: {opcion_ventana}")
                else:
                    error_msg = f"\n❌ FALLO: El índice '{opcion_ventana}' está fuera del rango de pestañas abiertas (0-{len(all_pages_in_context)-1})."
                    self.logger.error(error_msg)
                    self.base.tomar_captura(f"{nombre_base}_error_indice_invalido", directorio)
                    raise IndexError(error_msg)
            elif isinstance(opcion_ventana, str):
                # Intentar encontrar por URL o título
                found_match = False
                for p in all_pages_in_context:
                    try:
                        if opcion_ventana in p.url or opcion_ventana in p.title():
                            target_page_to_focus = p
                            found_match = True
                            self.logger.info(f"\n  --> Seleccionada por coincidencia de URL/Título: '{opcion_ventana}' (URL: {p.url}, Título: {p.title()})")
                            break
                    except Error as e:
                        # La página podría haberse cerrado justo en el momento de acceder a URL/title
                        self.logger.warning(f"\n  --> Error de Playwright al acceder a URL/título de una página durante la búsqueda: {e}")
                
                if not found_match:
                    error_msg = f"\n❌ FALLO: No se encontró ninguna pestaña con la URL o título que contenga '{opcion_ventana}'."
                    self.logger.error(error_msg)
                    self.base.tomar_captura(f"{nombre_base}_error_no_coincidencia_foco", directorio)
                    raise ValueError(error_msg)
            else:
                error_msg = f"\n❌ FALLO: El tipo de 'opcion_ventana' no es válido. Debe ser int o str (tipo recibido: {type(opcion_ventana).__name__})."
                self.logger.error(error_msg)
                self.base.tomar_captura(f"{nombre_base}_error_tipo_opcion_foco", directorio)
                raise TypeError(error_msg)
            
            # --- Medición de rendimiento: Fin de búsqueda de página objetivo ---
            end_time_find_target_page = time.time()
            duration_find_target_page = end_time_find_target_page - start_time_find_target_page
            self.logger.info(f"PERFORMANCE: Tiempo de búsqueda de la página objetivo: {duration_find_target_page:.4f} segundos.")

            # 3. Cambiar el foco si la página objetivo no es la actual
            if target_page_to_focus == self.page:
                self.logger.info(f"\n✅ El foco ya está en la ventana seleccionada (URL: {self.page.url}). No es necesario cambiar.")
            else:
                self.logger.debug(f"\n  --> Cambiando el foco de '{self.page.url}' a '{target_page_to_focus.url}'...")
                # --- Medición de rendimiento: Inicio del cambio de foco ---
                start_time_switch_focus = time.time()
                self.page = target_page_to_focus
                # --- Medición de rendimiento: Fin del cambio de foco ---
                end_time_switch_focus = time.time()
                duration_switch_focus = end_time_switch_focus - start_time_switch_focus
                self.logger.info(f"PERFORMANCE: Tiempo de asignación del foco (self.page = ...): {duration_switch_focus:.4f} segundos.")
                
                self.logger.info(f"\n✅ Foco cambiado exitosamente a la ventana/pestaña seleccionada.")
            
            # 4. Reportar el estado final y tomar captura
            self.logger.info(f"\n  URL de la pestaña actual: {self.page.url}")
            self.logger.info(f"\n  Título de la pestaña actual: {self.page.title()}")
            self.base.tomar_captura(f"{nombre_base}_foco_cambiado", directorio)

            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (cambio de foco entre ventanas): {duration_total_operation:.4f} segundos.")
            
            return self.page # Retorna la página a la que se cambió el foco

        except (IndexError, ValueError, TypeError) as e:
            # Captura errores de validación de entrada o de búsqueda de la página
            self.logger.critical(f"\n❌ FALLO (Validación) - {nombre_paso}: {e}", exc_info=True)
            # La captura ya se tomó en los bloques if/elif donde se lanzó el error
            raise # Re-lanzar la excepción original para que el test falle

        except Error as e:
            # Captura errores específicos de Playwright
            error_msg = (
                f"\n❌ FALLO (Playwright) - {nombre_paso}: Ocurrió un error de Playwright al intentar cambiar el foco de ventana.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_playwright_cambiar_foco", directorio)
            raise AssertionError(error_msg) from e

        except Exception as e:
            # Captura cualquier otra excepción inesperada
            error_msg = (
                f"\n❌ FALLO (Inesperado) - {nombre_paso}: Ocurrió un error inesperado al intentar cambiar el foco de ventana.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_inesperado_cambiar_foco", directorio)
            raise AssertionError(error_msg) from e

    def cerrar_pestana_especifica(self, page_to_close: Page, nombre_base: str, directorio: str, nombre_paso: str = "") -> None:
        """
        Cierra un objeto `Page` específico proporcionado.
        Si la página que se va a cerrar es la actualmente activa (`self.page`),
        la función intentará cambiar el foco a la primera página disponible
        en el contexto del navegador. Mide el rendimiento de estas operaciones.

        Args:
            page_to_close (Page): El objeto `Page` específico que se desea cerrar.
            nombre_base (str): Nombre base utilizado para las **capturas de pantalla**
                               tomadas durante la ejecución de la función.
            directorio (str): **Ruta del directorio** donde se guardarán las capturas de pantalla.
            nombre_paso (str): Una descripción opcional del paso que se está ejecutando para los logs.

        Raises:
            AssertionError: Si ocurre un error de Playwright o un error inesperado
                            durante el cierre de la pestaña o el cambio de foco.
        """
        # --- Medición de rendimiento: Inicio total de la función ---
        start_time_total_operation = time.time()

        try:
            closed_url = "N/A (Página no válida o ya cerrada)"
            try:
                # Intenta obtener la URL para el log, pero maneja el error si la página ya está cerrada
                if page_to_close and not page_to_close.is_closed():
                    closed_url = page_to_close.url
                self.logger.info(f"\n--- {nombre_paso}: Intentando cerrar la pestaña con URL: {closed_url} ---")
            except Error as e:
                self.logger.warning(f"\nNo se pudo obtener la URL de la página a cerrar. Podría estar inactiva: {e}")

            if not page_to_close or page_to_close.is_closed():
                self.logger.info(f"\n ℹ️ La pestaña (URL: {closed_url}) ya estaba cerrada o no es un objeto Page válido. No se requiere acción.")
                # --- Medición de rendimiento: Fin total de la función (sin acción real) ---
                end_time_total_operation = time.time()
                duration_total_operation = end_time_total_operation - start_time_total_operation
                self.logger.info(f"PERFORMANCE: Tiempo total de la operación (pestaña ya cerrada): {duration_total_operation:.4f} segundos.")
                return # Salir si la página ya está cerrada o no es válida

            # 1. Determinar si la página a cerrar es la página actual (self.page)
            # --- Medición de rendimiento: Inicio de la detección de página actual ---
            start_time_is_current_page_check = time.time()
            is_current_page = (self.page == page_to_close)
            # --- Medición de rendimiento: Fin de la detección de página actual ---
            end_time_is_current_page_check = time.time()
            duration_is_current_page_check = end_time_is_current_page_check - start_time_is_current_page_check
            self.logger.info(f"PERFORMANCE: Tiempo de verificación si es la página actual: {duration_is_current_page_check:.4f} segundos.")

            self.logger.debug(f"\n  --> Tomando captura antes de cerrar la pestaña: {closed_url}")
            self.base.tomar_captura(f"{nombre_base}_antes_de_cerrar_especifica", directorio)
            
            # 2. Cerrar la pestaña específica
            self.logger.debug(f"\n  --> Procediendo a cerrar la pestaña: {closed_url}")
            # --- Medición de rendimiento: Inicio del cierre de la pestaña ---
            start_time_close_page = time.time()
            page_to_close.close()
            # --- Medición de rendimiento: Fin del cierre de la pestaña ---
            end_time_close_page = time.time()
            duration_close_page = end_time_close_page - start_time_close_page
            self.logger.info(f"PERFORMANCE: Tiempo de cierre de la pestaña '{closed_url}': {duration_close_page:.4f} segundos.")
            
            self.logger.info(f"\n✅ Pestaña '{closed_url}' cerrada exitosamente.")
            # No se toma una captura después de cerrar la página porque ya no es accesible.

            # 3. Si la página cerrada era la página actual (self.page), cambiar el foco
            if is_current_page:
                self.logger.info("\n  --> Detectado: La pestaña cerrada era la pestaña activa.")
                # --- Medición de rendimiento: Inicio del cambio de foco ---
                start_time_switch_focus = time.time()
                # Buscar la primera página disponible en el contexto
                if self.page.context.pages:
                    self.page = self.page.context.pages[0]
                    # --- Medición de rendimiento: Fin del cambio de foco ---
                    end_time_switch_focus = time.time()
                    duration_switch_focus = end_time_switch_focus - start_time_switch_focus
                    self.logger.info(f"PERFORMANCE: Tiempo de cambio de foco a la nueva pestaña activa: {duration_switch_focus:.4f} segundos.")

                    self.logger.info(f"\n🔄 Foco cambiado automáticamente a la primera pestaña disponible: URL = {self.page.url}")
                    self.base.tomar_captura(f"{nombre_base}_foco_cambiado_despues_cerrar", directorio)
                else:
                    self.logger.warning("\n⚠️ No hay más pestañas abiertas en el contexto del navegador. La instancia 'self.page' ahora es None.")
                    self.page = None # No hay página activa en este contexto
                    self.logger.info("PERFORMANCE: No se realizó cambio de foco, no hay más páginas en el contexto.")
            else:
                self.logger.info("\n  --> La pestaña cerrada no era la pestaña activa. El foco actual permanece sin cambios.")
            
            # --- Medición de rendimiento: Fin total de la función ---
            end_time_total_operation = time.time()
            duration_total_operation = end_time_total_operation - start_time_total_operation
            self.logger.info(f"PERFORMANCE: Tiempo total de la operación (cierre de pestaña específica y gestión de foco): {duration_total_operation:.4f} segundos.")

        except Error as e: # Captura errores específicos de Playwright
            # Esto puede ocurrir si la página ya se cerró por alguna razón externa, o si hubo un problema con el contexto.
            if "Target page, context or browser has been closed" in str(e) or "Page closed" in str(e):
                self.logger.warning(f"\n⚠️ Advertencia (Playwright): La pestaña ya estaba cerrada o el contexto ya no es válido durante la operación. Detalles: {e}")
                # En este caso, no necesitamos relanzar una excepción, ya que el objetivo (cerrar la página)
                # se cumple implícitamente o la página ya estaba en el estado deseado.
                # Asegúrate de que el estado de self.page es consistente si se cerró la activa
                if self.page and self.page.is_closed():
                    self.logger.warning("\n  --> La página activa se ha cerrado. Intentando reasignar el foco.")
                    if self.page.context.pages:
                        self.page = self.page.context.pages[0]
                        self.logger.info(f"\n  --> Foco reasignado a: {self.page.url}")
                    else:
                        self.page = None
                        self.logger.warning("\n  --> No hay más páginas en el contexto. self.page es None.")
            else:
                error_msg = (
                    f"\n❌ FALLO (Playwright Error) - {nombre_paso}: Ocurrió un error de Playwright al intentar cerrar la pestaña.\n"
                    f"Detalles: {e}"
                )
                self.logger.critical(error_msg, exc_info=True)
                self.base.tomar_captura(f"{nombre_base}_error_cerrar_pestana_playwright", directorio)
                raise AssertionError(error_msg) from e
        except Exception as e:
            error_msg = (
                f"\n❌ FALLO (Inesperado) - {nombre_paso}: Ocurrió un error al intentar cerrar la pestaña.\n"
                f"Detalles: {e}"
            )
            self.logger.critical(error_msg, exc_info=True)
            self.base.tomar_captura(f"{nombre_base}_error_cerrar_pestana", directorio)
            raise AssertionError(error_msg) from e