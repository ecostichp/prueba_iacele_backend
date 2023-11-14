#!/usr/bin/env bash
set -eo pipefail

# Create mount directory for service
mkdir -p $GCSFUSE_MOUNT_DIR

echo "Mounting Google Cloud Store Fuse."
gcsfuse --debug_gcs --debug_fuse $BUCKET_NAME $GCSFUSE_MOUNT_DIR
echo "Mounting completed."

# Run the web service on container startup. Here we use the gunicorn
exec uvicorn iaCeleApp:app --host 0.0.0.0 --port 8080