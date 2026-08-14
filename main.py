from typing import Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, Response
import os
import json
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from models import engine, SQLModel, WebhookEntry, CareerProfile
import uvicorn
from urllib.parse import quote_plus

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.post("/webhook/{webhook_id}")
async def webhook(webhook_id: str, request: Request):
    """Recebe chamadas de webhook do n8n e persiste no SQLite/Postgres."""
    try:
        payload = await request.json()
    except Exception:
        body = await request.body()
        try:
            payload = body.decode()
        except Exception:
            payload = str(body)

    entry = WebhookEntry(webhook_id=webhook_id, payload=payload)
    try:
        with Session(engine) as session:
            session.add(entry)
            session.commit()
            session.refresh(entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if isinstance(payload, dict):
        profile_candidate = {
            key: payload[key]
            for key in [
                "user_name",
                "area",
                "experience",
                "work_mode",
                "location",
                "soft_skills",
                "career_goal",
                "skills",
                "target_roles",
            ]
            if key in payload
        }
        if profile_candidate:
            try:
                with Session(engine) as session:
                    profile = CareerProfile(**profile_candidate)
                    session.add(profile)
                    session.commit()
                    session.refresh(profile)
                    return JSONResponse({
                        "status": "received",
                        "entry": entry.dict(),
                        "profile": profile.dict(),
                    })
            except Exception:
                pass

    return JSONResponse({"status": "received", "entry": entry.dict()})


@app.get("/messages")
def get_messages():
    with Session(engine) as session:
        stmt = select(WebhookEntry)
        results = session.exec(stmt).all()
        return [r.dict() for r in results]


@app.post("/profiles")
def create_profile(payload: dict[str, Any]):
    profile = CareerProfile(**payload)
    with Session(engine) as session:
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile.dict()


@app.get("/profiles")
def list_profiles():
    with Session(engine) as session:
        results = session.exec(select(CareerProfile)).all()
        return [item.dict() for item in results]


@app.get("/profiles/{profile_id}")
def get_profile(profile_id: int):
    with Session(engine) as session:
        profile = session.get(CareerProfile, profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil não encontrado")
        return profile.dict()


@app.get("/recommendations")
def list_recommendations():
    with Session(engine) as session:
        profile = session.exec(select(CareerProfile).order_by(CareerProfile.id.desc())).first()

    if not profile:
        return {"jobs": [], "courses": []}

    area = (profile.area or "Backend").lower()
    skills = ", ".join(profile.skills or [])

    job_templates = {
        "backend": [
            {"title": "Backend Python Developer", "company": "Nexa Labs", "kind": "Remoto", "match": "Alta compatibilidade"},
            {"title": "Python API Engineer", "company": "ByteWorks", "kind": "Híbrido", "match": "Boa compatibilidade"},
        ],
        "frontend": [
            {"title": "Frontend React Developer", "company": "Veloz Studio", "kind": "Remoto", "match": "Alta compatibilidade"},
            {"title": "UI Engineer", "company": "Nova Pixel", "kind": "Híbrido", "match": "Boa compatibilidade"},
        ],
        "dados": [
            {"title": "Analyst de Dados", "company": "DataFlow", "kind": "Remoto", "match": "Alta compatibilidade"},
            {"title": "Data Analyst Junior", "company": "Insight Lab", "kind": "Híbrido", "match": "Boa compatibilidade"},
        ],
        "full stack": [
            {"title": "Full Stack Developer", "company": "Orbit Tech", "kind": "Remoto", "match": "Alta compatibilidade"},
            {"title": "Full Stack Engineer", "company": "Spark System", "kind": "Híbrido", "match": "Boa compatibilidade"},
        ],
    }

    course_templates = {
        "backend": [
            {"title": "Python para Back-end", "provider": "Alura", "level": "Intermediário"},
            {"title": "APIs em Python com FastAPI", "provider": "Udemy", "level": "Intermediário"},
        ],
        "frontend": [
            {"title": "React do zero ao profissional", "provider": "Alura", "level": "Intermediário"},
            {"title": "HTML, CSS e JavaScript", "provider": "Curso em Vídeo", "level": "Básico"},
        ],
        "dados": [
            {"title": "SQL para análise de dados", "provider": "DataCamp", "level": "Intermediário"},
            {"title": "Python para ciência de dados", "provider": "Coursera", "level": "Intermediário"},
        ],
        "full stack": [
            {"title": "Full Stack com Python e JavaScript", "provider": "Alura", "level": "Intermediário"},
            {"title": "Desenvolvimento web completo", "provider": "Udemy", "level": "Iniciante"},
        ],
    }

    jobs = job_templates.get(area, job_templates["backend"])
    courses = course_templates.get(area, course_templates["backend"])

    if skills:
        jobs = [
            {**job, "match": f"Foco em {skills}" if i == 0 else job["match"]}
            for i, job in enumerate(jobs)
        ]

    # attach search/apply URL to jobs and courses if missing
    def attach_url(item, default_text):
        if "url" in item and item["url"]:
            return item
        q = quote_plus(item.get("title", default_text) + " " + item.get("company", ""))
        item["url"] = f"https://www.google.com/search?q={q}"
        return item

    jobs = [attach_url(job, "vaga") for job in jobs]
    courses = [dict(course, url=f"https://www.google.com/search?q={quote_plus(course.get('title',''))}") for course in courses]

    return {"jobs": jobs[:2], "courses": courses[:2], "area": profile.area if profile else area, "location": profile.location if profile else ""}


@app.post("/chat")
def chat_with_assistant(payload: dict[str, Any]):
    message = str((payload or {}).get("message", "")).strip()
    if not message:
        return {"reply": "Posso te ajudar com vagas, cursos e perfil profissional. Me diga o que você quer saber."}

    with Session(engine) as session:
        profile = session.exec(select(CareerProfile).order_by(CareerProfile.id.desc())).first()

    message_lower = message.lower()
    if any(word in message_lower for word in ["olá", "oi", "oii", "hello", "hey", "bom dia", "boa tarde", "boa noite"]):
        return {"reply": "Olá! Posso te ajudar com vagas, cursos e sugestões de carreira. Me diga sua área ou o que você quer explorar."}

    role_answers = {
        "php": "Um(a) Senior PHP normalmente cuida da arquitetura de aplicações web, revisa código, define boas práticas, integra APIs, otimiza performance, resolve bugs críticos e orienta outros devs da equipe.",
        "frontend": "Um(a) Frontend cuida da interface e da experiência do usuário, construindo telas, componentes, acessibilidade, responsividade e integração com APIs.",
        "backend": "Um(a) Backend é responsável pela lógica do sistema, bancos de dados, APIs, regras de negócio, autenticação e manutenção da aplicação em produção.",
        "dados": "Um(a) profissional de dados coleta, organiza e analisa informações para apoiar decisões, usando SQL, dashboards, modelagem e estatística.",
        "ux/ui": "Um(a) UX/UI trabalha na experiência e no visual do produto, com pesquisas, wireframes, protótipos, usabilidade e design consistente.",
        "devops": "Um(a) DevOps automatiza deploys, infraestrutura, monitoramento, pipelines e garante que a aplicação rode com mais estabilidade e velocidade.",
        "qa": "Um(a) QA valida qualidade de software por testes, automação, análise de requisitos, detecção de falhas e garantia de que a entrega atende ao esperado.",
        "product manager": "Um(a) Product Manager conecta cliente, negócio e tecnologia, define prioridades, escopo, métricas e direciona a evolução do produto.",
        "analyst": "Um(a) analista de dados ou negócios interpreta dados e processos, identifica oportunidades, mede indicadores e apoia decisões estratégicas.",
        "full stack": "Um(a) Full Stack trabalha tanto no frontend quanto no backend, entregando soluções completas, desde interface até APIs e integrações.",
        "cybersecurity": "Um(a) profissional de cybersecurity protege sistemas, dados e redes, com monitoramento, testes de segurança, políticas e resposta a incidentes.",
        "ai engineer": "Um(a) AI Engineer desenvolve e aplica modelos de inteligência artificial, integra IA em produtos e cuida de dados, métricas e deploy de soluções.",
        "mobile": "Um(a) Mobile desenvolve aplicativos para Android ou iOS, cuida da experiência do usuário, integra APIs e garante desempenho e usabilidade no celular.",
        "cloud": "Um(a) Cloud Engineer cuida de infraestrutura em nuvem, deploy, escalabilidade, segurança, observabilidade e automação de ambientes de produção.",
        "machine learning": "Um(a) Machine Learning Engineer cria modelos preditivos, treina dados, valida métricas e integra soluções de IA em aplicações reais.",
        "data analyst": "Um(a) Data Analyst transforma dados em insights, monta relatórios, mede indicadores e orienta decisões com análises claras e objetivas.",
        "ux research": "Um(a) UX Research investiga o comportamento das pessoas, coleta feedback, analisa necessidades e orienta decisões de produto com evidência.",
    }

    if ("o que" in message_lower or "qual" in message_lower) and any(word in message_lower for word in ["faz", "fazem", "trabalha", "trabalham", "desempenha", "senior", "pleno", "junior"]):
        for keyword, answer in role_answers.items():
            if keyword in message_lower:
                return {"reply": answer}

    if any(word in message_lower for word in ["vaga", "job", "trabalho", "oportunidade"]):
        if profile:
            area = profile.area or "Backend"
            loc = profile.location or "Brasil"
            return {"reply": f"Você parece estar buscando oportunidades em {area}. No seu perfil, a localização atual é {loc}. Posso sugerir vagas em {area} com foco em {', '.join(profile.skills or ['Python', 'SQL'])}."}
        return {"reply": "Posso te ajudar a encontrar vagas. Primeiro, preencha seu perfil para eu sugerir áreas e oportunidades mais alinhadas ao seu perfil."}

    if any(word in message_lower for word in ["curso", "estudar", "aprendizado", "aprende", "treinar"]):
        if profile:
            area = profile.area or "Backend"
            return {"reply": f"Para fortalecer seu perfil em {area}, vale focar em cursos de Python, SQL, Git e comunicação. Posso sugerir trilhas de estudo mais específicas para o seu objetivo."}
        return {"reply": "Posso recomendar cursos de acordo com sua área. Me diga sua área de interesse e nível de experiência."}

    if any(word in message_lower for word in ["perfil", "sobre mim", "minha area", "sobre mim", "quem sou"]):
        if profile:
            return {"reply": f"Seu perfil mostra que você trabalha na área de {profile.area} e prefere {profile.work_mode}. Seu foco está em {', '.join(profile.skills or ['habilidades técnicas'])} e soft skills como {', '.join(profile.soft_skills or ['comunicação'])}."}
        return {"reply": "Ainda não tenho um perfil salvo. Preencha o formulário e salve seu perfil para receber um resumo personalizado."}

    if any(word in message_lower for word in ["tecnologia", "python", "sql", "fastapi", "docker", "frontend", "backend"]):
        return {"reply": "Uma boa rota de estudo é praticar projetos reais e combinar teoria com execução. Para seu caso, Python + SQL + Git + comunicação costuma transformar bastante o perfil."}

    return {"reply": "Entendi. Posso te ajudar com vagas, cursos, perfil profissional e objetivos de carreira. Me diga a sua área, o que você quer aprender ou em que tipo de oportunidade está buscando."}


@app.get("/")
def index():
    return FileResponse("static/index.html")


@app.get("/config.js")
def config_js():
    """Serves a small JavaScript file with runtime config coming from env vars.

    Deploys can set the `N8N_CHAT_URL` env var to point to the hosted n8n chat.
    """
    n8n = os.getenv(
        "N8N_CHAT_URL",
        "https://camillasilveira.app.n8n.cloud/webhook/c5d6507b-f421-4f5e-94a2-6541b24d2035/chat",
    )
    payload = {"N8N_CHAT_URL": n8n}
    js = "window.APP_CONFIG = " + json.dumps(payload) + ";"
    return Response(js, media_type="application/javascript")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
