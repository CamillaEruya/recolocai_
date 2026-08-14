# Release — Recoloca IA

Conteúdo do pacote de release:

- Código backend: `main.py`, `models.py`
- Frontend: `static/` (HTML/CSS)
- Dependências: `requirements.txt`
- Dockerfile e scripts de deploy em `scripts/`
- Manual de deployment: `DEPLOY_OCI.md`

Como gerar o zip de release localmente:

```bash
python scripts/package_release.py
# o zip ficará em releases/recoloca-ia-release.zip
```

Notas finais:
- Remova segredos antes de publicar (variáveis em `.env` não devem ser commitadas).
- Testes rápidos: `pytest -q`.
