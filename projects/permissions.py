
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerForUnsafe(BasePermission):
    """
    Owner-only for unsafe methods (PUT, PATCH, DELETE).
    Read:
      - owners and staff can read everything
      - others can read only ACTIVE projects (enforced in view)
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if request.user.is_staff or obj.owner_id == getattr(request.user, "id", None):
                return True
            # non-owner/non-staff: allowed read only if ACTIVE (checked in the view's get_object)
            return True
        return obj.owner_id == getattr(request.user, "id", None) or getattr(request.user, "is_staff", False)
