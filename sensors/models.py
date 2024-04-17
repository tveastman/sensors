from django.db import models
from sensors.uuid7 import get_uuid7
import django.contrib.auth.models


class Reading(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid7, editable=False)
    owner = models.ForeignKey(
        "sensors.User", related_name="readings", on_delete=models.CASCADE
    )
    gatewayFree = models.FloatField(null=True, blank=True)
    gatewayLoad = models.FloatField(null=True, blank=True)
    mac = models.CharField(max_length=20)
    timestamp = models.DateTimeField()
    type = models.CharField(max_length=20)
    bleName = models.CharField(max_length=20, null=True, blank=True)
    battery = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    rssi = models.FloatField(null=True, blank=True)


class User(django.contrib.auth.models.AbstractUser):
    id = models.UUIDField(primary_key=True, default=get_uuid7, editable=False)


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid7, editable=False)
    owner = models.ForeignKey(
        "sensors.User", related_name="devices", on_delete=models.CASCADE
    )
    mac = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
