# Auth Service

The Auth Service is responsible for user authentication and authorization in the Aura platform. It provides APIs for managing user accounts, user profiles, and authentication tokens.

## Features

- User registration and authentication
- JWT token generation and validation
- User profile management
- Role-based access control
- Password reset flow (placeholder implementation)

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login with email and password
- `POST /api/v1/auth/login/form` - Login with form data (OAuth2 compatible)
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/logout` - Logout (revoke token)
- `POST /api/v1/auth/password-reset/request` - Request a password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm a password reset
- `GET /api/v1/auth/me` - Get current user information

### User Management

- `GET /api/v1/users` - List users (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)
- `GET /api/v1/users/{user_id}/profile` - Get user profile
- `POST /api/v1/users/{user_id}/profile` - Create user profile
- `PUT /api/v1/users/{user_id}/profile` - Update user profile

## Local Development

### Prerequisites

- Python 3.10+
- PostgreSQL 14+

### Setup

1. Install dependencies:

```bash
pip install poetry
poetry install
```

2. Set up environment variables:

```bash
cp ../../.env.example .env
# Edit .env with your configuration
```

3. Run the service:

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload
```

4. Access the API documentation:

```
http://localhost:8007/docs
```

## Docker

```bash
docker build -t aura/auth-service .
docker run -p 8007:8007 --env-file .env aura/auth-service
```

## Testing

```bash
poetry run pytest
``` 