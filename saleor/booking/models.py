from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import pgettext_lazy
from django.core.validators import MinValueValidator, RegexValidator
from django_prices.models import PriceField
from ..room.models import Room
from ..customer.models import Customer


class Book(models.Model):
    description = models.CharField(
        pgettext_lazy('Book field', 'Table name'),
        max_length=152, default='', null=True, blank=True)
    price_type = models.CharField(
        pgettext_lazy('Book field', 'price type'),
        max_length=152, default='', null=True, blank=True)
    price = PriceField(
        pgettext_lazy('Book field', 'price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12,
        validators=[MinValueValidator(0)], default=Decimal(0), decimal_places=2)
    days = models.IntegerField(default=Decimal(1))
    child = models.IntegerField(default=Decimal(0))
    adult = models.IntegerField(default=Decimal(1))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, related_name='booking_user',
        verbose_name=pgettext_lazy('Book field', 'user'))
    customer = models.ForeignKey(
        Customer, blank=True, null=True, related_name='booking_customers',
        verbose_name=pgettext_lazy('Book field', 'customer'))
    room = models.ForeignKey(
        Room, verbose_name=pgettext_lazy('Book field', 'rooms'),
        related_name='booking_room',  blank=True, null=True,)
    check_in = models.DateTimeField(
        pgettext_lazy('Book field', 'Date from'),
        default=now)
    check_out = models.DateTimeField(
        pgettext_lazy('Book field', 'Date until'),
        default=now)
    created = models.DateTimeField(
        pgettext_lazy('Book field', 'created'),
        default=now, editable=False)

    class Meta:
        verbose_name = pgettext_lazy('Booking model', 'Booking')
        verbose_name_plural = pgettext_lazy('Booking model', 'Bookings')

    def __str__(self):
        return str(self.name) + ' #' + str(self.number)

