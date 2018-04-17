from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from django.db.models import F
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import pgettext_lazy
from django_countries.fields import Country, CountryField


class AddressBookManager(models.Manager):

    def as_data(self, address):
        data = model_to_dict(addressbook, exclude=['id', 'user'])
        if isinstance(data['country'], Country):
            data['country'] = data['country'].code
        return data

    def are_identical(self, addr1, addr2):
        data1 = self.as_data(addr1)
        data2 = self.as_data(addr2)
        return data1 == data2

    def store_address(self, user, address):
        data = self.as_data(address)
        address, dummy_created = user.addresses.get_or_create(**data)
        return address


@python_2_unicode_compatible
class AddressBook(models.Model):
    name = models.CharField(
        pgettext_lazy('AddressBook field', 'Name'),
        max_length=256, blank=True)
    maturity_status = models.CharField(
        pgettext_lazy('AddressBook field', 'Child / Adult'),
        max_length=256, blank=True)
    id_no = models.CharField(
        pgettext_lazy('AddressBook field', 'ID or Passport No'),
        max_length=256, blank=True)
    nationality = models.CharField(
        pgettext_lazy('AddressBook field', 'Nationality'),
        max_length=256, blank=True)
    dob = models.CharField(
        pgettext_lazy('AddressBook field', 'Date of Birth'),
        max_length=256, blank=True)
    relation = models.CharField(
        pgettext_lazy('AddressBook field', 'Relation'),
        max_length=256, blank=True)
    phone = models.CharField(
        pgettext_lazy('AddressBook field', 'Phone Number'),
        max_length=30, unique=True, blank=True)
    objects = AddressBookManager()

    @property
    def full_name(self):
        return '%s' % (self.contact_name)

    class Meta:
        verbose_name = pgettext_lazy('AddressBook model', 'address book')
        verbose_name_plural = pgettext_lazy('AddressBook model', 'address books')

    def __str__(self):
        if self.name:
            return '%s - %s' % (self.name, self.nationality)
        return self.name

    def __repr__(self):
        return (
            'AddressBook(name=%r, dob=%r, '
            'id_no=%r, relation=%r, maturity_status=%r,  nationality=%r, phone=%r)' % (
                self.name, self.dob, self.id_no, self.relation,
                self.maturity_status, self.nationality, self.phone))


class CustomerManager(BaseUserManager):

    def create_customer(self, email, password=None,
                    is_active=True, username='', **extra_fields):
        'Creates a User with the given username, email and password'
        email = CustomerManager.normalize_email(email)
        customer = self.model(email=email, is_active=is_active,
                           **extra_fields)
        if password:
            customer.set_password(password)
        customer.save()
        return customer

    def redeem_points(self, customer, points):
        customer.loyalty_points = F('loyalty_points') - points        
        customer.redeemed_loyalty_points = F('redeemed_loyalty_points') + points
        customer.save(update_fields=['loyalty_points', 'redeemed_loyalty_points'])
    
    def gain_points(self, customer, points):
        customer.loyalty_points = F('loyalty_points') + points        
        customer.save(update_fields=['loyalty_points'])
    

class Customer(models.Model):
    name = models.CharField(pgettext_lazy('Customer field', 'Name'), max_length=100, null=True, blank=True)
    email = models.EmailField(pgettext_lazy('Customer field', 'Email'), null=True, blank=True)
    nid = models.CharField(pgettext_lazy('Customer field', 'ID No / Passport'), max_length=128, null=True, blank=True)
    nationality = models.CharField(pgettext_lazy('Customer field', 'Country'), max_length=128, null=True, blank=True)
    dob = models.CharField(pgettext_lazy('Customer field', 'Date of Birth'), max_length=128, null=True, blank=True)
    description = models.CharField(pgettext_lazy('Customer field', 'User Description'), max_length=500, null=True, blank=True)
    addresses = models.ManyToManyField(
        AddressBook, blank=True,
        verbose_name=pgettext_lazy('Customer field', 'addresses'))   
    is_active = models.BooleanField(
        pgettext_lazy('Customer field', 'active'),
        default=True)
    creditable = models.BooleanField(default=False)
    loyalty_points = models.DecimalField(
        pgettext_lazy('Customer field', 'loyalty points'), default=Decimal(0), max_digits=100, decimal_places=2)    
    redeemed_loyalty_points = models.DecimalField(
        pgettext_lazy('Customer field', 'Redeemed loyalty points'), default=Decimal(0), max_digits=100, decimal_places=2)    
    mobile = models.CharField(pgettext_lazy('Customer field', 'Phone No'), max_length=100, null=True, blank=True)
    image = models.FileField(upload_to='employee', blank=True, null=True)
    date_joined = models.DateTimeField(
        pgettext_lazy('Customer field', 'date joined'),
        default=timezone.now, editable=False)
    default_shipping_address = models.ForeignKey(
        AddressBook, related_name='+', null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('Customer field', 'default shipping address'))
    default_billing_address = models.ForeignKey(
        AddressBook, related_name='+', null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=pgettext_lazy('Customer field', 'default billing address'))

    # USERNAME_FIELD = 'email'

    objects = CustomerManager()

    # search_fields = [
    #     index.SearchField('email')]

    class Meta:
        verbose_name = pgettext_lazy('Customer model', 'customer')
        verbose_name_plural = pgettext_lazy('Customer model', 'customers')

    def __str__(self):
        return self.name

    def get_full_name(self):
        return self.email
        
    def is_creditable_check_box(self):
        if self.creditable:
            return "checked='checked'"
        return ''

    def get_short_name(self):
        return self.email

    def get_addresses(self):
        return self.addresses.all()

    def get_child_count(self):
        return self.addresses.all().filter(maturity_status='child').count()

    def get_adult_count(self):
        return (self.addresses.all().filter(maturity_status='adult').count() + 1)

    def get_sales(self):
        return len(self.customers.all())

    def get_total_discount(self):
        total = self.customers.aggregate(models.Sum('discount_amount'))['discount_amount__sum']
        if total:
            return cool_format(total)
        return '--'

    def get_total_sales_amount(self):
        total = self.customers.aggregate(models.Sum('total_net'))['total_net__sum']
        if total:
            return cool_format(total)+' '+settings.DEFAULT_CURRENCY
        return '--'

    def get_total_credit_amount(self):
        total = self.credit_customers.aggregate(models.Sum('total_net'))['total_net__sum']
        if total:
            return cool_format(total)+' '+settings.DEFAULT_CURRENCY
        return '--'

    def get_credits(self):
        return len(self.credit_customers.all())    

    def get_loyalty_points(self):
        if self.loyalty_points != 0.00:
            return cool_format(self.loyalty_points)
        return 0

    def get_redeemed_loyalty_points(self):
        if self.redeemed_loyalty_points != 0.00:
            return cool_format(self.redeemed_loyalty_points)
        return 0

    def get_loy_perc(self):        
        redeemed = self.redeemed_loyalty_points
        loyalty  = self.loyalty_points
        total = redeemed + loyalty       
        if not total:
            return 0.00
        return (100*loyalty)/total

    def get_rem_perc(self):        
        redeemed = self.redeemed_loyalty_points
        loyalty  = self.loyalty_points
        total = redeemed + loyalty        
        if not total:
            return 0.00
        return (100*redeemed)/total


def cool_format(value):
     value = Decimal(value)
     if value < 1000.00:
        return str("%.2f" % value)
     elif value < Decimal(1000000.0):
        value = value/Decimal(1000.0)
        return str("%.2f" % value) + 'K'
     else:
        return str("%.2f" % value/Decimal(1000000.0)) + 'M'