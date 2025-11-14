# Inicialización del Backend: Armario Inteligente y Generación de Looks

Este documento define la estructura inicial propuesta para el backend del proyecto, basada en FastAPI y orientada a la digitalización y gestión inteligente de prendas.

## Estructura de Carpetas y Archivos

```
/app
├── /api
│   └── v1
│       ├── auth_router.py          # Endpoint para validar token de Google
│       ├── garment_router.py       # Endpoints para subir/listar prendas
│       └── look_router.py          # Endpoint para generar look
├── /core
│   ├── auth_service.py             # Lógica de validación del token
│   ├── garment_service.py          # Lógica de subida, rembg y GCS
│   ├── image_processor.py          # Función que encapsula Azure CV y rembg
│   ├── look_generator.py           # Algoritmo de combinación de looks
│   └── config_service.py           # Inicialización y gestión de secretos (GSM)
├── /db
│   └── mongo_models.py             # Definición del esquema para GarmentItem
├── main.py                         # Inicialización de FastAPI y routers
└── settings.py                     # Configuración y llamada a config_service
README.md                         # Instrucciones básicas del proyecto
requirements.txt                  # Dependencias necesarias del backend
```

## Descripción de Componentes Clave

- **/api/v1/**: Routers para los endpoints principales (autenticación, prendas, generación de looks).
- **/core/**: Servicios de negocio y utilidades (validación de token, procesamiento de imágenes, lógica de combinación, gestión de configuración y secretos).
- **/db/**: Modelos y esquemas de MongoDB.
- **main.py**: Punto de entrada de la aplicación FastAPI.
- **settings.py**: Configuración global y carga de variables críticas.

## Consideraciones Técnicas

- El backend procesará imágenes en memoria usando `rembg` antes de subirlas a Google Cloud Storage.
- La clasificación de imágenes se realizará con Azure Computer Vision.
- La autenticación se basa en Google OAuth, validando el token en cada petición protegida.
- Los secretos y credenciales se gestionarán mediante Google Secret Manager.
- MongoDB almacenará usuarios y prendas, siguiendo el modelo definido en el plan.

---
