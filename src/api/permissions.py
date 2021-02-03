from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Allow access only if the user is an admin
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        return False
