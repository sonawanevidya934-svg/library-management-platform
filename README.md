<<<<<<< HEAD
# Enterprise Student Record & Academic Management Platform

Python 3.11 / Flask REST API with Pytest, Flake8, Jenkins CI, Docker and Kubernetes (Minikube).

## Business rules
- A student can enrol in at most **18 credits per semester**
- No two active courses of one student may share a timetable slot (conflict check)
- Course capacity is enforced; duplicate enrolments are rejected
- Marks are 0-100 and map to a 10-point grade scale; **GPA is credit-weighted**

## API (prefix `/api`)
| Method | Path | Purpose |
| --- | --- | --- |
| GET | /health | Liveness / readiness probe |
| GET, POST | /students | List / register students |
| GET | /students/<id> | Student details |
| GET | /students/<id>/gpa | Credit-weighted GPA |
| GET, POST | /courses | List (`?q=`) / add courses |
| POST | /enroll | Enrol a student in a course |
| POST | /drop | Drop a course |
| POST | /marks | Record marks for an enrolled course |

## Run locally
```bash
python3 -m venv venv && source venv/bin/activate   # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py                                       # http://localhost:5000
pytest -v --cov=app --cov=database tests/
flake8 app database tests run.py
```

## Docker
```bash
docker build -t student-academic-platform:v1.0.0 .
docker run -d -p 5000:5000 --name student-container student-academic-platform:v1.0.0
curl http://localhost:5000/api/health
```

## Kubernetes (Minikube)
```bash
minikube image load student-academic-platform:v1.0.0
kubectl apply -f k8s/
kubectl get pods -l app=student-platform
```
=======
# student-academic-platform
>>>>>>> 34ca389efbf5c81011fd4eb17a3424c18a904dc1
