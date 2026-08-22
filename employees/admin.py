from django.contrib import admin

from .models import Employee, EmployeeImage, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "skill_type", "level")
    list_filter = ("skill_type",)
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "surname",
        "name",
        "patronymic",
        "position",
        "workplace",
        "gender",
        "hired_at",
    )
    list_filter = ("workplace", "gender")
    search_fields = ("surname", "name", "patronymic")
    fields = (
        "surname",
        "name",
        "patronymic",
        "gender",
        "position",
        "hired_at",
        "workplace",
        "skills",
    )


@admin.register(EmployeeImage)
class EmployeeImageAdmin(admin.ModelAdmin):
    list_display = ("employee", "order")
