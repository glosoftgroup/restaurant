from rest_framework.response import Response
from rest_framework.request import Request
from saleor.booking.models import Payment as Table
from .serializers import (
    PaymentListSerializer,
     )
from rest_framework import generics
from django.contrib.auth import get_user_model
User = get_user_model()


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentListSerializer
    queryset = Table.objects.all()

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        queryset = self.get_queryset().filter(book__pk=pk)
        serializer = PaymentListSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)

