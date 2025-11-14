# Look-It Backend

Backend para la aplicación de Armario Inteligente y Generación de Looks.

## Estructura del proyecto

```
/app
├── /api/v1
│   ├── auth_router.py
│   ├── garment_router.py
│   └── look_router.py
├── /core
│   ├── auth_service.py
│   ├── garment_service.py
│   ├── image_processor.py
│   ├── look_generator.py
│   └── config_service.py
├── /db
│   └── mongo_models.py
├── main.py
└── settings.py
```

## Instalación

1. Clona el repositorio y accede a la carpeta `look-it-backend`.
2. Crea y activa un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Dependencias principales
- fastapi
- uvicorn
- python-jose (JWT)
- pydantic
- motor (MongoDB)
- rembg
- google-cloud-storage
- google-cloud-secret-manager
- azure-cognitiveservices-vision-computervision
- python-dotenv

## Configuración
- Configura las variables de entorno necesarias (por ejemplo, GCP_PROJECT_ID).
- Los secretos se gestionan mediante Google Secret Manager.

## Ejecución
```bash
uvicorn app.main:app --reload
```
