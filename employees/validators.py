from django.core.exceptions import ValidationError

DEVELOPER_WORDS = (
    "бэкенд",
    "бекенд",
    "бэкендер",
    "бекендер",
    "фронтенд",
    "фронтендер",
    "backend",
    "frontend",
    "разработчик",
    "программист",
    "developer",
)
TESTER_WORDS = ("тестировщик", "тестер", "qa", "тестировщица", "tester")


def is_developer(position):
    text = (position or "").lower()
    return any(word in text for word in DEVELOPER_WORDS)


def is_tester(position):
    text = (position or "").lower()
    return any(word in text for word in TESTER_WORDS)


def validate_neighbor_positions(employee):
    """Проверяет, что разработчики и тестировщики не сидят за соседними столами."""
    if not employee.workplace_id:
        return

    try:
        current_number = int(str(employee.workplace.room_number))
    except (TypeError, ValueError):
        return

    from .models import Employee

    current_is_dev = is_developer(employee.position)
    current_is_test = is_tester(employee.position)

    if not (current_is_dev or current_is_test):
        return

    neighbors = Employee.objects.filter(
        workplace__room_number__in=[str(current_number - 1), str(current_number + 1)]
    ).exclude(pk=employee.pk)

    for neighbor in neighbors:
        if current_is_dev and is_tester(neighbor.position):
            raise ValidationError(
                f"Разработчик не может сидеть за соседним столом с тестировщиком "
                f"(стол {neighbor.workplace.room_number})."
            )
        if current_is_test and is_developer(neighbor.position):
            raise ValidationError(
                f"Тестировщик не может сидеть за соседним столом с разработчиком "
                f"(стол {neighbor.workplace.room_number})."
            )
