# Local Environment Instructions

## 0) Prerequisites Check
```bash
docker --version
gcloud --version
```

## 1) Clone + Enter the Project
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd engineering-tech-task
```

## 2) Set Up Google ADC (One-Time)

Login for Application Default Credentials:
```bash
gcloud auth application-default login
```

Confirm the credentials file exists:
```bash
ls ~/.config/gcloud/application_default_credentials.json
```

Confirm your project is set:
```bash
gcloud config get-value project
```

Expected (for you): `brightos-tech-task`

## 3) Stop Any Leftover Containers (Avoid Port Issues)
```bash
docker stop $(docker ps -q)
```

Optional sanity check:
```bash
docker ps
```

(should be empty)

## 4) Build the Docker Image
```bash
docker build -t brightos-tech-task .
```

## 5) Run the Container (with API Key + Google Creds + Project)
```bash
docker run --rm -p 8082:8080 \
  -e API_KEY=dev-key \
  -e GOOGLE_CLOUD_PROJECT=brightos-tech-task \
  -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/adc.json \
  -v ~/.config/gcloud/application_default_credentials.json:/tmp/adc.json:ro \
  brightos-tech-task
```

Leave this terminal running.

## 6) Verify Deployment

Open the API documentation in a browser:
* `http://localhost:8082/docs`

## 7) Test the API (In New Terminal)

### Feature 1: User Data Ingestion (POST)
```bash
curl -sS -X POST "http://localhost:8082/users/test-user/health-data" \
  -H "Content-Type: application/json" \
  -H "x-api-key: dev-key" \
  -d '{"timestamp":"2026-01-16T00:00:00Z","steps":1234,"calories":56.7,"sleepHours":7.5}'
```

Expected result:
```json
{ "status": "ok", "id": "..." }
```

### Feature 2: User Data Retrieval (GET)
```bash
curl -sS "http://localhost:8082/users/test-user/health-data?start=15-01-2026&end=16-01-2026" \
  -H "x-api-key: dev-key"
```

### Feature 3: Basic Aggregation (GET)
```bash
curl -sS "http://localhost:8082/users/test-user/summary?start=15-01-2026&end=16-01-2026" \
  -H "x-api-key: dev-key"
```

## 8) Stop the Service

Go back to the Docker terminal and press:
```
Ctrl + C
```

---

# Cloud Run Environment Instructions

## 0) Prerequisites Check

* Google Cloud SDK (`gcloud`) installed
* Logged in to Google Cloud
* A Google Cloud project selected
* Firestore enabled in the project

## 1) Set Up Google Cloud Authentication
```bash
gcloud auth login
gcloud config set project brightos-tech-task
```

Verify project:
```bash
gcloud config get-value project
```

## 2) Safeguard Check

(Optional) Confirm the Cloud Run service exists (or see existing services):
```bash
gcloud run services list --region australia-southeast1
```

## 3) Build & Deploy to Cloud Run

Build the container and deploy directly to Cloud Run from source:
```bash
gcloud run deploy brightos-tech-task \
  --source . \
  --region australia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars API_KEY=dev-key,GOOGLE_CLOUD_PROJECT=brightos-tech-task
```

## 4) Verify Deployment

Fetch the deployed service URL:
```bash
URL=$(gcloud run services describe brightos-tech-task --region australia-southeast1 --format="value(status.url)")
echo "$URL"
```

Open the API documentation in a browser:
```bash
echo "$URL/docs"
```

## 5) Test the API

### Feature 1: User Data Ingestion (POST)
```bash
URL=$(gcloud run services describe brightos-tech-task --region australia-southeast1 --format="value(status.url)")
curl -i -X POST "$URL/users/test-user/health-data" \
  -H "Content-Type: application/json" \
  -H "x-api-key: dev-key" \
  -d '{"timestamp":"2026-01-16T00:00:00Z","steps":1234,"calories":56.7,"sleepHours":7.5}'
```

Expected result:
```json
{ "status": "ok", "id": "..." }
```

### Feature 2: User Data Retrieval (GET)
```bash
URL=$(gcloud run services describe brightos-tech-task --region australia-southeast1 --format="value(status.url)")
curl "$URL/users/test-user/health-data?start=15-01-2026&end=16-01-2026" \
  -H "x-api-key: dev-key"
```

### Feature 3: Basic Aggregation (GET)
```bash
URL=$(gcloud run services describe brightos-tech-task --region australia-southeast1 --format="value(status.url)")
curl "$URL/users/test-user/summary?start=15-01-2026&end=16-01-2026" \
  -H "x-api-key: dev-key"
```