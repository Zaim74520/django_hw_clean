from django.core.validators import MinValueValidator
from django.db import models


class Collect(models.Model):
    REASON_CHOICES = [
        ("birthday", "День рождения"),
        ("wedding", "Свадьба"),
        ("graduation", "Выпускной"),
        ("holiday", "Праздник"),
        ("other", "Другое"),
    ]

    author = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="collects",
        verbose_name="Автор сбора",
    )
    title = models.CharField(max_length=200, verbose_name="Название")
    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES,
        default="other",
        verbose_name="Повод",
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    goal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Целевая сумма",
        help_text="Оставьте пустым для бесконечного сбора",
    )
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Текущая сумма",
    )
    cover = models.ImageField(
        upload_to="collect_covers/",
        blank=True,
        null=True,
        verbose_name="Обложка",
    )
    end_date = models.DateTimeField(verbose_name="Дата и время завершения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Групповой сбор"
        verbose_name_plural = "Групповые сборы"
        ordering = ["-created_at"]

    def delete(self, *args, **kwargs):
        if self.cover:
            self.cover.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title


class Payment(models.Model):
    collect = models.ForeignKey(
        Collect,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Сбор",
    )
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Пользователь",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Сумма",
    )
    full_name = models.CharField(
        max_length=150,
        verbose_name="ФИО",
        help_text="ФИО пользователя, сделавшего пожертвование",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.amount} ({self.collect.title})"