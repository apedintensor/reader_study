# Reader Study Web Application Backend

## Overview

This is the backend for the Reader Study Web Application, a FastAPI-based service that provides authentication and data management for medical image studies.

## Features

- User authentication with fastapi-users (JWT-based)
- Role-based authorization system
- Async database operations with SQLAlchemy
- CRUD operations for all resources
- Secure password handling
- Centralized configuration

## Project Structure

```
backend/
  ├─ app/                   # Application package
  │   ├─ api/               # API endpoints 
  │   │   ├─ deps.py        # Dependency injection
  │   │   ├─ routes.py      # API route registration
  │   │   └─ endpoints/     # Individual API endpoint modules
  │   ├─ auth/              # Authentication system
  │   │   ├─ db.py          # User database integration
  │   │   ├─ manager.py     # User management
  │   │   ├─ models.py      # User model definition
  │   │   ├─ routes.py      # Auth routes
  │   │   └─ schemas.py     # Auth Pydantic schemas
  │   ├─ core/              # Core application components
  │   │   └─ config.py      # Configuration settings
  │   ├─ crud/              # CRUD operations for models
  │   ├─ db/                # Database configuration
  │   │   ├─ base.py        # Base model class
  │   │   ├─ init_db.py     # Database initialization
  │   │   └─ session.py     # Database session handling
  │   ├─ models/            # SQLAlchemy models
  │   ├─ schemas/           # Pydantic schemas
  │   └─ main.py            # Application entry point
  ├─ docs/                  # Documentation
  └─ requirements.txt       # Dependencies
```

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   SECRET_KEY=your-secret-key-at-least-32-chars
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Access the API documentation: http://localhost:8000/docs

## Authentication

The application uses JWT-based authentication provided by fastapi-users.

- Register: POST `/auth/register`
- Login: POST `/auth/jwt/login`
- Get current user: GET `/auth/me`

## Key Refactoring Changes

1. **Consolidated User Model**: Removed duplicate User model definitions and standardized on a single model in `app/auth/models.py`.

2. **Unified Database Sessions**: Added support for both synchronous and asynchronous database operations through a central session manager.

3. **Centralized Configuration**: Moved all configuration to `app/core/config.py`, including database URLs and security settings.

4. **Enhanced Security**: Implemented proper password hashing with passlib.

5. **Database Initialization**: Added database initialization script to create initial roles and admin user.