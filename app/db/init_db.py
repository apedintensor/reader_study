# backend/app/db/init_db.py
import asyncio
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.auth.models import User
from app.core.config import settings
from app.db.session import async_engine, sync_engine
from app.db.base import Base
from app.models.models import Role
from app.crud.crud_role import role as role_crud
from app.auth.schemas import UserCreate
from app.auth.manager import UserManager
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase


# Create initial superuser account
async def create_initial_superuser(db: AsyncSession):
    """Create an initial superuser if none exists"""
    try:
        # Create a SQLAlchemyUserDatabase instance directly
        user_db = SQLAlchemyUserDatabase(db, User)
        
        # Create UserManager instance directly instead of using the dependency
        user_manager = UserManager(user_db)
        
        # Create superuser
        superuser_data = UserCreate(
            email=settings.SUPERUSER_EMAIL,
            password=settings.SUPERUSER_PASSWORD,
            is_superuser=True,
            is_active=True,
            is_verified=True,
            role_id=1,  # Admin role ID
        )
        
        try:
            await user_manager.create(superuser_data)
            print("Superuser created successfully")
        except UserAlreadyExists:
            print("Superuser already exists")
    except Exception as e:
        print(f"Error creating superuser: {e}")


# Create initial roles
def create_initial_roles(db: Session):
    """Create initial roles if they don't exist"""
    initial_roles = [
        {"name": "Admin"},
        {"name": "Doctor"},
        {"name": "Researcher"}
    ]
    
    for role_data in initial_roles:
        role = role_crud.get_by_name(db=db, name=role_data["name"])
        if not role:
            from app.schemas.schemas import RoleCreate
            role_create = RoleCreate(name=role_data["name"])
            role = role_crud.create(db=db, role=role_create)
            print(f"Role '{role_data['name']}' created")
        else:
            print(f"Role '{role_data['name']}' already exists")


# Initialize the database with required data
async def init_db():
    """Initialize the database with required data"""
    # Create tables if they don't exist
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
      # Create initial data using sync session for compatibility with existing CRUD
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        # Create initial roles
        create_initial_roles(db)
        
        # Close sync session
        db.close()
        
        # Create superuser using async session
        async with AsyncSession(async_engine) as async_session:
            await create_initial_superuser(async_session)
            
        print("Database initialization completed")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        
        
# Run the initialization directly if script is executed
if __name__ == "__main__":
    asyncio.run(init_db())