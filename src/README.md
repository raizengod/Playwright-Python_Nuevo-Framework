# Mejora framework de Automatización de Pruebas UI con Playwright y Python 🧪

## 🚀 Descripción General
Este proyecto representa una evolución en nuestro enfoque de automatización de pruebas de UI. El framework ha sido reestructurado desde cero para implementar las mejores prácticas de la industria, como el Page Object Model (POM). El objetivo es ofrecer una solución de automatización modular, escalable y mantenible, que valida la funcionalidad de la UI de manera robusta y genera reportes detallados.

## ✨ Características Principales
* **Arquitectura de Page Object Model (POM) Modular:** A diferencia de una estructura monolítica, este framework separa la lógica de interacción en clases de acción especializadas (actions_elementos.py, actions_navegacion.py, etc.), con una clase BasePage que actúa como un agregador central. Esto mejora la mantenibilidad, reutilización de código y facilita la escalabilidad del framework.

* **Gestión de Entornos Centralizada:** El framework utiliza archivos .env dedicados (dev.env, qa.env, staging.env, prod.env) para gestionar la configuración de cada entorno. Esto elimina la necesidad de modificar el código para cambiar de URL base o credenciales, haciendo la ejecución de pruebas más segura y flexible.

* **Configuración Dinámica con conftest.py y pyproject.toml:** Se han centralizado las configuraciones, fixtures y ganchos de Pytest en un solo archivo. Se ha añadido pyproject.toml para configurar automáticamente las opciones de ejecución de Pytest, como el nivel de verbosidad y la generación de reportes HTML.

* **Generación de Datos de Prueba:** La inclusión de la librería Faker nos permite crear usuarios, contraseñas, nombres y correos electrónicos realistas y aleatorios para cada ejecución, lo cual es fundamental para evitar la repetición de datos y habilitar tests más dinámicos y efectivos.

* **Sistema de Logging Avanzado:** La nueva clase logger.py proporciona un sistema de logging detallado que permite configurar distintos niveles de severidad para los mensajes que se imprimen en la consola y los que se guardan en el archivo de log.

* **Ejecución Paralela de Pruebas:** La configuración para la ejecución de pruebas en paralelo utilizando pytest-xdist reduce significativamente el tiempo de ejecución del suite de pruebas completo.

* **Reportes de Calidad con pytest-reporter-html1:** El framework genera reportes en formato HTML que ofrecen una visualización completa de los resultados de las pruebas, facilitando la identificación de fallos y la revisión de la ejecución.

## 🛠️ Tecnologías Utilizadas
* **Python 3.13.17:** Lenguaje de programación.
* **Playwright:** Librería de automatización de navegadores.
* **Pytest:** Framework de pruebas.
* **Pytest-xdist:** Ejecución de pruebas en paralelo.
* **Pytest-reporter-html1:** Generador de reportes HTML.
* **python-dotenv:** Para la gestión de variables de entorno.
* **Faker:** Módulo para la generación de datos de prueba.
* **requests:** Módulo para la integración de pruebas de rendimiento (futura).

## 📂 Estructura del Proyecto
La estructura del proyecto está diseñada para ser clara, modular y fácil de mantener:
```
.
├── src/
│   ├── environments/              # Archivos de entorno dedicados
│   │   ├── dev.env
│   │   ├── qa.env
│   │   ├── staging.env
│   │   └── prod.env
│   ├── locator/                # Contiene los localizadores de elementos web por página/componente
│   │   ├── __init__.py
│   │   ├── locator_registro.py
│   │   └── ...
│   ├── pages/                  # Contiene las clases Page Object Model (POM)
│   │   ├── __init__.py
│   │   ├── actions_archivos.py
│   │   ├── actions_dialogos.py
│   │   ├── actions_dropdowns.py
│   │   ├── actions_elementos.py
│   │   ├── actions_navegacion.py
│   │   ├── actions_tablas.py
│   │   ├── actions_teclado.py
│   │   └── base_page.py       # Agregador de todas las clases de accióninteracción
│   ├── utils/                  # Utilidades como configuraciones y logger
│   │   ├── __init__.py
│   │   ├── config.py          # Gestión de configuraciones y entornos
│   │   ├── generador_datos.py # Generación de datos de prueba aleatorios
│   │   └── logger.py          # Sistema de logging centralizado
│   ├── test/
│   │   ├── archivos/               # Archivos de prueba (ej. para upload/download)
│   │   │   ├── archivos_data_escritura/
│   │   │   ├── archivos_data_fuente/
│   │   │   ├── archivos_download/
│   │   │   └── archivos_upload/
│   │   ├── reportes/               # Directorio para almacenar evidencias de las pruebas
│   │   │   ├── html/               # Informes HTML
│   │   │   ├── video/              # Grabaciones de video de las ejecuciones
│   │   │   ├── traceview/          # Archivos traceview de Playwright
│   │   │   └── imagen/             # Capturas de pantalla
│   │   ├── test_home.py               # Tests para la página de inicio
│   │   ├── test_login.py              # Tests para la funcionalidad de login
│   │   ├── test_registro.py           # Tests para la funcionalidad de registro
│   │   └── conftest.py                # Fixtures y configuraciones de Pytest
├── .gitignore
├── pyproject.toml                 # Configuración de Pytest (opciones por defecto)
├── requirements.txt               # Dependencias del proyecto
└── README.md                      # Este archivo
```

## ⚙️ Configuración e Instalación
**Clonar el repositorio:**

```bash
git clone https://github.com/raizengod/Playwright-Python_Nuevo-Framework.git
cd src
```

**Crear y activar un entorno virtual (recomendado):**

```bash
python -m venv mv_BC
# En Windows
.\venv\Scripts\activate
# En macOS/Linux
source venv/bin/activate
```

**Instalar las dependencias:**

```bash
pip install -r requirements.txt
playwright install  # Instala los navegadores necesarios (Chromium, Firefox, WebKit)
# (Asegúrate de que pytest-reporter-html1 esté incluido en requirements.txt)
```

```bash
pip install playwright pytest pytest-html openpyxl
playwright install
```

Asegurar Directorios de Evidencias: El archivo config.py define una función ensure_directories_exist() que crea automáticamente las carpetas necesarias para reportes y archivos de datos. Asegúrate de que esta función se ejecute, o créalas manualmente según la Estructura del Proyecto.

## 🚀 Uso
Para ejecutar el suite de pruebas para un entorno específico (por ejemplo, QA), utiliza la variable de entorno ENVIRONMENT o el argumento --env-file.

1.  * **Usando la variable de entorno**
    (Recomendado para CI/CD y automatización)

    ```bash
    # En Windows
    set ENVIRONMENT=qa && pytest --workers 4
    
    # En macOS/Linux
    ENVIRONMENT=qa pytest --workers 4
    ```

2.  **Usando el argumento --env-file**
    (Útil para ejecuciones manuales y debugging)

    ```bash
    pytest --workers 4 --env-file=tests/environments/qa.env
    ```
3.  **Ejecuta prueba de módulo especifico**
    ```bash
    pytest src\test\test_registro.py
    ```

2.  **Ejecutar todas las pruebas con Pytest:**
    ```bash
    pytest src\test\
    ```

3.  **Ejecutar pruebas específicas (ejemplo):**
    ```bash
    pytest src\test\test_login.py::test_login_exitoso_data_json
    ```

4.  **Ejecuta las pruebas en paralelo y genera los resultados de reporte:**
    ```bash
    pytest src\test\ -n 8
    ```
Una vez que la ejecución finalice, el reporte en formato **HTML** se generará automáticamente en la ruta ```reports/html1/playwright_reporte.html.```

## ✅ Habilidades Demostradas
Este framework demuestra habilidades avanzadas en:

* Diseño y arquitectura de frameworks de automatización.
* Implementación de patrones de diseño de software (Page Object Model).
* Gestión de configuraciones y ambientes.
* Generación dinámica de datos de prueba para tests robustos.
* Centralización de la lógica de logging y manejo de excepciones.
* Configuración y optimización de CI/CD para la automatización de QA.
* Gestión de dependencias y entornos de prueba.
* Implementación de reportes de calidad con pytest-reporter-html.
* Integración de pruebas de rendimiento.

## 🔮 Mejoras Futuras / Roadmap
* **Pruebas de API:** Integrar pruebas de API REST para validar la capa de negocio.
* **Integración con Test Management Tools:** Sincronizar los resultados de las pruebas con herramientas como Jira, TestRail o Xray.
* **Dockerización:** Empaquetar el framework en un contenedor de Docker para asegurar un entorno de ejecución consistente.

## Licencia
Este proyecto está bajo la Licencia MIT.

## Autor
[Carlos N](https://github.com/raizengod)