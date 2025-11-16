# Backend Tasks: Armario Inteligente y Generación de Looks

## Fase 0: Creación de Estructura de Proyecto

*   [x] **[Estructura - Backend]** Crear la estructura de carpetas y archivos base para FastAPI:

    /app
    ├── /api/v1 (auth_router.py, garment_router.py, look_router.py)
    ├── /core (auth_service.py, garment_service.py, image_processor.py, look_generator.py, config_service.py)
    ├── /db (mongo_models.py)
    ├── main.py
    └── settings.py

## Fase 1: Setup / Fundacional

*   [x] **[Setup - Backend Config]** Crear la lógica de inicialización y conexión a Google Secret Manager (GSM) en el nuevo archivo app/core/config_service.py.

*   [x] **[Setup - Backend Config]** Modificar app/settings.py para llamar a config_service y cargar de forma segura las claves de MongoDB, Azure CV, y cualquier otra credencial.

*   [x] **[Setup Backend]** Configurar el proyecto FastAPI, añadiendo dependencias en el fichero **requirements.txt** dependencias clave (e.g., `python-jose`, `Pydantic`, `motor` para MongoDB, `rembg`, etc.).
    * Dependencias principales:
        - fastapi
        - uvicorn
        - python-jose (JWT)
        - pydantic
        - motor (MongoDB)
        - rembg
        - google-cloud-storage
        - google-cloud-secret-manager
        - azure-cognitiveservices-vision-computervision
        - python-dotenv (opcional para variables de entorno)

*   [x] **[Setup - BBDD]** Crear los modelos Pydantic/clases en app/db/mongo_models.py con los siguientes campos definitivos:

    * Colección users: _id (PK), google_id (Índice Único), email, creation_date.

    * Colección garment_items: _id (PK), user_id (Referencia), storage_url, type, role (ej: Superior Primario, Capa, Inferior), color, occasion, creation_date.

*   [x] **[Setup - Backend Core]** Configurar la inicialización principal de FastAPI en app/main.py, asegurando la conexión a MongoDB y el montaje de routers.

* * * * *

## Fase 2: Historia 1: Autenticación Rápida (MVP)

*   [ ] **[HU 1 Backend]** Implementar el servicio `app/core/auth_service.py` para:

    *   Validar el token ID de Google.

    *   Buscar o crear el usuario en la colección `users` de MongoDB usando `google_id`.

    *   Generar un token JWT propio para el usuario autenticado y devolverlo al frontend. Este JWT se usará para autenticar las siguientes peticiones a la API.

*   [ ] **[HU 1 Backend]** Implementar la protección de endpoints y validación del token JWT:
    *   Crear una dependencia de seguridad en FastAPI que valide el JWT recibido en el header Authorization.
    *   Usar esta dependencia en todos los endpoints que requieran autenticación, devolviendo error 401 si el token no es válido o está expirado.

*   [ ] **[HU 1 Backend]** Crear el *router* `app/api/v1/auth_router.py` con el *endpoint* POST (`/login`) que recibe el token de Google y devuelve el token JWT interno.

* * * * *

### Fase 3: Historia 2: Digitalización de Prendas (MVP)

*   [ ] **[HU 2 Backend]** Implementar la lógica de procesamiento en `app/core/image_processor.py` (función que llama a `rembg` y luego a Azure CV, utilizando *streams* de bytes para el procesamiento **en memoria**).

*   [ ] **[HU 2 Backend]** Implementar la lógica central en `app/core/garment_service.py` que:

    *   Utiliza `image_processor` para obtener la imagen limpia y la clasificación.

    *   Asigna el role (Superior Primario, Capa, Inferior, etc.) basándose en el type clasificado.

    *   Sube la imagen limpia a GCS.

    *   Guarda el registro en MongoDB.

*   [ ] **[HU 2 Backend]** Crear el *router* `app/api/v1/garment_router.py` con:

    *   Un *endpoint* POST (`/upload`) protegido con autenticación para recibir el archivo.

    *   Un *endpoint* GET (`/list`) para listar las prendas del usuario autenticado.

* * * * *

### Fase 4: Historia 3: Generación de Looks Automáticos (MVP)

*   [ ] **[HU 3 Backend]** Crear el servicio app/core/look_generator.py que implemente el Algoritmo de Capas V1. Este debe usar el campo role para aplicar las reglas de combinación: (DEBE tener 1 Inferior + 1 Calzado; PUEDE tener máx. 1 Superior Primario y máx. 1 Capa).

*   [ ] **[HU 3 Backend]** Crear el *router* `app/api/v1/look_router.py` con un *endpoint* POST (`/generate`) protegido con autenticación que llama al `look_generator`.
