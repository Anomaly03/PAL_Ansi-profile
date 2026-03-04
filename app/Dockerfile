# ───────────────────────────────────────────────────
# Dockerfile — Web Profile App Container
# ───────────────────────────────────────────────────
FROM python:3.12-slim

LABEL maintainer="ansible-docker-demo"
LABEL description="Simple web profile for Ansible + Docker teaching demo"

WORKDIR /app

# Copy static assets into the directory the server expects
COPY index.html style.css ./static/

# Copy the application server
COPY server.py .

# Expose the internal port the Python server listens on
EXPOSE 8080

# CONTAINER_NAME is passed at runtime by Docker / Ansible
ENV PORT=8080
ENV CONTAINER_NAME=webprofile

CMD ["python", "server.py"]
