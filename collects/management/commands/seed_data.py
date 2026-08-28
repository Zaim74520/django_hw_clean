import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from collects.models import Collect, Payment

REASONS = ["birthday", "wedding", "graduation", "holiday", "other"]
FIRST_NAMES = ["Алексей", "Мария", "Дмитрий", "Елена", "Сергей", "Анна"]
LAST_NAMES = ["Иванов", "Смирнов", "Кузнецов", "Попов", "Соколов"]


class Command(BaseCommand):
    help = "Наполняет БД моковыми данными: пользователи, сборы, платежи"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Количество создаваемых сборов (по умолчанию 100)",
        )

    def handle(self, *args, **options):
        count = options["count"]

        user, _ = User.objects.get_or_create(
            username="demo_author",
            defaults={"email": "demo@example.com"},
        )
        user.set_password("demo123")
        user.save()

        self.stdout.write(f"Пользователь demo_author / demo123")

        for i in range(count):
            collect = Collect.objects.create(
                author=user,
                title=f"Сбор #{i + 1}: {random.choice(REASONS)}",
                reason=random.choice(REASONS),
                description=f"Тестовый сбор номер {i + 1}",
                goal_amount=random.choice([None, 5000, 10000, 50000, 100000]),
                end_date=timezone.now() + timedelta(days=random.randint(1, 90)),
            )
            payments_count = random.randint(0, 10)
            for _ in range(payments_count):
                amount = random.randint(100, 3000)
                Payment.objects.create(
                    collect=collect,
                    user=user,
                    amount=amount,
                    full_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                )
                collect.current_amount += amount
            collect.save()

        total_collects = Collect.objects.count()
        total_payments = Payment.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Создано: {total_collects} сборов, {total_payments} платежей"
            )
        )