# API Integration Data Processing Assessment
A production-ready Django REST Framework API for classifying names by gender using the external Genderize API.

## Setup & Installation
1. Create venv: `python -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run Development Server: `python manage.py runserver`

## Execute Unit Tests
Run locally: `python manage.py test api`

## Endpoint Definition
**`GET /api/classify?name={name}`**

Resolves input against Genderize.io downstream.

### Example response
```json
{
  "status": "success",
  "data": {
    "name": "john",
    "gender": "male",
    "probability": 0.99,
    "sample_size": 1234,
    "is_confident": true,
    "processed_at": "2026-04-12T12:00:00Z"
  }
}
```
