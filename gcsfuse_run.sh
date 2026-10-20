#!/usr/bin/env bash
set -Eeuo pipefail

echo "======================================"
echo "Inicializando la aplicación FastAPI"
echo "======================================"

# Variables
# Asegura la existencia del directorio donde se montará el almacenamiento
MOUNT_DIR="${GCSFUSE_MOUNT_DIR:-/backend/uploadfiles}"

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

gcsfuse \
    --implicit-dirs \
    "$BUCKET_NAME" \
    "$MOUNT_DIR"

# Verificar montaje
if ! mountpoint -q "$MOUNT_DIR"; then
    echo "ERROR: Falló la verificación de montaje de GCSFuse."
    exit 1
fi

echo "GCSFuse mounted successfully."

# Iniciar FastAPI
echo "Iniciando Uvicorn..."

exec uvicorn iaCeleApp:app \
    --host 0.0.0.0 \
    --port 8080 \
    