from fastapi.testclient import TestClient

from main import app


def test_profiles_crud_flow():
    payload = {
        "user_name": "Maria",
        "area": "Backend",
        "experience": "Pleno",
        "work_mode": "Remoto",
        "location": "São Paulo - SP",
        "soft_skills": ["comunicação", "liderança"],
        "career_goal": "Crescimento técnico",
        "skills": ["Python", "SQL"],
        "target_roles": ["Backend Engineer", "Python Developer"],
    }

    with TestClient(app) as client:
        create_response = client.post("/profiles", json=payload)
        assert create_response.status_code == 200, create_response.text
        data = create_response.json()
        assert data["user_name"] == "Maria"
        assert data["area"] == "Backend"

        list_response = client.get("/profiles")
        assert list_response.status_code == 200
        assert len(list_response.json()) >= 1

        profile_id = data["id"]
        get_response = client.get(f"/profiles/{profile_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == profile_id


def test_recommendations_from_profile():
    payload = {
        "user_name": "Maria",
        "area": "Backend",
        "experience": "Pleno",
        "work_mode": "Remoto",
        "location": "São Paulo - SP",
        "soft_skills": ["comunicação", "liderança"],
        "career_goal": "Crescimento técnico",
        "skills": ["Python", "SQL"],
        "target_roles": ["Backend Engineer", "Python Developer"],
    }

    with TestClient(app) as client:
        client.post("/profiles", json=payload)
        response = client.get("/recommendations")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "courses" in data
        assert len(data["jobs"]) >= 1
        assert len(data["courses"]) >= 1


def test_chat_role_question():
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "o que um senior php faz?"})
        assert response.status_code == 200
        body = response.json()
        assert "PHP" in body["reply"]
        assert "arquitetura" in body["reply"].lower()
