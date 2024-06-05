from django_filters import FilterSet, filters
from .models import User


class UserSearchFilter(FilterSet):
    search = filters.CharFilter(method="filter_by_all_fields")
    class Meta:
        model = User
        fields = []

    def filter_by_all_fields(self, queryset, name, value):
        return queryset.filter(
            filters.Q(email=value)
            | filters.Q(first_name__icontains=value)
            | filters.Q(last_name__icontains=value)
        )