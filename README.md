# Challenge Alura — Backend + Webhook (n8n)

Este repositório contém um scaffold simples em Python com FastAPI para receber webhooks do n8n, um frontend minimalista para visualizar payloads e arquivos básicos para deploy.

Como usar (local):

1. Crie e ative um ambiente virtual (opcional):

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Rode a aplicação:

```bash
uvicorn main:app --reload
```

Se você usa o chat n8n para o onboarding (modal do Quiz), configure a variável antes de iniciar:

```powershell
$env:N8N_CHAT_URL='https://seu-n8n-host/chat'
% For Linux/macOS:
export N8N_CHAT_URL='https://seu-n8n-host/chat'
```

4. Abra `http://localhost:8000/` para ver o monitor de webhooks e testar com o formulário.

Testar com n8n:

- Configure um webhook no n8n que aponte para `http://SEU_HOST:8000/webhook/{webhookId}` (use o `webhookId` do seu workflow). Ex.: `http://meuip:8000/webhook/c5d6507b-f421-4f5e-94a2-6541b24d2035`.
- Para testar localmente com n8n.cloud ou um serviço externo, use `ngrok` para expor sua porta 8000:

```bash
ngrok http 8000
```

Observações:

- Armazenamento é em memória (apenas para estudo). Para produção, persista em banco de dados.
- O projeto inclui `Procfile` e `Dockerfile` para deploy em plataformas como Heroku, Render ou Docker.

**Deploy**

Docker (build & run local):

```bash
docker build -t challenge-alura .
docker run -p 8000:8000 -e PORT=8000 -e N8N_CHAT_URL="https://seu-n8n-host/chat" challenge-alura
```

OCI / Oracle Cloud Infrastructure (recomendado para o seu caso):

Opção 1 - VM Ubuntu na OCI:

1. Crie uma instância Ubuntu na OCI.
2. Instale Docker e Git na VM.
3. Clone o projeto e rode:

```bash
git clone <seu-repositorio>
cd camila
cp .env.example .env
sudo docker build -t recoloca-ia .
sudo docker run -d --name recoloca-ia -p 80:8000 --env-file .env recoloca-ia

Observação: inclua `N8N_CHAT_URL` em seu `.env` (veja `.env.example`) ou exporte antes de rodar. O script `scripts/deploy_vm.sh` também aceita a variável `N8N_CHAT_URL` do ambiente e a repassa ao container.
```

4. Abra a porta 80 ou 443 no security list da OCI.
5. Acesse a IP pública da VM no navegador. Exemplo:

```bash
http://<IP_PUBLICA>
```

Opção 2 - OCI Container Instances / Registry:

1. Faça login no OCI Registry.
2. Construa a imagem localmente:

```bash
docker build -t <region>.ocir.io/<tenancy>/<repo>/recoloca-ia:latest .
```

3. Faça push para o registro e deploy via Container Instance.
4. Configure a variável `PORT=8000` e a porta pública do container.

Heroku (deploy Git):

1. Crie app no Heroku: `heroku create nome-do-app`
2. Faça login e suba o código:

```bash
git add .
git commit -m "Deploy"
git push heroku main
```

Heroku usará o `Procfile` para rodar a aplicação. Se usar banco de dados em produção, configure um add-on ou variáveis de ambiente.

Render (deploy):

- Pelo painel, escolha "New -> Web Service" e conecte o repositório.
- Como build command use `pip install -r requirements.txt` e start command `uvicorn main:app --host 0.0.0.0 --port $PORT`.

Observação sobre banco de dados:

- O projeto usa SQLite por padrão (`database.db`). Em produção, troque por Postgres/MySQL e configure `DATABASE_URL`.

