from django.db import models


class Workplace(models.Model):
    room_number = models.CharField(
        max_length=10, unique=True
    )  # теперь только цифры: "201", "101"
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Кабинет {self.room_number}"  # слово «Кабинет» добавляется только при отображении


# Create your models here.
