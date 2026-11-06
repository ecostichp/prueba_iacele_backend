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

# En el contenedor la app siempre usa el socket de Cloud SQL.
export DB_MODE=cloudsql
export PGGSSENCMODE=disable
export PGSSLNEGOTIATION=postgres

: "${GCLOUD_SQL_NAME:?ERROR: GCLOUD_SQL_NAME no está configurado.}"
: "${GCLOUD_SQL_DB:?ERROR: GCLOUD_SQL_DB no está configurado.}"
: "${GCLOUD_SQL_USER:?ERROR: GCLOUD_SQL_USER no está configurado.}"
: "${GCLOUD_SQL_PASSWORD:?ERROR: GCLOUD_SQL_PASSWORD no está configurado.}"

SQL_SOCKET_DIR="${GCLOUD_SQL_NAME}"
if [[ "${SQL_SOCKET_DIR}" != /* ]]; then
    SQL_SOCKET_DIR="/cloudsql/${SQL_SOCKET_DIR}"
fi
SQL_SOCKET="${SQL_SOCKET_DIR}/.s.PGSQL.5432"

echo "DB_MODE=${DB_MODE}"
echo "Esperando el socket de PostgreSQL en ${SQL_SOCKET}"

for _ in $(seq 1 30); do
    if [[ -S "${SQL_SOCKET}" ]]; then
        echo "Socket de Cloud SQL listo."
        break
    fi
    sleep 1
done

if [[ ! -S "${SQL_SOCKET}" ]]; then
    echo "ERROR: no aparece el socket de PostgreSQL en ${SQL_SOCKET}."
    echo "Cloud Run tiene que tener conectada la instancia ${SQL_SOCKET_DIR}."
    exit 1
fi

# Iniciar FastAPI
echo "Iniciando Uvicorn..."

exec uvicorn iaCeleApp:app \
    --host 0.0.0.0 \
    --port 8080 \
    