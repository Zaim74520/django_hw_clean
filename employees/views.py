from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

from .models import Employee

EMPLOYEES_PER_PAGE = 10


def index(request):
    total = Employee.objects.count()
    employees = (
        Employee.objects.select_related("workplace")
        .prefetch_related("images", "skills")
        .order_by("-hired_at")[:4]
    )
    return render(
        request,
        "employees/index.html",
        {"employees": employees, "total_employees": total},
    )


class EmployeeListView(generic.ListView):
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"
    paginate_by = EMPLOYEES_PER_PAGE

    def get_queryset(self):
        return (
            Employee.objects.select_related("workplace")
            .prefetch_related("images", "skills")
            .order_by("surname", "name")
        )


class EmployeeDetailView(LoginRequiredMixin, generic.DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"

    def get_queryset(self):
        return Employee.objects.select_related("workplace").prefetch_related(
            "images", "skills"
        )
