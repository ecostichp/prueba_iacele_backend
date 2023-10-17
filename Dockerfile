
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-buster

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True


# Install system dependencies
RUN set -e; \
    apt-get update -y && apt-get install -y \
    tini \
    lsb-release; \
    gcsFuseRepo=gcsfuse-`lsb_release -c -s`; \
    echo "deb https://packages.cloud.google.com/apt $gcsFuseRepo main" | \
    tee /etc/apt/sources.list.d/gcsfuse.list; \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key add -; \
    apt-get update; \
    apt-get install -y gcsfuse \
    && apt-get clean

# install psycopg dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*    


# Set fallback mount directory
ENV MNT_DIR /mnt/gcsfuse

# Set the current working directory to the container image
WORKDIR /backend

# Copy local code to the container image.
COPY ./app /backend/app


# Update pip.
RUN pip install --no-cache-dir -U pip

# Copy requirements.txt and install production dependencies.
COPY ./requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Copy and ensure the script is executable
COPY ./gcsfuse_run.sh /backend/gcsfuse_run.sh
RUN chmod +x /backend/gcsfuse_run.sh

# Use tini to manage zombie processes and signal forwarding
# https://github.com/krallin/tini
ENTRYPOINT ["/usr/bin/tini", "--"]

# Pass the startup script as arguments to Tini
CMD ["/backend/gcsfuse_run.sh"]
