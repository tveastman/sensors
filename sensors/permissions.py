import rest_framework


class IsOwner(rest_framework.permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
