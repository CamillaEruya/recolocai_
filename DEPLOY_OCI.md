# Guia de Deploy na OCI (VM Ubuntu ou Container Instances)

Este passo a passo explica como subir a aplicação `Recoloca IA` na Oracle Cloud Infrastructure.

## Pré-requisitos
- Conta OCI ativa
- Chave SSH pública (para VM)
- Docker instalado na VM (para opções com Container Instance também é possível)

---

## Opção A — VM Ubuntu (mais simples)

1. Na OCI Console -> Compute -> Instances -> Create Instance
   - Image: Ubuntu
   - Shape: VM.Standard.E2.1.Micro ou equivalente
   - Configure network e adicione sua chave SSH pública

2. Conecte via SSH:

```bash
ssh -i sua_chave.pem ubuntu@IP_PUBLICO
```

3. Instale Docker e Git:

```bash
sudo apt update
sudo apt install -y docker.io git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

4. Clone o repositório e rode:

```bash
git clone <seu-repositorio.git>
cd camila
cp .env.example .env
# Edite .env se necessário
./scripts/deploy_vm.sh
```

5. Abra a porta 80 no Security List da subnet (Ingress rule TCP 80 0.0.0.0/0)

6. Acesse `http://<IP_PUBLICO>` no navegador.

---

## Opção B — OCI Container Registry + Container Instance

1. Construa e tague a imagem localmente:

```bash
docker build -t recoloca-ia:latest .
docker tag recoloca-ia:latest <region>.ocir.io/<tenancy>/<repo>/recoloca-ia:latest
```

2. Faça login no OCIR (use seu namespace e auth token):

```bash
docker login <region>.ocir.io -u '<tenancy>/<namespace>/<username>' -p '<auth-token>'
docker push <region>.ocir.io/<tenancy>/<repo>/recoloca-ia:latest
```

3. Crie um Container Instance apontando para essa imagem e exponha a porta `8000` (ou configure `PORT=8000`).

---

## Notas finais
- Para usar domínio/HTTPS, coloque um Nginx reverso na VM ou use Load Balancer na OCI e um certificado TLS.
- Mantenha segredos (tokens, senhas) fora do repositório; use Vault ou variáveis de ambiente no OCI.
