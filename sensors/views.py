import django.views

import structlog
import rest_framework.viewsets
import rest_framework.permissions


import sensors.serializers
import sensors.permissions
import sensors.models

logger = structlog.get_logger()


# Create your views here.
class Home(django.views.generic.TemplateView):
    template_name = "home.html"


class ReadingViewSet(rest_framework.viewsets.ModelViewSet):
    permission_classes = [
        rest_framework.permissions.IsAuthenticated,
        sensors.permissions.IsOwner,
    ]
    queryset = sensors.models.Reading.objects.none()
    serializer_class = sensors.serializers.ReadingSerializer

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return sensors.models.Reading.objects.filter(owner=user).order_by("-id")

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DeviceViewSet(rest_framework.viewsets.ModelViewSet):
    permission_classes = [
        rest_framework.permissions.IsAuthenticated,
        sensors.permissions.IsOwner,
    ]
    serializer_class = sensors.serializers.DeviceSerializer
    queryset = sensors.models.Device.objects.none()

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user
        return sensors.models.Device.objects.filter(owner=user).order_by("-id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
