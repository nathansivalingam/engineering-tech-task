## Instructions (Local Environment)

### Build
docker build -t brightos-tech-task .

### Deploy
docker run --rm -p 8082:8080 -e API_KEY=dev-key brightos-tech-task

Select: http://localhost:8082/docs

### Test

#### Feature 1: User Data Ingestion (POST)
curl -X POST "http://localhost:8082/users/test-user/health-data" \
  -H "Content-Type: application/json" \
  -H "x-api-key: dev-key" \
  -d '{"timestamp":"2026-01-16T00:00:00Z","steps":1234,"calories":56.7,"sleepHours":7.5}'

#### Feature 2: User Data Retrieval (GET)
curl "http://localhost:8082/users/test-user/health-data?start=15-01-2026&end=16-01-2026" \
  -H "x-api-key: dev-key"

#### Feature 3: Basic Aggregation (GET)
curl "http://localhost:8082/users/test-user/summary?start=15-01-2026&end=16-01-2026" \
  -H "x-api-key: dev-key"


## Instructions (Cloud Run Environment)

### Deploy
gcloud run deploy brightos-tech-task \
  --source . \
  --allow-unauthenticated \
  --set-env-vars API_KEY=dev-key \
  --region australia-southeast1

### Test

#### Feature 1: User Data Ingestion (POST)
curl -X POST "https://brightos-tech-task-50151081562.australia-southeast1.run.app/users/test-user/health-data" \
  -H "Content-Type: application/json" \
  -H "x-api-key: dev-key" \
  -d '{"timestamp":"2026-01-16T00:00:00Z","steps":1234,"calories":56.7,"sleepHours":7.5}'

#### Feature 2: User Data Retrieval (GET)
curl "https://brightos-tech-task-50151081562.australia-southeast1.run.app/users/test-user/health-data?start=15-01-2026&end=16-01-2026" \
  -H "x-api-key: dev-key"

#### Feature 3: Basic Aggregation (GET)
curl "https://brightos-tech-task-50151081562.australia-southeast1.run.app/users/test-user/summary?start=15-01-2026&end=16-01-2026" \
  -H "x-api-key: dev-key"
