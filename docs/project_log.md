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
*   Implemented authentication system using fastapi-users (`app/auth/`).
*   Created User model that extends fastapi-users' BaseUserTable with additional fields.
*   Added JWT-based authentication with configurable token lifetime.
*   Set up authentication endpoints for registration, login, and profile management.
*   Added role support for user authentication.
*   Created dependency functions for accessing the current authenticated user.
*   Transitioned to asynchronous SQLite database access for authentication.
*   Updated FastAPI app to initialize database tables asynchronously on startup.
*   Fixed dependency issues by adding `pydantic-settings>=2.0.0` to project dependencies.
*   Resolved CRUD operation access in `init_db.py` by updating from dot notation to dictionary access.
*   Fixed user creation in database initialization by directly instantiating SQLAlchemy user database and UserManager.
*   Created database recreation script (`recreate_db.py`) to resolve schema issues with missing columns.
*   Added root endpoint ("/") to provide API information and documentation links.
*   Added admin endpoint ("/admin") that currently redirects to API documentation for future expansion.
*   Successfully validated application startup with all core functionality working properly.
*   Implemented centralized error handling:
    *   Defined custom exception classes: `EntityNotFoundException`, `PermissionDeniedException`, `DuplicateEntryException`, `GenericServerError` in `app/core/exceptions.py`.
    *   Added exception handlers for each, plus handlers for `RequestValidationError` and `HTTPException`, returning structured JSON error responses.
    *   Registered all handlers globally in `main.py`.
    *   Added logging for 500 and unexpected errors.
    *   Provided reusable helper functions for raising HTTP exceptions.
