from .permissions import IsAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated, DjangoModelPermissions

ADMIN_PERMISSIONS = [
    IsAuthenticated,
    IsAdmin
]

STANDARD_PERMISSIONS = [
    IsAuthenticated,
    DjangoModelPermissions
]

CONSUMER_PERMISSIONS = [
    IsAuthenticated
]

UNPROTECTED = [
    AllowAny
]