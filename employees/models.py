from datetime import date

from django.db import models

from .validators import validate_neighbor_positions


class Skill(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название навыка")
    skill_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Тип навыка",
        help_text="Например: технический, софт-скилл",
    )
    level = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Уровень",
        help_text="Например: junior, middle, expert",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Например, уровень владения или детали",
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    GENDER_CHOICES = [
        ("M", "Мужской"),
        ("F", "Женский"),
    ]

    surname = models.CharField(max_length=50, verbose_name="Фамилия")
    name = models.CharField(max_length=50, verbose_name="Имя")
    patronymic = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Отчество",
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name="Пол",
    )
    position = models.CharField(max_length=100, verbose_name="Должность")

    hired_at = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата приёма на работу",
    )

    workplace = models.OneToOneField(
        "workplaces.Workplace",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee",
        verbose_name="Рабочее место",
    )

    skills = models.ManyToManyField(
        Skill,
        related_name="employees",
        blank=True,
        verbose_name="Навыки",
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["surname", "name"]

    def clean(self):
        validate_neighbor_positions(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def tenure_days(self):
        if not self.hired_at:
            return None
        return (date.today() - self.hired_at).days

    def __str__(self):
        # Если отчества нет, показываем только фамилию и имя
        if self.patronymic:
            return f"{self.surname} {self.name} {self.patronymic}"
        return f"{self.surname} {self.name}"


class EmployeeImage(models.Model):
    employee = models.ForeignKey(
        "Employee",
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to="employee_photos/",
        verbose_name="Фото",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения",
    )

    class Meta:
        verbose_name = "Фото сотрудника"
        verbose_name_plural = "Фото сотрудников"
        ordering = ["order"]

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Фото {self.employee.surname} {self.employee.name}"
