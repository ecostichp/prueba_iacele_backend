#!/usr/bin/env bash
set -eo pipefail

# Create mount directory for service
mkdir -p $MNT_DIR

echo "Mounting Google Cloud Store Fuse."
gcsfuse --debug_gcs --debug_fuse $BUCKET_NAME $MNT_DIR
echo "Mounting completed."

exec ls

# Run the web service on container startup. Here we use the gunicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8080