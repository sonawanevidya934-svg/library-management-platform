import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_home_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["status"] == "running"


def test_healthcheck_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    assert "Student Record" in data["service"]


def test_list_courses(client):
    response = client.get("/api/courses")
    assert response.status_code == 200
    assert response.get_json()["count"] >= 5


def test_register_student_endpoint(client):
    payload = {"student_id": "S500", "name": "Test User",
               "email": "test@university.edu", "semester": 2}
    response = client.post("/api/students", json=payload)
    assert response.status_code == 201
    assert client.get("/api/students/S500").status_code == 200


def test_student_not_found(client):
    assert client.get("/api/students/NOPE").status_code == 404


def test_enroll_marks_and_gpa_flow(client):
    assert client.post("/api/enroll", json={"student_id": "S101", "course_id": "C301"}
                       ).status_code == 200
    assert client.post("/api/marks", json={"student_id": "S101", "course_id": "C301",
                                           "marks": 90}).status_code == 200
    gpa = client.get("/api/students/S101/gpa").get_json()
    assert gpa["gpa"] == 10.0


def test_enroll_conflict_returns_400(client):
    client.post("/api/enroll", json={"student_id": "S101", "course_id": "C301"})
    response = client.post("/api/enroll", json={"student_id": "S101", "course_id": "C303"})
    assert response.status_code == 400
    assert "Schedule conflict" in response.get_json()["error"]
