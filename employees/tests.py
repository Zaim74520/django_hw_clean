from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from employees.models import Employee
from employees.validators import validate_neighbor_positions
from workplaces.models import Workplace


class BaseTestCase(TestCase):
    """Общая подготовка данных для тестов."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="tutor",
            password="testpass123",
        )
        self.desk_1 = Workplace.objects.create(room_number="1")
        self.desk_2 = Workplace.objects.create(room_number="2")
        self.desk_3 = Workplace.objects.create(room_number="3")
        self.desk_10 = Workplace.objects.create(room_number="10")

        self.employee = Employee.objects.create(
            surname="Иванов",
            name="Иван",
            patronymic="Иванович",
            gender="M",
            position="бэкенд-разработчик",
            workplace=self.desk_1,
            hired_at=date.today() - timedelta(days=30),
        )
        for day in range(2, 6):
            Employee.objects.create(
                surname=f"Сотрудник{day}",
                name="Тест",
                position="аналитик",
                hired_at=date.today() - timedelta(days=day * 10),
            )


class IndexPageTests(BaseTestCase):
    """Тесты главной страницы."""

    def test_index_page_available(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_page_context_has_total_employees(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.context["total_employees"], 5)

    def test_index_page_shows_four_latest_employees(self):
        response = self.client.get(reverse("index"))
        employees = response.context["employees"]
        self.assertEqual(len(employees), 4)
        expected_pks = list(
            Employee.objects.order_by("-hired_at")[:4].values_list("pk", flat=True)
        )
        self.assertEqual(list(employees.values_list("pk", flat=True)), expected_pks)


class EmployeeListPageTests(BaseTestCase):
    """Тесты страницы со списком сотрудников."""

    def test_list_page_available(self):
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(response.status_code, 200)

    def test_list_page_context_has_employees(self):
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(len(response.context["employees"]), 5)

    def test_list_page_pagination_ten_per_page(self):
        for i in range(6, 15):
            Employee.objects.create(
                surname=f"Пагинация{i}",
                name="Тест",
                position="аналитик",
            )
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["employees"]), 10)
        self.assertEqual(response.context["paginator"].num_pages, 2)


class EmployeeDetailPageTests(BaseTestCase):
    """Тесты прав доступа к подробной карточке сотрудника."""

    def test_detail_page_requires_login(self):
        response = self.client.get(reverse("employee_detail", args=[self.employee.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_detail_page_available_for_logged_in_user(self):
        self.client.login(username="tutor", password="testpass123")
        response = self.client.get(reverse("employee_detail", args=[self.employee.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_page_context_has_employee(self):
        self.client.login(username="tutor", password="testpass123")
        response = self.client.get(reverse("employee_detail", args=[self.employee.pk]))
        self.assertEqual(response.context["employee"], self.employee)

    def test_detail_page_returns_404_for_missing_employee(self):
        self.client.login(username="tutor", password="testpass123")
        response = self.client.get(reverse("employee_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)


class NeighborValidatorTests(TestCase):
    """Тесты валидатора: разработчики и тестировщики не за соседними столами."""

    def setUp(self):
        self.desk_1 = Workplace.objects.create(room_number="1")
        self.desk_2 = Workplace.objects.create(room_number="2")
        self.desk_3 = Workplace.objects.create(room_number="3")
        self.desk_5 = Workplace.objects.create(room_number="5")

        self.developer = Employee.objects.create(
            surname="Разработчик",
            name="Пётр",
            position="бэкенд-разработчик",
            workplace=self.desk_1,
        )

    def test_tester_cannot_sit_next_to_developer(self):
        tester = Employee(
            surname="Тестировщик",
            name="Мария",
            position="тестировщик",
            workplace=self.desk_2,
        )
        with self.assertRaises(ValidationError):
            validate_neighbor_positions(tester)

    def test_developer_cannot_sit_next_to_tester(self):
        tester = Employee.objects.create(
            surname="Тестировщица",
            name="Ольга",
            position="тестировщик",
            workplace=self.desk_3,
        )
        developer = Employee(
            surname="Разработчик2",
            name="Игорь",
            position="фронтенд-разработчик",
            workplace=self.desk_2,
        )
        with self.assertRaises(ValidationError):
            validate_neighbor_positions(developer)

    def test_developer_can_sit_far_from_tester(self):
        tester = Employee.objects.create(
            surname="Тестировщик",
            name="Анна",
            position="тестировщик",
            workplace=self.desk_5,
        )
        developer = Employee(
            surname="Разработчик3",
            name="Сергей",
            position="бэкенд-разработчик",
            workplace=self.desk_1,
        )
        try:
            validate_neighbor_positions(developer)
        except ValidationError:
            self.fail("Разработчик на несоседнем столе не должен вызывать ошибку")

    def test_two_developers_can_sit_next_to_each_other(self):
        developer = Employee(
            surname="Разработчик4",
            name="Артём",
            position="бэкенд-разработчик",
            workplace=self.desk_2,
        )
        try:
            validate_neighbor_positions(developer)
        except ValidationError:
            self.fail("Два разработчика за соседними столами — допустимо")

    def test_save_blocks_tester_next_to_developer(self):
        tester = Employee(
            surname="Тестировщик",
            name="Елена",
            position="тестировщик",
            workplace=self.desk_2,
        )
        with self.assertRaises(ValidationError):
            tester.save()

    def test_save_allows_tester_far_from_developer(self):
        tester = Employee(
            surname="Тестировщик",
            name="Елена",
            position="тестировщик",
            workplace=self.desk_5,
        )
        try:
            tester.save()
        except ValidationError:
            self.fail("Тестировщик на несоседнем столе должен сохраняться")
