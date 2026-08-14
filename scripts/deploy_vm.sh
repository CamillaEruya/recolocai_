#!/bin/sh
# Script para buildar a imagem e rodar no host (ex.: VM Ubuntu na OCI)
set -e

IMAGE_NAME=${IMAGE_NAME:-recoloca-ia}
PORT=${PORT:-8000}
ENV_FILE=${ENV_FILE:-.env}

echo "Construindo imagem: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

echo "Parando container antigo (se existir)"
docker rm -f "$IMAGE_NAME" >/dev/null 2>&1 || true

echo "Iniciando container na porta 80 -> $PORT"
# If N8N_CHAT_URL is set in the environment, pass it explicitly to the container
EXTRA_ENV=""
if [ -n "$N8N_CHAT_URL" ]; then
	EXTRA_ENV="-e N8N_CHAT_URL=$N8N_CHAT_URL"
fi

docker run -d --name "$IMAGE_NAME" -p 80:${PORT} $EXTRA_ENV --env-file "$ENV_FILE" "$IMAGE_NAME"

echo "Container iniciado. Abra http://<IP_DA_VM> para acessar."
