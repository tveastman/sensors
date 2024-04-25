import django_filters
from . import models


class Reading(django_filters.FilterSet):
    timestamp__gt = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="gt"
    )
    timestamp__lt = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="lt"
    )

    class Meta:
        model = models.Reading
        exclude = ["owner"]
        fields = ["mac"]
