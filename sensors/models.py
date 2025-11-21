from collections import defaultdict
from datetime import timedelta
import time
from django.db import models
from sensors.uuid7 import get_uuid7
import django.contrib.auth.models
import django.utils.timezone
import functools


@functools.lru_cache(maxsize=100)
def _get_device_name(owner, mac, time):
    try:
        device = Device.objects.get(owner=owner, mac=mac)
        return device.name
    except Device.DoesNotExist:
        return None


def get_device_name(owner, mac):
    return _get_device_name(owner, mac, time.time() // 5)


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

    @property
    def device_name(self):
        return get_device_name(self.owner, self.mac)

    class Meta:
        indexes = (models.Index(fields=("owner", "timestamp")),)


class User(django.contrib.auth.models.AbstractUser):
    id = models.UUIDField(primary_key=True, default=get_uuid7, editable=False)

    def latest_readings(self):
        devices = {device.mac: device for device in Device.objects.filter(owner=self)}
        macs = devices.keys()
        qs = (
            Reading.objects.filter(
                owner=self,
                mac__in=macs,
            )
            .annotate(
                latest_timestamp=models.Window(
                    expression=models.functions.FirstValue("timestamp"),
                    partition_by=["mac"],
                    order_by=models.F("timestamp").desc(),
                )
            )
            .filter(timestamp=models.F("latest_timestamp"))
        )
        latest = []
        for reading in qs:
            name = devices[reading.mac].name
            latest.append([name, reading])
        return latest

    def get_chart_data(self):
        devices = Device.objects.filter(owner=self)
        names = {d.mac: d.name for d in devices}
        readings = Reading.objects.filter(
            owner=self,
            mac__in=[d.mac for d in devices],
            timestamp__gt=django.utils.timezone.now() - timedelta(hours=24),
        ).order_by("-timestamp")
        datasets = defaultdict(list)
        hour = 60 * 60
        now = django.utils.timezone.now().timestamp() / hour
        for reading in readings:
            name = names[reading.mac]
            t = reading.timestamp.timestamp() / hour
            x = now - t
            datasets[name].append(dict(x=x, y=reading.temperature))
        data = {
            "datasets": [
                dict(data=data, showLine=True, label=label)
                for label, data in datasets.items()
            ],
        }
        return data


class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid7, editable=False)
    owner = models.ForeignKey(
        "sensors.User", related_name="devices", on_delete=models.CASCADE
    )
    mac = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
