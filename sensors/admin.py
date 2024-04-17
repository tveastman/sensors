from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
import sensors.models


# Register your models here.
class SensorsUserAdmin(UserAdmin):
    pass


admin.site.register(sensors.models.User, SensorsUserAdmin)


@admin.register(sensors.models.Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "owner",
        "type",
        "mac",
        "temperature",
        "humidity",
        "battery",
        "rssi",
    )
    list_filter = ("owner", "mac")
    date_hierarchy = "timestamp"


@admin.register(sensors.models.Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "owner",
        "mac",
        "name",
    )
    list_filter = ("owner",)
