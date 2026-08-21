from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic

from .models import Employee


def index(request):
    employees = Employee.objects.all()
    return render(request, "employees/index.html", {"employees": employees})


class EmployeeListView(generic.ListView):
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"


class EmployeeDetailView(LoginRequiredMixin, generic.DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"
