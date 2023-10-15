from django.contrib.auth.mixins import AccessMixin
from django.http.response import HttpResponseRedirect
from django.urls import reverse

class UserIsOwnerMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.created_by != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class UnauthenticatedUserMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(reverse('index'))


class UserHasRoleMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.groups.filter(name__in=self.allowed_roles).exists():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        return HttpResponseRedirect(reverse('index'))
