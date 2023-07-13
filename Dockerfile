
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Set the current working directory to the container image and copy requirements.txt
WORKDIR /backend

# install psycopg dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Update pip.
RUN pip install --no-cache-dir -U pip

# Install production dependencies.
COPY ./requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy local code to the container image.
COPY ./app /backend/app

# Run the web service on container startup. Here we use the gunicorn
CMD exec uvicorn app.main:app --host 0.0.0.0 --port 8080