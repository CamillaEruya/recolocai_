# Testes locais e ngrok

Este arquivo descreve como testar a aplicação localmente e como expor a porta com `ngrok` para que o n8n (ou serviços externos) possam enviar webhooks.

1) Rodar a aplicação localmente

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

A aplicação ficará disponível em `http://localhost:8000` e criará o arquivo `database.db` na raiz.

2) Expor local para internet com `ngrok`

- Baixe e instale ngrok: https://ngrok.com/
- Execute (Windows):

```powershell
.\ngrok.exe http 8000
```

- Ou (macOS / Linux):

```bash
ngrok http 8000
```

- Copie o `Forwarding` HTTPS (ex.: `https://abcd1234.ngrok.io`). Esse será seu `BASE_URL` público.

3) Configurar webhooks no n8n

Nas configurações de webhook do seu workflow, aponte para:

- `https://{NGROK_ID}.ngrok.io/webhook/c5d6507b-f421-4f5e-94a2-6541b24d2035` (chat)
- `https://{NGROK_ID}.ngrok.io/webhook/a62a4879-c178-471c-b63a-ef711e27fabd` (form)

4) Exemplos de testes (curl)

- Teste simples (chat webhook):

```bash
curl -X POST "https://{NGROK_ID}.ngrok.io/webhook/c5d6507b-f421-4f5e-94a2-6541b24d2035" \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, quero começar o quiz"}'
```

- Teste de formulário (upload de PDF) — o endpoint aceita multipart/form-data; n8n enviará binários nesse formato:

```bash
curl -X POST "https://{NGROK_ID}.ngrok.io/webhook/a62a4879-c178-471c-b63a-ef711e27fabd" \
  -F "Arquivo_PDF=@/caminho/para/GuiaDeCarreiras.pdf"
```

Observação: o endpoint salva o corpo do request no campo `payload`. Para uploads multipart, o conteúdo será recebido como bytes/string e armazenado no SQLite para inspeção.

5) Verificar dados recebidos

- Interface web: abra `http://localhost:8000/` (ou a URL do ngrok) e veja as mensagens recebidas na página.
- API: consulte `GET /messages` para listar as entradas salvas no banco:

```bash
curl http://localhost:8000/messages
```

6) Troubleshooting rápido

- Se `curl` retornar erro de conexão, verifique se `uvicorn` está rodando e se o firewall permite a porta 8000.
- No ngrok: se a URL mudar, atualize os webhooks no n8n.
- Para depurar payloads complexos, use `curl -v` para ver cabeçalhos e corpo.

7) Próximos passos recomendados

- Trocar SQLite por Postgres em produção (CONFIG: `DATABASE_URL`).
- Criar endpoints REST para CRUD de perfis (quiz) para uso pelos nodes do n8n.
