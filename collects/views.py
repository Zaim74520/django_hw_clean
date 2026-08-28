from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Collect, Payment
from .permissions import CollectPermission
from .serializers import (
    CollectDetailSerializer,
    CollectListSerializer,
    CollectWriteSerializer,
    PaymentCreateSerializer,
    PaymentSerializer,
)


class CollectViewSet(viewsets.ModelViewSet):
    queryset = Collect.objects.select_related("author").prefetch_related("payments")
    permission_classes = [CollectPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "reason": ["exact"],
        "author": ["exact"],
        "end_date": ["gte", "lte"],
    }
    ordering_fields = ["created_at", "end_date", "current_amount"]

    def get_serializer_class(self):
        if self.action == "list":
            return CollectListSerializer
        elif self.action == "retrieve":
            return CollectDetailSerializer
        return CollectWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False, methods=["get"])
    def active(self, request):
        from django.utils import timezone
        collects = self.get_queryset().filter(end_date__gte=timezone.now())
        page = self.paginate_queryset(collects)
        if page is not None:
            serializer = CollectListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = CollectListSerializer(collects, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("collect", "user")
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "collect": ["exact"],
        "user": ["exact"],
    }
    ordering_fields = ["created_at", "amount"]

    def get_serializer_class(self):
        if self.action == "create":
            return PaymentCreateSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user if self.request.user.is_authenticated else None)