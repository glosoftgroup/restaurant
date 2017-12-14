from django.db.models import Q
from rest_framework import pagination
from rest_framework import generics
from django.contrib.auth import get_user_model

from .pagination import CustomPagination
from .serializers import (
     CustomerListSerializer,
     CreditWorthyCustomerSerializer,
     CustomerUpdateSerializer,
     )

from ...customer.models import Customer as Table
import logging

User = get_user_model()
debug_logger = logging.getLogger('debug_logger')
info_logger = logging.getLogger('info_logger')
error_logger = logging.getLogger('error_logger')     


class CreditWorthyCustomerListAPIView(generics.ListAPIView):
    serializer_class = CreditWorthyCustomerSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = Table.objects.filter(creditable=True)
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)               
                ).distinct()
        return queryset_list


class CustomerListAPIView(generics.ListAPIView):   
    serializer_class = CustomerListSerializer

    def get_queryset(self, *args, **kwargs):        
        queryset_list = Table.objects.all()
        query = self.request.GET.get('q')
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query)|  
                Q(mobile__icontains=query)             
                ).distinct()
        return queryset_list


class CustomerDetailAPIView(generics.RetrieveAPIView):
    queryset = Table.objects.all()
    serializer_class = CustomerListSerializer


class CustomerUpdateAPIView(generics.RetrieveUpdateAPIView):    
    queryset = Table.objects.all()
    serializer_class = CustomerUpdateSerializer


class CustomerPagListAPIView(generics.ListAPIView):
    serializer_class = CustomerListSerializer
    pagination_class = CustomPagination
    queryset = Table.objects.all()

    def get_queryset(self, *args, **kwargs):
        queryset_list = Table.objects.all().select_related()
        query = self.request.GET.get('q')
        page_size = 'page_size'
        if self.request.GET.get(page_size):
            pagination.PageNumberPagination.page_size = self.request.GET.get(page_size)
        else:
            pagination.PageNumberPagination.page_size = 10
        if self.request.GET.get('date'):
            queryset_list = queryset_list.filter(date_joined__icontains=self.request.GET.get('date'))
        if query:
            queryset_list = queryset_list.filter(
                Q(name__icontains=query) |
                Q(mobile__icontains=query) |
                Q(email__icontains=query)
                ).distinct()
        return queryset_list
