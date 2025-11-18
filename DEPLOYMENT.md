# Guía de Dockerización y Despliegue en Google Cloud Run

Esta guía detalla el proceso completo para dockerizar y desplegar la aplicación Look-It backend en Google Cloud Run.

## Prerrequisitos

- Docker instalado y funcionando
- Google Cloud SDK (`gcloud`) instalado y configurado
- Cuenta de Google Cloud con un proyecto activo
- Permisos necesarios para crear repositorios en Artifact Registry y servicios en Cloud Run

## Configuración Inicial

### 1. Configurar el proyecto de Google Cloud

```bash
# Verificar el proyecto actual
gcloud config get-value project

# Si necesitas cambiar de proyecto
gcloud config set project TU_PROJECT_ID
```

### 2. Variables de Entorno

Define las siguientes variables según tu configuración:

```bash
export REGION="europe-southwest1"  # O tu región preferida
export AR_REPO="look-it-repo"      # Nombre para tu repositorio de Artifact Registry
export PROJECT_ID=$(gcloud config get-value project)
export IMAGE_TAG="latest"           # Tag para tu imagen (ej: latest, v1.0, google_auth)
```

## Paso 1: Dockerizar la Aplicación

### 1.1 Construir la Imagen Docker

Desde el directorio raíz del proyecto, construye la imagen Docker optimizada para la plataforma de Cloud Run:

```bash
docker build --platform linux/amd64 -t look-it-backend:$IMAGE_TAG .
```

**Nota:** El flag `--platform linux/amd64` es importante porque Cloud Run ejecuta contenedores en arquitectura AMD64, incluso si estás desarrollando en una Mac con Apple Silicon.

### 1.2 Verificar la Imagen Local

Opcionalmente, puedes probar la imagen localmente antes de subirla:

```bash
docker run -p 8080:8080 look-it-backend:$IMAGE_TAG
```

Luego visita `http://localhost:8080` para verificar que la aplicación funciona correctamente.

## Paso 2: Configurar Artifact Registry

### 2.1 Crear el Repositorio (Solo la Primera Vez)

Si es la primera vez que despliegas, necesitas crear el repositorio en Artifact Registry:

```bash
gcloud artifacts repositories create $AR_REPO \
    --repository-format=docker \
    --location=$REGION \
    --description="Repositorio Docker para Look-It backend"
```

### 2.2 Configurar Autenticación Docker

Configura Docker para autenticarse con Artifact Registry:

```bash
gcloud auth configure-docker $REGION-docker.pkg.dev
```

## Paso 3: Subir la Imagen a Artifact Registry

### 3.1 Etiquetar la Imagen

Etiqueta tu imagen local con la ruta completa del Artifact Registry:

```bash
docker tag look-it-backend:$IMAGE_TAG \
    $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:$IMAGE_TAG
```

### 3.2 Subir la Imagen

Haz push de la imagen al repositorio:

```bash
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:$IMAGE_TAG
```

Este proceso puede tardar varios minutos dependiendo del tamaño de la imagen y tu conexión a internet.

## Paso 4: Desplegar en Cloud Run

### 4.1 Desplegar el Servicio

Despliega tu aplicación en Cloud Run usando la imagen que acabas de subir:

```bash
gcloud run deploy look-it-backend-service \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:$IMAGE_TAG \
    --service-account look-it-backend@look-it-478017.iam.gserviceaccount.com \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --min-instances 0 \
    --cpu 1
```

**Parámetros explicados:**
- `--image`: Ruta completa de la imagen en Artifact Registry
- `--region`: Región donde se desplegará el servicio
- `--platform managed`: Usa la plataforma completamente gestionada de Cloud Run
- `--allow-unauthenticated`: Permite acceso público sin autenticación
- `--min-instances 0`: Permite escalar a cero cuando no hay tráfico (reduce costos)
- `--cpu 1`: Asigna 1 CPU al contenedor
- `--memory 512Mi`: Asigna 512MB de memoria (ajusta según necesidades)

### 4.2 Verificar el Despliegue

Una vez completado el despliegue, obtén la URL del servicio:

```bash
gcloud run services describe look-it-backend-service \
    --region $REGION \
    --format 'value(status.url)'
```

También puedes ver el estado del servicio en la [Consola de Google Cloud](https://console.cloud.google.com/run).

## Actualizaciones Futuras

Para actualizar la aplicación después de hacer cambios:

1. **Construir nueva imagen:**
   ```bash
   docker build --platform linux/amd64 -t look-it-backend:$IMAGE_TAG .
   ```

2. **Etiquetar y subir:**
   ```bash
   docker tag look-it-backend:$IMAGE_TAG \
       $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:$IMAGE_TAG
   docker push $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:$IMAGE_TAG
   ```

3. **Redesplegar:**
   ```bash
   gcloud run deploy look-it-backend-service \
       --image $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:$IMAGE_TAG \
       --region $REGION
   ```

## Scripts de Automatización

Si prefieres automatizar el proceso, puedes crear scripts que combinen estos pasos:

### Script Completo de Build y Push

```bash
#!/bin/bash
set -e

export REGION="europe-southwest1"
export AR_REPO="look-it-repo"
export PROJECT_ID=$(gcloud config get-value project)
export IMAGE_TAG=${1:-latest}

echo "Construyendo imagen Docker..."
docker build --platform linux/amd64 -t look-it-backend:$IMAGE_TAG .

echo "Etiquetando imagen..."
docker tag look-it-backend:$IMAGE_TAG \
    $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:$IMAGE_TAG

echo "Subiendo imagen a Artifact Registry..."
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:$IMAGE_TAG

echo "Imagen subida exitosamente!"
```

### Script de Despliegue

```bash
#!/bin/bash
set -e

export REGION="europe-southwest1"
export AR_REPO="look-it-repo"
export PROJECT_ID=$(gcloud config get-value project)
export IMAGE_TAG=${1:-latest}

echo "Desplegando en Cloud Run..."
gcloud run deploy look-it-backend-service \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:$IMAGE_TAG \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --min-instances 0 \
    --cpu 1 \
    --memory 512Mi

echo "Obteniendo URL del servicio..."
SERVICE_URL=$(gcloud run services describe look-it-backend-service \
    --region $REGION \
    --format 'value(status.url)')

echo "Servicio desplegado en: $SERVICE_URL"
```

## Solución de Problemas

### Error: "Repository not found"
- Verifica que el repositorio existe: `gcloud artifacts repositories list --location=$REGION`
- Si no existe, créalo con el comando del Paso 2.1

### Error: "Permission denied"
- Verifica tus permisos: `gcloud projects get-iam-policy $PROJECT_ID`
- Asegúrate de tener los roles necesarios: Artifact Registry Writer y Cloud Run Admin

### Error: "Image pull failed"
- Verifica que la imagen existe: `gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend`
- Confirma que el tag es correcto

### La aplicación no carga correctamente
- Verifica los logs: `gcloud run services logs read look-it-backend-service --region $REGION`
- Asegúrate de que la aplicación escucha en el puerto 8080 (requerido por Cloud Run)

## Recursos Adicionales

- [Documentación de Cloud Run](https://cloud.google.com/run/docs)
- [Documentación de Artifact Registry](https://cloud.google.com/artifact-registry/docs)
- [Dockerfile de referencia](Dockerfile)

