from django.db import models
from workplaces.models import Workplace


class Skill(models.Model):
    SKILL_TYPES = [
        ("frontend", "Фронтенд"),
        ("backend", "Бэкенд"),
        ("testing", "Тестирование"),
        ("management", "Управление проектами"),
        ("other", "Другое"),
    ]

    name = models.CharField(max_length=100, verbose_name="Название навыка")
    skill_type = models.CharField(
        max_length=20, choices=SKILL_TYPES, verbose_name="Тип навыка"
    )
    level = models.IntegerField(
        verbose_name="Уровень владения",
        default=1,
        choices=[(i, i) for i in range(1, 11)],
    )
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return f"{self.name} (уровень {self.level})"


class Employee(models.Model):
    GENDER_CHOICES = [
        ("male", "Мужской"),
        ("female", "Женский"),
        ("other", "Другой"),
    ]

    name = models.CharField(max_length=100, verbose_name="Имя")
    surname = models.CharField(max_length=100, verbose_name="Фамилия", blank=True)
    patronymic = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Отчество"
    )
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, verbose_name="Пол", default="other"
    )
    position = models.CharField(max_length=100, verbose_name="Должность")
    workplace = models.ForeignKey(
        Workplace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Рабочее место",
    )

    skills = models.ManyToManyField(
        Skill,
        related_name="employees",
        blank=True,
        verbose_name="Навыки",
    )

    def __str__(self):
        return f"{self.name} {self.surname}"  # <-- теперь surname существует
