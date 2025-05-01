# Project Log

## 2025-05-01

*   Initialized project structure with FastAPI.
*   Defined initial database schema using DBML (`docs/db.dbml`).
*   Outlined backend design, auth strategy, routes, schemas, and security plan (`docs/backend-design.md`).
*   Created SQLAlchemy models based on DBML (`app/models/models.py`).
*   Created Pydantic schemas for API request/response validation (`app/schemas/schemas.py`).
*   Implemented initial CRUD operations for User, Role, and Case models (`app/crud/`).
*   Implemented CRUD operations for Assessment, Diagnosis, ManagementPlan, AIOutput, DiagnosisTerm, ManagementStrategy, Image, and CaseMetaData models (`app/crud/`).

## 2025-05-02

*   Created FastAPI API endpoint files for all entities (`app/api/endpoints/`).
*   Created database session dependency (`app/api/deps.py`).
*   Updated main API router (`app/api/routes.py`) to include all endpoint routers.

## 2025-05-03

*   Implemented authentication system using fastapi-users (`app/auth/`).
*   Created User model that extends fastapi-users' BaseUserTable with additional fields.
*   Added JWT-based authentication with configurable token lifetime.
*   Set up authentication endpoints for registration, login, and profile management.
*   Added role support for user authentication.
*   Created dependency functions for accessing the current authenticated user.
*   Transitioned to asynchronous SQLite database access for authentication.
*   Updated FastAPI app to initialize database tables asynchronously on startup.
