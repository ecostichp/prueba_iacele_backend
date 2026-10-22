# Python 3.14 con Debian Bookworm
FROM python:3.14-slim-bookworm

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GCSFUSE_MOUNT_DIR=/backend/uploadfiles \
    DEBIAN_FRONTEND=noninteractive

# Directorio de trabajo
WORKDIR /backend

# Dependencias del sistema
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        tini \
        ca-certificates \
        curl \
        gnupg \
        fuse3 \
        libpq5 \
        build-essential \
        libpq-dev; \
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL \
        https://packages.cloud.google.com/apt/doc/apt-key.gpg \
        | gpg --dearmor \
        -o /etc/apt/keyrings/cloud.google.gpg; \
    echo "deb [signed-by=/etc/apt/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt gcsfuse-bookworm main" \
        > /etc/apt/sources.list.d/gcsfuse.list; \
    apt-get update; \
    apt-get install -y --no-install-recommends gcsfuse; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

# Copiar dependencias primero para aprovechar caché
COPY ./requirements.txt /backend/requirements.txt

# Actualizar pip e instalar dependencias
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir \
        -r /backend/requirements.txt

# Copiar aplicación
COPY ./iaCeleApp /backend/iaCeleApp

# Copiar script de arranque
COPY ./gcsfuse_run.sh /backend/gcsfuse_run.sh

# Permisos de ejecución y directorio de montaje
RUN chmod +x /backend/gcsfuse_run.sh \
    && mkdir -p /backend/bucket

# Gestión de señales y procesos
ENTRYPOINT ["/usr/bin/tini", "--"]

# Script de arranque
CMD ["/bin/bash", "/backend/gcsfuse_run.sh"]
