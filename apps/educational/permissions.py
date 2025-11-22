from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

class EditorRequiredMixin(LoginRequiredMixin):
    """Mixin que restringe acceso a usuarios con rol editor o admin."""
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        if not (getattr(user, 'is_editor', False) or getattr(user, 'is_admin_role', False)):
            raise PermissionDenied('No tienes permisos para realizar esta acción.')
        return super().dispatch(request, *args, **kwargs)
