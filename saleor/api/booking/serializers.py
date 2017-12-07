# table rest api serializers

from rest_framework import serializers
from django.contrib.auth import get_user_model
from saleor.booking.models import Book as Table
from saleor.booking.models import Payment
from saleor.customer.models import Customer
User = get_user_model()


class PaymentListSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ('id',
                  'invoice_number',
                  'book',
                  'amount',
                  'payment_option',
                  'date',
                  'customer_name',
                  'description',
                  'created'
                 )

    def get_amount(self, obj):
        try:
            return obj.amount_paid.gross
        except Exception as e:
            return 0

    def get_customer_name(self, obj):
        try:
            return obj.customer.name
        except Exception as e:
            print e
            return ''

