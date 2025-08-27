FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG GID=1042
ARG UID=1042

# Ensure packages are available.
RUN apt-get update

# Install system dependencies, including libmagic1 for MIME type detection
RUN DEBIAN_FRONTEND=noninteractive \
    apt-get install -qy \
    libmagic1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .
RUN pip install --upgrade pip
RUN pip install uv
RUN pip install .

# Add deploy use to match server.
RUN addgroup --gid ${GID} deploy \
    && useradd --gid ${GID} --uid ${UID} --home-dir /home/deploy --create-home --shell /bin/bash deploy

# Ensure app is owned by deploy
RUN chown -R deploy:deploy /app

USER deploy

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
