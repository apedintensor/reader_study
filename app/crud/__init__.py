# backend/app/crud/__init__.py
from .crud_user import user
from .crud_role import role
from .crud_case import case
from .crud_assessment import assessment
from .crud_diagnosis import diagnosis
from .crud_management_plan import management_plan
from .crud_ai_output import ai_output
from .crud_diagnosis_term import diagnosis_term
from .crud_management_strategy import management_strategy
from .crud_image import image
from .crud_case_metadata import case_metadata

# Import other crud objects as they are created
# ... and so on
