# Pi Course - Backend API
A Django REST Framework API for a tutoring platform where students can find tutors and create lesson requests.

## Features

User authentication with JWT tokens
Role-based permissions (student/tutor)
Tutor discovery with filtering and search
Lesson request management
OpenAPI documentation with Swagger UI

# Quick Start
## Prerequisites

Python 3.11+
pip
Virtual environment (recommended)

## Installation

Clone the repository

```bash
git clone https://github.com/ayselbbzd/picourse.git
cd picourse-backend
```

## Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Install dependencies

```bash
make install
or
pip install -r requirements.txt
```

## Run migrations

```bash
make migrate
or
python manage.py makemigrations
python manage.py migrate
```

## Load seed data

```bash
make seed
or
python manage.py seed_data
```

## Run the development server

```bash
make run
or
python manage.py runserver
```
The API will be available at http://localhost:8000/

## Docker Setup (Optional)

```bash
# Build and start containers
make docker-up
# or
docker-compose up -d

# Stop containers
make docker-down
# or
docker-compose down
```

## Demo Accounts
After running seed data, you can use these demo accounts:

```
Students:
Email: student@demo.com / Password: DemoPass123!
Email: student2@demo.com / Password: DemoPass123!
```

```
Tutors:
Email: tutor@demo.com / Password: DemoPass123!
Email: tutor2@demo.com / Password: DemoPass123!
```

## API Documentation
Visit http://localhost:8000/api/docs/ for interactive Swagger UI documentation.

## Key Endpoints

**Authentication**

POST /api/auth/register/ - User registration
POST /api/auth/login/ - User login (get JWT tokens)
POST /api/auth/refresh/ - Refresh access token

**User Profile**

GET /api/me/ - Get current user profile
PATCH /api/me/ - Update current user profile

**Tutors & Subjects**

GET /api/subjects/ - List all subjects
GET /api/tutors/ - List tutors (with filtering)
GET /api/tutors/{id}/ - Get tutor details

**Lesson Requests**

POST /api/lesson-requests/ - Create lesson request (students only)
GET /api/lesson-requests/ - List lesson requests
PATCH /api/lesson-requests/{id}/ - Update lesson request status (tutors only)


## API Examples
Register a new student
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "role": "student",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@demo.com",
    "password": "DemoPass123!"
  }'
```

Get tutors with filtering
```bash
curl -X GET "http://localhost:8000/api/tutors/?subject=1&ordering=-rating&search=physics"
Create lesson request
bashcurl -X POST http://localhost:8000/api/lesson-requests/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "tutor_id": 1,
    "subject_id": 1,
    "start_time": "2025-08-25T10:00:00Z",
    "duration_minutes": 60,
    "note": "Need help with calculus"
  }'
```

## Testing
Run the test suite:
```bash
make test
or
python manage.py test
```

# Architecture Notes
## Design Decisions

1. Role-Based Access Control: Implemented using Django's built-in user model with a role field. Profiles are automatically created based on user role during registration.
2. JWT Authentication: Used djangorestframework-simplejwt for stateless authentication, suitable for mobile apps.
3. API Design: RESTful API design following DRF conventions. Used class-based views for CRUD operations and function-based views for simple endpoints.
4. Database Relations:
- OneToOne relationships for user profiles
- ManyToMany relationship between tutors and subjects
- ForeignKey relationships for lesson requests

5. Filtering & Search: Implemented using DRF's built-in filtering with query parameters for flexible tutor discovery.
6. Permissions: Custom permission logic in views rather than separate permission classes for simplicity in this MVP.

## Security Features

JWT token authentication
Password validation
Role-based permissions
Input validation and sanitization
CORS configuration for frontend integration

## Performance Optimizations

select_related() and prefetch_related() to prevent N+1 queries
Database indexes on frequently queried fields
Pagination for list endpoints

## API Rate Limiting
Currently not implemented but can be easily added using DRF's throttling classes or django-ratelimit for production use.
