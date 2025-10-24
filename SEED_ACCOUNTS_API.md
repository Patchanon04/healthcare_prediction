# Seed Accounts API

## 📋 Overview
API endpoint to seed database with test accounts for development and testing.

## 🔗 Endpoint
```
POST /api/v1/seed-accounts/
```

## 🔓 Authentication
No authentication required (AllowAny)

---

## 📤 Request

### Headers
```
Content-Type: application/json
```

### Body (Optional)
```json
{
  "reset": true
}
```

**Parameters:**
- `reset` (boolean, optional): If `true`, deletes existing test accounts before creating new ones. Default: `false`

---

## 📥 Response

### Success Response (201 Created or 200 OK)
```json
{
  "success": true,
  "created": 4,
  "skipped": 0,
  "accounts": [
    {
      "username": "doctor1",
      "role": "doctor",
      "email": "doctor1@hospital.com"
    },
    {
      "username": "nurse1",
      "role": "nurse",
      "email": "nurse1@hospital.com"
    },
    {
      "username": "admin1",
      "role": "admin",
      "email": "admin1@hospital.com"
    },
    {
      "username": "radiologist1",
      "role": "radiologist",
      "email": "radiologist1@hospital.com"
    }
  ],
  "skipped_usernames": [],
  "message": "Created 4 accounts, skipped 0 existing accounts"
}
```

### Response When Accounts Already Exist (200 OK)
```json
{
  "success": true,
  "created": 0,
  "skipped": 4,
  "accounts": [],
  "skipped_usernames": ["doctor1", "nurse1", "admin1", "radiologist1"],
  "message": "Created 0 accounts, skipped 4 existing accounts"
}
```

---

## 👥 Test Accounts Created

| Username | Password | Email | Role | Contact |
|----------|----------|-------|------|---------|
| doctor1 | password123 | doctor1@hospital.com | doctor | 081-234-5678 |
| nurse1 | password123 | nurse1@hospital.com | nurse | 082-345-6789 |
| admin1 | password123 | admin1@hospital.com | admin | 083-456-7890 |
| radiologist1 | password123 | radiologist1@hospital.com | radiologist | 084-567-8901 |

---

## 🧪 Postman Examples

### Example 1: Create Accounts (First Time)
```
POST http://localhost:8000/api/v1/seed-accounts/
Content-Type: application/json

{}
```

### Example 2: Reset and Create Accounts
```
POST http://localhost:8000/api/v1/seed-accounts/
Content-Type: application/json

{
  "reset": true
}
```

### Example 3: Production URL
```
POST http://54.179.8.155/api/v1/seed-accounts/
Content-Type: application/json

{}
```

---

## 📝 Postman Collection

### Import this JSON into Postman:

```json
{
  "info": {
    "name": "Medical Diagnosis System - Seed Accounts",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Seed Accounts (Create)",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{}"
        },
        "url": {
          "raw": "{{base_url}}/api/v1/seed-accounts/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "seed-accounts", ""]
        }
      }
    },
    {
      "name": "Seed Accounts (Reset)",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"reset\": true\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/v1/seed-accounts/",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "seed-accounts", ""]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

---

## 🚀 Usage

### Using cURL
```bash
# Create accounts
curl -X POST http://localhost:8000/api/v1/seed-accounts/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Reset and create accounts
curl -X POST http://localhost:8000/api/v1/seed-accounts/ \
  -H "Content-Type: application/json" \
  -d '{"reset": true}'
```

### Using Python requests
```python
import requests

# Create accounts
response = requests.post('http://localhost:8000/api/v1/seed-accounts/')
print(response.json())

# Reset and create accounts
response = requests.post(
    'http://localhost:8000/api/v1/seed-accounts/',
    json={'reset': True}
)
print(response.json())
```

---

## ⚠️ Notes

1. **Development Only**: This endpoint should be disabled in production or protected with admin authentication
2. **Password Security**: All test accounts use the same password (`password123`) for convenience
3. **Idempotent**: Running without `reset=true` will skip existing accounts
4. **User Profiles**: Each account automatically gets a UserProfile created with full_name, contact, and role

---

## 🔐 Login After Seeding

After seeding accounts, you can login using:

```
POST /api/v1/auth/login/
Content-Type: application/json

{
  "username": "doctor1",
  "password": "password123"
}
```

Response:
```json
{
  "token": "abc123...",
  "username": "doctor1",
  "email": "doctor1@hospital.com"
}
```

Use the token for authenticated requests:
```
Authorization: Token abc123...
```
