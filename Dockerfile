# Usa la versión más actual y estable de Debian Slim para Python 3.14
FROM python:3.14-slim-bookworm

# Variables de entorno para optimizar logs, evitar archivos temporales y configurar rutas
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    GCSFUSE_MOUNT_DIR=/backend/uploadfiles \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /backend

#  Instalación optimizada y segura de dependencias y gcsfuse
RUN set -e; \
    apt-get update && apt-get install -y --no-install-recommends \
    tini \
    ca-certificates \
    curl \
    fuse3 \
    && curl -L -O https://github.com \
    && dpkg --install gcsfuse_2.4.0_amd64.deb \
    && rm gcsfuse_2.4.0_amd64.deb \
    && apt-get purge -y --auto-remove curl \
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
