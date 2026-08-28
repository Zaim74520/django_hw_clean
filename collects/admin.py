from django.contrib import admin

from .models import Collect, Payment


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "reason", "goal_amount", "current_amount", "end_date")
    list_filter = ("reason",)
    search_fields = ("title", "description")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("collect", "full_name", "amount", "created_at")
    list_filter = ("collect",)