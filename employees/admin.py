from django.contrib import admin
from .models import Employee, Skill


class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "skill_type", "level")
    list_filter = ("skill_type",)
    search_fields = ("name",)


admin.site.register(Skill, SkillAdmin)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    # Убрали 'skills' из list_display, чтобы убрать ошибку admin.E109
    list_display = ("surname", "name", "patronymic", "position", "workplace", "gender")

    list_filter = ("workplace", "gender")
    search_fields = ("surname", "name", "patronymic")

    # В fields оставляем skills, чтобы в форме создания/редактирования
    # можно было выбирать навыки. Порядок: Фамилия, Имя, Отчество
    fields = (
        "surname",
        "name",
        "patronymic",
        "gender",
        "position",
        "workplace",
        "skills",
    )
