# Import key components to make them accessible from the auth package
from app.auth.models import User
from app.auth.manager import current_active_user, current_superuser