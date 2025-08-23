
import django_filters
from .models import Project


class ProjectFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    project_type = django_filters.CharFilter(field_name="project_type", lookup_expr="iexact")
    owner = django_filters.NumberFilter(field_name="owner_id")

    class Meta:
        model = Project
        fields = ["status", "project_type", "owner"]
