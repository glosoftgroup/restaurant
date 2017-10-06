from ...table.models import Table
from .serializers import (
    TableListSerializer,
     )
from rest_framework import generics
from django.contrib.auth import get_user_model
User = get_user_model()


class TableListAPIView(generics.ListAPIView):
    serializer_class = TableListSerializer
    queryset = Table.objects.all()