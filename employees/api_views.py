from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from employees.models import Employee
from employees.permissions import EmployeePermission

from .serializers import (
    EmployeeDetailSerializer,
    EmployeeListSerializer,
    EmployeeWriteSerializer,
)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related("workplace").prefetch_related(
        "images", "skills"
    )
    serializer_class = EmployeeWriteSerializer
    permission_classes = [EmployeePermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "skills__name": ["exact"],
        "hired_at": ["exact", "gte", "lte"],
    }
    ordering_fields = ["surname", "name", "hired_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        elif self.action == "retrieve":
            return EmployeeDetailSerializer
        return EmployeeWriteSerializer