#!/bin/sh
# Script de exemplo para tag e push para OCIR (Oracle Cloud Registry)
set -e

# Variáveis necessárias:
# OCIR_REGION e OCIR_REPO devem ser fornecidas.
OCIR_REGION=${OCIR_REGION:-<region>}
TENANCY=${TENANCY:-<tenancy>}
REPO=${REPO:-<repo>}
IMAGE_NAME=${IMAGE_NAME:-recoloca-ia}
TAG=${TAG:-latest}

if [ "$OCIR_REGION" = "<region>" ]; then
  echo "Por favor, defina OCIR_REGION, TENANCY e REPO nas variáveis de ambiente.";
  exit 1
fi

FULL_NAME="$OCIR_REGION.ocir.io/$TENANCY/$REPO/$IMAGE_NAME:$TAG"

echo "Tagging $IMAGE_NAME -> $FULL_NAME"
docker tag "$IMAGE_NAME:$TAG" "$FULL_NAME"

echo "Faça login no OCIR (use auth token como senha)"
echo "docker login $OCIR_REGION.ocir.io -u '<tenancy>/<namespace>/<username>' -p '<auth-token>'"

echo "Depois de logado, rode: docker push $FULL_NAME"

echo ""
echo "Exemplos de uso com N8N_CHAT_URL"
echo "1) Push da imagem permanece o mesmo. Para rodar localmente com a variável:
  export N8N_CHAT_URL='https://seu-n8n-host/chat'
  docker run -e N8N_CHAT_URL="$N8N_CHAT_URL" -p 8000:8000 $FULL_NAME"

echo "2) Ao criar uma OCI Container Instance, adicione a variável de ambiente na spec do container. Exemplo (OCI CLI):"
echo "  oci container instance create --display-name recoloca-ia --container-config file://container-config.json --compartment-id <compartment> --shape 'VM.Standard.E2.1'
  # em container-config.json inclua 'env' dentro de 'containers[0].environmentVariables' com N8N_CHAT_URL"

echo "3) Alternativamente, use o Secret/Config do provedor para injetar a URL em production instead of baking it into the image."
