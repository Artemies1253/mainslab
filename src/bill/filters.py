from django_filters import rest_framework as filters


class BillListFilter(filters.FilterSet):
    org_name = filters.CharFilter(field_name="organization__name", lookup_expr="iexact")
    client_name = filters.CharFilter(field_name="client__name", lookup_expr="iexact")
