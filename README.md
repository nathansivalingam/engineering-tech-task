# Bright OS – Health Data API

## Setup Instructions

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
gcloud auth application-default login
gcloud config set project <YOUR_PROJECT_ID>
```

```bash
export API_KEY=dev-key
```

```bash
python -m uvicorn main:app --reload
```

---

## Deployment Instructions for Cloud Run

```bash
docker build -t brightos-tech-task .
```

```bash
docker run --rm -p 8080:8080 -e API_KEY=dev-key brightos-tech-task
```

```bash
gcloud builds submit --tag gcr.io/<PROJECT_ID>/health-api
```

```bash
gcloud run deploy health-api --image gcr.io/<PROJECT_ID>/health-api
```

---

## Example API Requests

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

```json
{ "status": "ok" }
```

---

### Add Health Data

```bash
curl -X POST "http://127.0.0.1:8000/users/u1/health-data" \
  -H "X-API-Key: dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-01-08T08:30:00Z",
    "steps": 1200,
    "calories": 450,
    "sleepHours": 7.5
  }'
```

---

### Get Health Data

```bash
curl -H "X-API-Key: dev-key" \
"http://127.0.0.1:8000/users/u1/health-data?start=08-01-2026&end=10-01-2026"
```

---

### Get Summary

```bash
curl -H "X-API-Key: dev-key" \
"http://127.0.0.1:8000/users/u1/summary?start=08-01-2026&end=10-01-2026"
```

```json
{
  "totalSteps": 9200,
  "averageCalories": 583.33,
  "averageSleepHours": 7.17,
  "count": 3
}
```

---

## Limitations

```text
Cloud Run deployment requires a billing-enabled Google Cloud project.
Caching, rate limiting, and automated tests are not implemented.
```
