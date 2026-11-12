#!/usr/bin/env bash
set -Eeuo pipefail

echo "======================================"
echo "Inicializando la aplicación FastAPI"
echo "======================================"

# Variables
# Asegura la existencia del directorio donde se montará el almacenamiento
MOUNT_DIR="${GCSFUSE_MOUNT_DIR:-/backend/bucket}"

# Validar nombre del bucket
if [[ -z "${BUCKET_NAME:-}" ]]; then
    echo "ERROR: BUCKET_NAME no está configurado."
    exit 1
fi

# Crear directorio de montaje
mkdir -p "$MOUNT_DIR"

echo "Bucket: $BUCKET_NAME"
echo "Mount directory: $MOUNT_DIR"

# Montar Google Cloud Storage
echo "Mounting Google Cloud Storage..."

# # Descomentar para montar el bucket, en este momento el bucket no existe.
# gcsfuse \
#     --implicit-dirs \
#     "$BUCKET_NAME" \
#     "$MOUNT_DIR"

# # Verificar montaje
# if ! mountpoint -q "$MOUNT_DIR"; then
#     echo "ERROR: Falló la verificación de montaje de GCSFuse."
#     exit 1
# fi

# echo "GCSFuse mounted successfully."

# En el contenedor la app usa el conector de Cloud SQL, no el socket de Cloud Run.
export DB_MODE=cloudsql

: "${GCLOUD_SQL_NAME:?ERROR: GCLOUD_SQL_NAME no está configurado.}"
: "${GCLOUD_SQL_DB:?ERROR: GCLOUD_SQL_DB no está configurado.}"
: "${GCLOUD_SQL_USER:?ERROR: GCLOUD_SQL_USER no está configurado.}"
: "${GCLOUD_SQL_PASSWORD:?ERROR: GCLOUD_SQL_PASSWORD no está configurado.}"

echo "DB_MODE=${DB_MODE}"
echo "Cloud SQL: ${GCLOUD_SQL_NAME} / ${GCLOUD_SQL_DB}"

# Iniciar FastAPI
echo "Iniciando Uvicorn..."

exec uvicorn iaCeleApp:app \
    --host 0.0.0.0 \
    --port 8080 \
    