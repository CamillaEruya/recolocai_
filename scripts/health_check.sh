#!/bin/sh
# Verifica o endpoint / (homepage) e /recommendations
set -e

HOST=${HOST:-http://localhost:8000}

echo "Verificando $HOST/"
curl -fS "$HOST/" >/dev/null && echo "OK: / disponível" || (echo "Falha: /"; exit 2)

echo "Verificando $HOST/recommendations"
curl -sSf "$HOST/recommendations" | jq . >/dev/null && echo "OK: /recommendations retornou JSON" || (echo "Falha: /recommendations"; exit 2)

echo "Health-check concluído."
