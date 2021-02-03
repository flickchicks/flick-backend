from rest_framework.permissions import AllowAny
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.permissions import IsAuthenticated

from .permissions import IsAdmin

ADMIN_PERMISSIONS = [IsAuthenticated, IsAdmin]

STANDARD_PERMISSIONS = [IsAuthenticated, DjangoModelPermissions]

CONSUMER_PERMISSIONS = [IsAuthenticated]

UNPROTECTED = [AllowAny]
