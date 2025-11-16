# !/bin/bash
cd .
# Construir la imagen Docker
docker build --platform linux/amd64 -t look-it-backend .

# Formato: REPOSITORY_HOST/PROJECT_ID/REPOSITORY_NAME/IMAGE_NAME:TAG
export REGION="europe-southwest1" # O tu región preferida
export AR_REPO="look-it-repo" # Un nombre para tu repositorio
export PROJECT_ID=$(gcloud config get-value project)

# Crear el repositorio (solo la primera vez)
#gcloud artifacts repositories create $AR_REPO --repository-format=docker --location=$REGION

# Etiquetar la imagen local
docker tag look-it-backend $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:latest

docker push $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:latest