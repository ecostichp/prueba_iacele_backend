# Usa la versión más actual y estable de Debian Slim para Python 3.14
FROM python:3.14-slim-bookworm

# Variables de entorno para optimizar logs, evitar archivos temporales y configurar rutas
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GCSFUSE_MOUNT_DIR=/backend/uploadfiles \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /backend

# INSTALACIÓN DE GCSFUSE (Método oficial compatible con Debian Bookworm)
RUN set -e; \
    apt-get update && apt-get install -y --no-install-recommends \
    tini \
    ca-certificates \
    curl \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl https://google.com | gpg --dearmor -o /etc/apt/keyrings/cloud.google.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/cloud.google.gpg] https://google.com gcsfuse-bookworm main" | tee /etc/apt/sources.list.d/gcsfuse.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcsfuse \
    && apt-get purge -y --auto-remove curl gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requerimientos ANTES del código para maximizar el uso de la caché de Docker
COPY ./requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación y el script de arranque
COPY ./iaCeleApp /backend/iaCeleApp
COPY ./gcsfuse_run.sh /backend/gcsfuse_run.sh
RUN chmod +x /backend/gcsfuse_run.sh

# Manejo correcto de señales del sistema y procesos zombie con Tini
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/backend/gcsfuse_run.sh"]
