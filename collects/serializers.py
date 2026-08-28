from django.utils import timezone
from rest_framework import serializers

from .models import Collect, Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "collect", "user", "amount", "full_name", "created_at"]
        read_only_fields = ["created_at", "collect"]


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "collect", "user", "amount", "full_name", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        collect = data.get("collect")
        amount = data.get("amount")
        if collect.end_date and collect.end_date < timezone.now():
            raise serializers.ValidationError("Сбор уже завершён")
        if collect.goal_amount and collect.current_amount + amount > collect.goal_amount:
            raise serializers.ValidationError(
                "Сумма платежа превышает оставшуюся целевую сумму"
            )
        return data


class CollectListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    payment_count = serializers.SerializerMethodField()

    class Meta:
        model = Collect
        fields = [
            "id", "author", "author_name", "title", "reason",
            "goal_amount", "current_amount", "cover", "end_date",
            "created_at", "payment_count",
        ]
        read_only_fields = ["current_amount", "created_at"]

    def get_payment_count(self, obj):
        return getattr(obj, "payment_count", obj.payments.count())


class CollectDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Collect
        fields = [
            "id", "author", "author_name", "title", "reason",
            "description", "goal_amount", "current_amount",
            "cover", "end_date", "created_at", "payments",
            "progress_percent",
        ]
        read_only_fields = ["current_amount", "created_at"]

    def get_progress_percent(self, obj):
        if obj.goal_amount:
            return round(float(obj.current_amount / obj.goal_amount * 100), 1)
        return None


class CollectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collect
        fields = [
            "author", "title", "reason", "description",
            "goal_amount", "cover", "end_date",
        ]
        read_only_fields = ["author"]

    def validate_end_date(self, value):
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Дата завершения должна быть в будущем")
        return value