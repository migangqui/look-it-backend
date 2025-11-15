# !/bin/bash

# Formato: REPOSITORY_HOST/PROJECT_ID/REPOSITORY_NAME/IMAGE_NAME:TAG
export REGION="europe-southwest1" # O tu región preferida
export AR_REPO="look-it-repo" # Un nombre para tu repositorio
export PROJECT_ID=$(gcloud config get-value project)

gcloud run deploy look-it-backend-service \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/look-it-backend:latest \
    --service-account look-it-backend@look-it-478017.iam.gserviceaccount.com \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --min-instances 0 \
    --cpu 1

# Para verificar la URL en cualquier momento:
gcloud run services describe look-it-backend-service --region $REGION --format 'value(status.url)'