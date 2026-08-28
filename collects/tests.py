from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import Collect, Payment


class CollectTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("author", password="pass123")
        self.other = User.objects.create_user("other", password="pass123")
        self.client = APIClient()

        self.collect = Collect.objects.create(
            author=self.user,
            title="Тестовый сбор",
            reason="birthday",
            goal_amount=10000,
            end_date=timezone.now() + timedelta(days=30),
        )
        self.finished_collect = Collect.objects.create(
            author=self.other,
            title="Завершённый",
            reason="wedding",
            goal_amount=5000,
            end_date=timezone.now() - timedelta(days=1),
        )

    # --- Доступность списка ---
    def test_collect_list_available(self):
        response = self.client.get("/api/collects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Создание сбора ---
    def test_create_collect_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/collects/", {
            "title": "Новый сбор",
            "reason": "wedding",
            "end_date": (timezone.now() + timedelta(days=10)).isoformat(),
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_collect_unauthenticated(self):
        response = self.client.post("/api/collects/", {
            "title": "Новый сбор",
            "reason": "wedding",
            "end_date": (timezone.now() + timedelta(days=10)).isoformat(),
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Детальная ---
    def test_collect_detail_available(self):
        response = self.client.get(f"/api/collects/{self.collect.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Тестовый сбор", str(response.data))

    # --- Редактирование ---
    def test_edit_collect_by_author(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/api/collects/{self.collect.pk}/",
            {"title": "Обновлённый сбор"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_edit_collect_by_other(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f"/api/collects/{self.collect.pk}/",
            {"title": "Чужой сбор"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Удаление ---
    def test_delete_collect_by_author(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/collects/{self.collect.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # --- Платежи ---
    def test_payment_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/payments/", {
            "collect": self.collect.pk,
            "amount": "500.00",
            "full_name": "Иван Иванов",
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_payment_to_finished_collect_fails(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/payments/", {
            "collect": self.finished_collect.pk,
            "amount": "500.00",
            "full_name": "Иван Иванов",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_exceeds_goal_fails(self):
        self.client.force_authenticate(user=self.user)
        Payment.objects.create(
            collect=self.collect, user=self.user,
            amount=9800, full_name="Почти всё",
        )
        self.collect.current_amount = 9800
        self.collect.save()
        response = self.client.post("/api/payments/", {
            "collect": self.collect.pk,
            "amount": "500.00",
            "full_name": "Ещё немного",
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Фильтрация ---
    def test_filter_by_reason(self):
        response = self.client.get("/api/collects/?reason=birthday")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        titles = [item["title"] for item in data]
        self.assertIn("Тестовый сбор", titles)
        self.assertNotIn("Завершённый", titles)

    # --- Active endpoint ---
    def test_active_collects(self):
        response = self.client.get("/api/collects/active/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get("results", response.data)
        titles = [item["title"] for item in data]
        self.assertIn("Тестовый сбор", titles)
        self.assertNotIn("Завершённый", titles)