import django.views
import django.http
import django.db
import django.conf
import json
import io

import structlog
import rest_framework.filters
import rest_framework.viewsets
import rest_framework.permissions
from django.contrib.auth.mixins import LoginRequiredMixin
import polars as pl

import sensors.serializers
import sensors.permissions
import sensors.models
from . import filters

logger = structlog.get_logger()


# Create your views here.
class Home(LoginRequiredMixin, django.views.generic.TemplateView):
    template_name = "home.html"

    # def get_context_data(self, *args, **kwargs):
    #     context = super().get_context_data(*args, **kwargs)
    #     user: sensors.models.User = self.request.user
    #     if user.is_authenticated:
    #         context["latest_readings"] = user.latest_readings()
    #     return context


class ReadingViewSet(rest_framework.viewsets.ModelViewSet):
    permission_classes = [
        rest_framework.permissions.IsAuthenticated,
        sensors.permissions.IsOwner,
    ]
    queryset = sensors.models.Reading.objects.none()
    serializer_class = sensors.serializers.ReadingSerializer
    filterset_class = filters.Reading
    ordering_fields = ["timestamp"]

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


class Chart(LoginRequiredMixin, django.views.generic.TemplateView):
    template_name = "chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.user.get_chart_data()
        encoded = json.dumps(data, indent=2)
        context["data"] = encoded
        return context


class Test(django.views.generic.TemplateView):
    template_name = "test.html"


class DownloadParquet(LoginRequiredMixin, django.views.View):
    def get(self, request, *args, **kwargs):
        logger.info("DownloadParquet", args=args, kwargs=kwargs)
        owner_id = request.user.id.hex

        database_filename = django.conf.settings.DATABASES["default"]["NAME"]
        uri = f"sqlite://{database_filename}"
        query = f"SELECT * FROM sensors_reading WHERE owner_id = '{owner_id}'"
        df = pl.read_database_uri(
            query=query,
            uri=uri,
            schema_overrides={
                "timestamp": pl.Datetime(time_zone="NZ"),
            },
        )

        logger.info(
            "dataframe created",
            estimated_size_mb=str(df.estimated_size("mb")),
            owner_id=owner_id,
        )

        parquet_file = io.BytesIO()
        df.write_parquet(parquet_file)
        parquet_file.seek(0)
        return django.http.FileResponse(
            parquet_file, as_attachment=True, filename="readings.parquet"
        )
