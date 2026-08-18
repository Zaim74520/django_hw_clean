from django.contrib import admin

from .models import Workplace


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ("room_number", "is_active")
    list_filter = ("is_active",)
    search_fields = ("room_number",)


# Register your models here.
