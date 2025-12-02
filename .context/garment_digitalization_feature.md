# Feature: Digitalización de Prendas (MVP)

## Resumen

Esta feature permite a los usuarios subir imágenes de prendas de ropa que serán procesadas automáticamente para:
1. Eliminar el fondo de la imagen usando `rembg`
2. Clasificar la prenda usando Azure Computer Vision
3. Asignar un rol a la prenda basándose en su tipo
4. Almacenar la imagen procesada en Google Cloud Storage
5. Guardar los metadatos en MongoDB

Los usuarios pueden luego listar todas sus prendas digitalizadas.

## Requisitos Previos

### Dependencias Instaladas
Las siguientes dependencias ya están en `requirements.txt`:
- `rembg` - Para eliminación de fondo
- `azure-cognitiveservices-vision-computervision` - Para clasificación de imágenes
- `google-cloud-storage` - Para almacenamiento de imágenes
- `fastapi` - Framework web
- `motor` - Driver asíncrono para MongoDB
- `pydantic` - Validación de datos

### Configuración Existente
- ✅ Autenticación JWT implementada (`app/core/auth_service.py`)
- ✅ Modelos de datos definidos (`app/db/mongo_models.py`)
- ✅ Repositorio de prendas creado (`app/db/repository/garmentitem_repository.py`)
- ✅ Configuración de secretos desde Google Secret Manager (`app/core/config_service.py`)
- ✅ Conexión a MongoDB configurada (`app/db/mongo_config.py`)

### Secretos Necesarios en Google Secret Manager
- `AZURE_COMPUTER_VISION_KEY` - Clave de API de Azure Computer Vision
- `MONGO_URI` - URI de conexión a MongoDB
- `JWT_SECRET` - Secreto para firmar tokens JWT

### Configuración Adicional Requerida
- **Bucket de Google Cloud Storage**: `look-it-storage` (configurar en código, no requiere secreto por ahora)
- **Endpoint de Azure Computer Vision**: `https://style-app.cognitiveservices.azure.com/` (configurar en código o settings)

## Arquitectura

### Flujo de Datos

```
Cliente (Frontend)
    ↓ [POST /api/v1/garment/upload]
    ↓ Headers: Authorization: Bearer <JWT>
    ↓ Body: multipart/form-data con archivo de imagen
Router (garment_router.py)
    ↓ Valida JWT → get_current_user()
    ↓ Extrae archivo de la petición
GarmentService (garment_service.py)
    ↓ Llama a ImageProcessor
ImageProcessor (image_processor.py)
    ↓ 1. Procesa imagen con rembg (en memoria)
    ↓ 2. Envía imagen procesada a Azure CV (en memoria)
    ↓ Retorna: imagen procesada (bytes) + clasificación
GarmentService (garment_service.py)
    ↓ 3. Mapea type → role (TODO: definir mapeo)
    ↓ 4. Sube imagen procesada a GCS → storage_url
    ↓ 5. Crea GarmentItem con metadatos
    ↓ 6. Guarda en MongoDB vía repository
    ↓ Retorna: GarmentItem creado
Router (garment_router.py)
    ↓ Retorna respuesta JSON al cliente
```

### Componentes

1. **`image_processor.py`**: Procesamiento de imágenes (rembg + Azure CV)
2. **`garment_service.py`**: Orquestación del flujo completo
3. **`garment_router.py`**: Endpoints REST API
4. **`garmentitem_repository.py`**: Acceso a datos (ya existe)

## Tareas de Implementación

### Tarea 1: Implementar `app/core/image_processor.py`

**Objetivo**: Crear funciones para procesar imágenes en memoria usando rembg y Azure Computer Vision.

**Funciones a implementar**:

#### `process_image(image_bytes: bytes) -> dict`
Procesa una imagen recibida como bytes en memoria.

**Pasos**:
1. Usar `rembg` para eliminar el fondo de la imagen
   - Importar: `from rembg import remove`
   - Procesar: `output_bytes = remove(image_bytes)`
   - Mantener todo en memoria (no escribir archivos temporales)

2. Enviar la imagen procesada a Azure Computer Vision para clasificación
   - Importar: `from azure.cognitiveservices.vision.computervision import ComputerVisionClient`
   - Importar: `from msrest.authentication import CognitiveServicesCredentials`
   - Configurar cliente con:
     - Endpoint: `https://style-app.cognitiveservices.azure.com/`
     - Key: desde `app.settings.AZURE_CV_KEY`
   - Usar `analyze_image()` o `tag_image()` para obtener tags/clasificación
   - Extraer el tipo de prenda más relevante de los resultados

3. Retornar diccionario con:
   ```python
   {
       "processed_image_bytes": bytes,  # Imagen sin fondo
       "type": str,  # Tipo clasificado por Azure CV (ej: "shirt", "pants", etc.)
       "tags": list,  # Tags adicionales si están disponibles
       "color": str,  # Color detectado si está disponible (opcional)
   }
   ```

**Consideraciones**:
- Todo el procesamiento debe ser en memoria usando `io.BytesIO` si es necesario
- Manejar errores de Azure CV (timeout, invalid image, etc.)
- Validar que la imagen es válida antes de procesar

**Dependencias**:
- `app.settings.AZURE_CV_KEY`
- Configurar endpoint de Azure CV (puede ser constante o en settings)

---

### Tarea 2: Implementar `app/core/garment_service.py`

**Objetivo**: Orquestar el flujo completo de digitalización de prendas.

**Funciones a implementar**:

#### `async def upload_garment(user_id: str, image_bytes: bytes, filename: str) -> GarmentItem`
Función principal que coordina todo el proceso.

**Pasos**:
1. **Procesar imagen**:
   - Llamar a `image_processor.process_image(image_bytes)`
   - Obtener imagen procesada y clasificación

2. **Mapear type → role**:
   - Recibir el `type` de Azure CV
   - Aplicar lógica de mapeo para asignar `role`
   - **TODO**: Definir mapeo completo. Por ahora, crear función placeholder:
     ```python
     def map_type_to_role(type: str) -> str:
         # Mapeo básico (expandir según necesidad)
         type_lower = type.lower()
         if "shirt" in type_lower or "top" in type_lower or "blouse" in type_lower:
             return "Superior Primario"
         elif "jacket" in type_lower or "coat" in type_lower:
             return "Capa"
         elif "pants" in type_lower or "jeans" in type_lower or "trousers" in type_lower:
             return "Inferior"
         elif "shoe" in type_lower or "boot" in type_lower or "sneaker" in type_lower:
             return "Calzado"
         else:
             return "Otro"  # O lanzar error si no se puede clasificar
     ```

3. **Subir imagen a Google Cloud Storage**:
   - Importar: `from google.cloud import storage`
   - Crear cliente de GCS (usará credenciales por defecto de la aplicación)
   - Bucket: `look-it-storage`
   - Generar nombre único para el archivo (ej: `{user_id}/{timestamp}_{filename}`)
   - Subir `processed_image_bytes` al bucket
   - Obtener URL pública o signed URL → `storage_url`

4. **Crear registro en MongoDB**:
   - Crear instancia de `GarmentItem`:
     ```python
     garment = GarmentItem(
         user_id=user_id,
         storage_url=storage_url,
         type=type_from_azure,  # Tipo original de Azure CV
         role=mapped_role,  # Rol mapeado
         color=color_from_azure if available else None,
         occasion=None,  # Por ahora None, se puede añadir después
         creation_date=datetime.now(timezone.utc)
     )
     ```
   - Guardar usando `garmentitem_repository.save(garment)`
   - Retornar el `GarmentItem` creado

**Manejo de errores**:
- Si el procesamiento de imagen falla → HTTPException 400
- Si Azure CV falla → HTTPException 502 o 500
- Si GCS falla → HTTPException 500
- Si MongoDB falla → HTTPException 500

**Dependencias**:
- `app.core.image_processor`
- `app.db.mongo_models.GarmentItem`
- `app.db.repository.garmentitem_repository`
- `app.settings` (si se necesita configuración adicional)

---

### Tarea 3: Crear `app/api/v1/garment_router.py`

**Objetivo**: Exponer endpoints REST para subir y listar prendas.

**Endpoints a implementar**:

#### `POST /api/v1/garment`
Endpoint protegido para subir una prenda.

**Especificaciones**:
- **Autenticación**: Requerida (usar `Depends(get_current_user)`)
- **Content-Type**: `multipart/form-data`
- **Parámetros**:
  - `file`: Archivo de imagen (FastAPI `UploadFile`)
- **Respuesta exitosa** (200):
  ```json
  {
    "id": "string",
    "user_id": "string",
    "storage_url": "string",
    "type": "string",
    "role": "string",
    "color": "string | null",
    "occasion": "string | null",
    "creation_date": "ISO datetime string"
  }
  ```
- **Errores**:
  - 401: Token JWT inválido o ausente
  - 400: Archivo inválido o formato no soportado
  - 500: Error interno del servidor

**Implementación**:
```python
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.auth_service import get_current_user
from app.core.garment_service import upload_garment

router = APIRouter()

@router.post
async def upload_garment_endpoint(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    # Validar tipo de archivo (imagen)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
    
    # Leer contenido del archivo
    image_bytes = await file.read()
    
    # Obtener user_id del token JWT
    user_id = current_user.get("sub")
    
    # Procesar y guardar prenda
    garment = await upload_garment(
        user_id=user_id,
        image_bytes=image_bytes,
        filename=file.filename
    )
    
    return garment.model_dump()
```

#### `GET /api/v1/garments`
Endpoint protegido para listar prendas del usuario autenticado.

**Especificaciones**:
- **Autenticación**: Requerida (usar `Depends(get_current_user)`)
- **Respuesta exitosa** (200):
  ```json
  [
    {
      "id": "string",
      "user_id": "string",
      "storage_url": "string",
      "type": "string",
      "role": "string",
      "color": "string | null",
      "occasion": "string | null",
      "creation_date": "ISO datetime string"
    },
    ...
  ]
  ```
- **Errores**:
  - 401: Token JWT inválido o ausente
  - 500: Error interno del servidor

**Implementación**:
```python
from app.db.repository.garmentitem_repository import find_by_user_id

@router.get
async def list_garments(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("sub")
    garments = await find_by_user_id(user_id)
    return [garment.model_dump() for garment in garments]
```

#### `PATCH /api/v1/garments/{garment_id}`
Endpoint protegido para editar propiedades de una prenda existente.

**Especificaciones**:
- **Autenticación**: Requerida (usar `Depends(get_current_user)`)
- **Content-Type**: `application/json`
- **Parámetros de ruta**:
  - `garment_id`: ID de la prenda a editar (string)
- **Body** (actualización parcial, todos los campos opcionales):
  ```json
  {
    "type": "string | null",
    "role": "string | null",
    "color": "string | null",
    "occasion": "string | null"
  }
  ```
- **Respuesta exitosa** (200):
  ```json
  {
    "id": "string",
    "user_id": "string",
    "storage_url": "string",
    "type": "string",
    "role": "string",
    "color": "string | null",
    "occasion": "string | null",
    "creation_date": "ISO datetime string"
  }
  ```
- **Errores**:
  - 401: Token JWT inválido o ausente
  - 400: ID de prenda inválido o formato incorrecto
  - 403: La prenda no pertenece al usuario autenticado
  - 404: Prenda no encontrada
  - 500: Error interno del servidor

**Restricciones**:
- No se puede editar `storage_url` (campo bloqueado)
- No se puede editar `user_id`, `id`, ni `creation_date` (campos inmutables)
- Solo se pueden editar: `type`, `role`, `color`, `occasion`
- La actualización es parcial: solo se actualizan los campos enviados en el body

**Implementación**:

1. **Crear modelo Pydantic para el request**:
```python
from pydantic import BaseModel
from typing import Optional

class GarmentUpdate(BaseModel):
    type: Optional[str] = None
    role: Optional[str] = None
    color: Optional[str] = None
    occasion: Optional[str] = None
```

2. **Añadir método al repositorio** (`app/db/repository/garmentitem_repository.py`):
```python
async def update_by_id(garment_id: str, user_id: str, update_data: dict) -> Optional[GarmentItem]:
    """
    Update a garment by ID, ensuring it belongs to the specified user.
    
    Args:
        garment_id: The ID of the garment to update
        user_id: The ID of the user who owns the garment
        update_data: Dictionary with fields to update (excludes storage_url, user_id, id, creation_date)
        
    Returns:
        Updated GarmentItem if found and updated, None if not found
        
    Raises:
        ValueError: If garment_id is not a valid ObjectId
    """
    try:
        object_id = ObjectId(garment_id)
    except InvalidId:
        raise ValueError(f"Invalid garment ID format: {garment_id}")
    
    # Filter out immutable fields
    allowed_fields = {"type", "role", "color", "occasion"}
    filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields and v is not None}
    
    if not filtered_data:
        # No valid fields to update
        raise ValueError("No valid fields to update")
    
    result = await garment_items_collection.find_one_and_update(
        {"_id": object_id, "user_id": user_id},
        {"$set": filtered_data},
        return_document=True
    )
    
    if result:
        return GarmentItem(**result)
    return None
```

3. **Añadir función al servicio** (`app/core/garment_service.py`):
```python
async def update_garment(garment_id: str, user_id: str, update_data: dict) -> GarmentItem:
    """
    Update a garment's properties.
    
    Args:
        garment_id: ID of the garment to update
        user_id: ID of the user who owns the garment
        update_data: Dictionary with fields to update
        
    Returns:
        Updated GarmentItem
        
    Raises:
        HTTPException: 404 if garment not found, 403 if not owner, 400 if invalid data
    """
    from app.db.repository.garmentitem_repository import update_by_id
    
    try:
        updated_garment = await update_by_id(garment_id, user_id, update_data)
        
        if not updated_garment:
            raise HTTPException(
                status_code=404,
                detail=f"Garment with ID {garment_id} not found or does not belong to the user"
            )
        
        return updated_garment
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating garment: {str(e)}")
```

4. **Añadir endpoint al router** (`app/api/v1/garment_router.py`):
```python
from app.core.garment_service import update_garment

@router.patch("/{garment_id}")
async def update_garment_endpoint(
    garment_id: str,
    update_data: GarmentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a garment's properties by ID.
    
    Requires authentication. Only allows updating garments belonging to the authenticated user.
    Supports partial updates - only include fields you want to update.
    """
    # Get user_id from JWT token
    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid JWT token: missing user_id")
    
    # Convert Pydantic model to dict, excluding None values
    update_dict = update_data.model_dump(exclude_none=True)
    
    # Update garment
    updated_garment = await update_garment(
        garment_id=garment_id,
        user_id=user_id,
        update_data=update_dict
    )
    
    return updated_garment.model_dump()
```

**Montaje del router**:
- Descomentar en `app/main.py`:
  ```python
  app.include_router(garment_router.router, prefix="/api/v1/garments")
  ```

---

### Tarea 4: Configuración Adicional

#### Actualizar `app/settings.py`
Añadir configuración para Azure CV endpoint y GCS bucket (si se desea centralizar):

```python
AZURE_CV_ENDPOINT = "https://style-app.cognitiveservices.azure.com/"
GCS_BUCKET_NAME = "look-it-storage"
```

O mantener como constantes en los archivos correspondientes.

#### Verificar Permisos de GCS
Asegurar que la aplicación tiene permisos para escribir en el bucket `look-it-storage`:
- Si se ejecuta en Cloud Run: verificar que el service account tiene `Storage Object Creator`
- Si se ejecuta localmente: configurar credenciales de aplicación (`GOOGLE_APPLICATION_CREDENTIALS`)

## Detalles Técnicos

### Procesamiento en Memoria

**Importante**: Todo el procesamiento debe realizarse en memoria para evitar:
- Crear archivos temporales en disco
- Problemas de concurrencia
- Limpieza de archivos temporales

**Ejemplo de uso de rembg en memoria**:
```python
from rembg import remove
from io import BytesIO

def process_with_rembg(image_bytes: bytes) -> bytes:
    output_bytes = remove(image_bytes)
    return output_bytes
```

**Ejemplo de uso de Azure CV con bytes**:
```python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from io import BytesIO

client = ComputerVisionClient(
    endpoint=AZURE_CV_ENDPOINT,
    credentials=CognitiveServicesCredentials(AZURE_CV_KEY)
)

# Analizar imagen desde bytes
image_stream = BytesIO(image_bytes)
result = client.tag_image_in_stream(image_stream)
```

### Estructura de Datos

**GarmentItem** (ya definido en `mongo_models.py`):
- `id`: ObjectId convertido a string
- `user_id`: ID del usuario (de JWT)
- `storage_url`: URL completa de la imagen en GCS
- `type`: Tipo clasificado por Azure CV (ej: "shirt", "pants")
- `role`: Rol asignado (ej: "Superior Primario", "Inferior")
- `color`: Color detectado (opcional)
- `occasion`: Ocasión de uso (opcional, None por ahora)
- `creation_date`: Fecha de creación

### Validaciones

1. **Tipo de archivo**: Solo aceptar imágenes (content-type: `image/*`)
2. **Tamaño de archivo**: Considerar límite máximo (ej: 10MB)
3. **Formato de imagen**: Validar que es una imagen válida antes de procesar
4. **Usuario autenticado**: Todos los endpoints requieren JWT válido

## Consideraciones y TODOs

### Mapeo Type → Role (PENDIENTE)

**Estado**: Pendiente de definir mapeo completo.

**Tipos posibles de Azure CV** (ejemplos):
- Shirt, T-shirt, Blouse → "Superior Primario"
- Jacket, Coat, Blazer → "Capa"
- Pants, Jeans, Trousers, Shorts → "Inferior"
- Shoes, Boots, Sneakers, Sandals → "Calzado"
- Dress, Skirt → ¿"Inferior" o nueva categoría?
- Accessories (hats, bags, etc.) → ¿Nueva categoría o ignorar?

**Acción requerida**:
1. Probar Azure CV con imágenes reales para ver qué tipos devuelve
2. Definir mapeo completo basado en resultados reales
3. Considerar casos edge (prendas ambiguas, múltiples tags, etc.)
4. Implementar función de mapeo robusta con fallback

### Manejo de Errores

Considerar casos especiales:
- Azure CV no puede clasificar la imagen → ¿Qué hacer?
- rembg falla → ¿Devolver imagen original o error?
- GCS temporalmente no disponible → ¿Retry o error inmediato?

### Optimizaciones Futuras

- Cache de resultados de Azure CV para imágenes similares
- Procesamiento asíncrono para imágenes grandes
- Validación de calidad de imagen antes de procesar
- Soporte para múltiples imágenes en una sola petición
- Extracción automática de color dominante de la imagen

## Testing

### Casos de Prueba Sugeridos

1. **Upload exitoso**:
   - Subir imagen válida → Verificar que se procesa, sube a GCS y guarda en DB

2. **Autenticación**:
   - Intentar subir sin token → 401
   - Intentar subir con token inválido → 401

3. **Validación de archivo**:
   - Subir archivo que no es imagen → 400
   - Subir imagen corrupta → Manejar error apropiadamente

4. **Listar prendas**:
   - Usuario con prendas → Retorna lista
   - Usuario sin prendas → Retorna lista vacía
   - Verificar que solo retorna prendas del usuario autenticado

## Referencias

- [Azure Computer Vision API Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/)
- [rembg Documentation](https://github.com/danielgatis/rembg)
- [Google Cloud Storage Python Client](https://cloud.google.com/storage/docs/reference/libraries#client-libraries)
- [FastAPI File Uploads](https://fastapi.tiangolo.com/tutorial/request-files/)

