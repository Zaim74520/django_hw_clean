import django.db.models.deletion
from django.db import migrations, models


def link_workplaces(apps, schema_editor):
    Employee = apps.get_model("employees", "Employee")
    Workplace = apps.get_model("workplaces", "Workplace")
    for employee in Employee.objects.all():
        workplace = Workplace.objects.filter(
            room_number=str(employee.workplace_old)
        ).first()
        if workplace:
            employee.workplace = workplace
            employee.save(update_fields=["workplace"])


class Migration(migrations.Migration):

    dependencies = [
        ("employees", "0002_skill_alter_employee_options_employee_gender_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="employee",
            old_name="workplace",
            new_name="workplace_old",
        ),
        migrations.AddField(
            model_name="employee",
            name="workplace",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="employee",
                to="workplaces.workplace",
                verbose_name="Рабочее место",
            ),
        ),
        migrations.RunPython(link_workplaces, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="employee",
            name="workplace_old",
        ),
    ]
