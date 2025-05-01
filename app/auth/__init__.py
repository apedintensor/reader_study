# Import key components to make them accessible from the auth package
# Import the unified User model
from app.models.models import User
from app.auth.manager import current_active_user, current_superuser