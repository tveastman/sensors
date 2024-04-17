import rest_framework.serializers

import sensors.models


class ReadingSerializer(rest_framework.serializers.HyperlinkedModelSerializer):
    class Meta:
        model = sensors.models.Reading
        exclude = ["owner"]


class DeviceSerializer(rest_framework.serializers.HyperlinkedModelSerializer):
    class Meta:
        model = sensors.models.Device
        exclude = ["owner"]
