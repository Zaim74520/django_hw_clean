from rest_framework import serializers

from .models import Employee, EmployeeImage, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "skill_type", "level"]


class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = ["id", "image", "order"]


class EmployeeListSerializer(serializers.ModelSerializer):
    skills = serializers.StringRelatedField(many=True)
    first_image = serializers.SerializerMethodField()
    tenure_days = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "surname",
            "name",
            "patronymic",
            "position",
            "skills",
            "first_image",
            "tenure_days",
        ]

    def get_first_image(self, obj):
        first = obj.images.first()
        return first.image.url if first else None

    def get_tenure_days(self, obj):
        return obj.tenure_days()


class EmployeeDetailSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    images = EmployeeImageSerializer(many=True, read_only=True)
    workplace_number = serializers.CharField(
        source="workplace.room_number", read_only=True
    )
    tenure_days = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "surname",
            "name",
            "patronymic",
            "gender",
            "position",
            "hired_at",
            "workplace",
            "workplace_number",
            "skills",
            "images",
            "tenure_days",
        ]
        read_only_fields = ["workplace"]

    def get_tenure_days(self, obj):
        return obj.tenure_days()


class EmployeeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "surname",
            "name",
            "patronymic",
            "gender",
            "position",
            "hired_at",
            "workplace",
            "skills",
        ]