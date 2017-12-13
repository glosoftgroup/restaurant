from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import generics
from rest_framework import pagination
from django.contrib.auth import get_user_model
from django.db.models import Q

from saleor.booking.models import Book as Table
from saleor.booking.models import Payment
from .pagination import PostLimitOffsetPagination
from .serializers import (
    PaymentListSerializer,
    BookingListSerializer
     )

User = get_user_model()


class BookingListAPIView(generics.ListAPIView):
    serializer_class = BookingListSerializer
    pagination_class = PostLimitOffsetPagination
    queryset = Table.objects.all()

    def get_queryset(self, *args, **kwargs):
        queryset_list = Table.objects.all().select_related()
        query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('status'):
            if self.request.GET.get('status') == 'True':
                queryset_list = queryset_list.filter(active=True)
            if self.request.GET.get('status') == 'False':
                queryset_list = queryset_list.filter(active=False)
        if self.request.GET.get('date'):
            if self.request.GET.get('date') is not 'null':
                queryset_list = queryset_list.filter(created__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(invoice_number__icontains=query) |
                Q(customer__name__icontains=query) |
                Q(room__name__icontains=query)
                ).distinct()
        return queryset_list


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentListSerializer
    queryset = Payment.objects.all()

    def list(self, request, pk=None):
        serializer_context = {
            'request': Request(request),
        }
        queryset = self.get_queryset().filter(book__pk=pk)
        serializer = PaymentListSerializer(queryset, context=serializer_context, many=True)
        return Response(serializer.data)

