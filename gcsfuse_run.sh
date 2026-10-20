#!/usr/bin/env bash
set -eo pipefail

# Asegura la existencia del directorio donde se montará el almacenamiento
mkdir -p "$GCSFUSE_MOUNT_DIR"

echo "Mounting Google Cloud Storage Fuse..."

# Monta el bucket. --implicit-dirs permite que Python y Pandas localicen carpetas generadas externamente
gcsfuse --implicit-dirs "$BUCKET_NAME" "$GCSFUSE_MOUNT_DIR"

echo "Mounting completed con éxito."

# Inicia FastAPI reemplazando el proceso del script (exec). Usa 4 trabajadores para producción.
exec uvicorn iaCeleApp:app --host 0.0.0.0 --port 8080 --workers 4
