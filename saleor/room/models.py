from __future__ import unicode_literals

import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import HStoreField
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.timezone import now
from django.db.models import F, Max, Q, Sum
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.text import slugify
from django.utils.translation import pgettext_lazy
from django.utils import six
from django_prices.models import PriceField
from mptt.managers import TreeManager
from mptt.models import MPTTModel
from prices import PriceRange
from satchless.item import InsufficientStock, Item, ItemRange
from text_unidecode import unidecode
from versatileimagefield.fields import VersatileImageField, PPOIField

from ..discount.models import calculate_discounted_price
from ..search import index
from .utils import get_attributes_display_map


class Package(models.Model):
    name = models.CharField(
        pgettext_lazy('Package field', 'name'), max_length=128, unique=True)

    class Meta:
        verbose_name = pgettext_lazy('Package model', 'package')
        verbose_name_plural = pgettext_lazy('Package model', 'package')
        app_label = 'room'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class RoomCategory(MPTTModel):
    name = models.CharField(
        pgettext_lazy('Category field', 'name'), max_length=128, unique=True)
    slug = models.SlugField(
        pgettext_lazy('Category field', 'slug'), max_length=50)
    description = models.TextField(
        pgettext_lazy('Category field', 'description'), blank=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='rooms_category_children',
        verbose_name=pgettext_lazy('Category field', 'parent'))
    hidden = models.BooleanField(
        pgettext_lazy('Category field', 'hidden'), default=False)

    objects = models.Manager()
    tree = TreeManager()

    class Meta:
        verbose_name = pgettext_lazy('Room Category model', 'room categories')
        verbose_name_plural = pgettext_lazy('Room Category model', 'room categories')
        app_label = 'room'

    def __str__(self):
        return self.name

    def get_product_num(self):
        return len(self.products.all())

    def get_absolute_url(self, ancestors=None):
        return reverse('product:category',
                       kwargs={'path': self.get_full_path(ancestors),
                               'category_id': self.id})

    def get_full_path(self, ancestors=None):
        if not self.parent_id:
            return self.slug
        if not ancestors:
            ancestors = self.get_ancestors()
        nodes = [node for node in ancestors] + [self]
        return '/'.join([node.slug for node in nodes])

    def set_hidden_descendants(self, hidden):
        self.get_descendants().update(hidden=hidden)


@python_2_unicode_compatible
class RoomClass(models.Model):
    name = models.CharField(
        pgettext_lazy('Room class field', 'name'), max_length=128, unique=True)
    has_variants = models.BooleanField(
        pgettext_lazy('Room class field', 'has variants'), default=True)
    product_attributes = models.ManyToManyField(
        'RoomAttribute', related_name='rooms_class', blank=True,
        verbose_name=pgettext_lazy('Room class field',
                                   'product attributes'))
    variant_attributes = models.ManyToManyField(
        'RoomAttribute', related_name='room_variants_class', blank=True,
        verbose_name=pgettext_lazy('Room class field', 'variant attributes'))
    is_shipping_required = models.BooleanField(
        pgettext_lazy('Room class field', 'is shipping required'),
        default=False)

    class Meta:
        verbose_name = pgettext_lazy(
            'Room class model', 'room class')
        verbose_name_plural = pgettext_lazy(
            'Room class model', 'room classes')
        app_label = 'room'

    def __str__(self):
        return self.name

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)


class RoomTax(models.Model):
    tax_name = models.CharField(
        pgettext_lazy('Tax name', 'Tax name (optional)'),
        max_length=128, blank=True)   
    tax_label = models.CharField(
        pgettext_lazy('Label on invoices', 'Short text printed on invoices'),
        max_length=128, blank=True)
    tax = models.IntegerField(pgettext_lazy('Room Tax', 'tax %'), validators=[MinValueValidator(0)], unique=True, default=Decimal(0))

    def __str__(self):
        return self.tax_name + ' ' +str(self.tax)+' %'

    def get_tax(self):
        return self.tax


class RoomManager(models.Manager):

    def get_available_products(self):
        today = datetime.date.today()
        return self.get_queryset().filter(
            Q(available_on__lte=today) | Q(available_on__isnull=True))


@python_2_unicode_compatible
class RoomAmenity(models.Model):
    name = models.CharField(
        pgettext_lazy('Room amenity field', 'display name'),
        max_length=100, unique=True)

    class Meta:
        #ordering = ('slug', )
        verbose_name = pgettext_lazy('Room amenity model', 'room amenity')
        verbose_name_plural = pgettext_lazy('Room amenity model', 'room amenities')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Room(models.Model, ItemRange, index.Indexed):
    room_class = models.ForeignKey(
        RoomClass, related_name='room', null=True, blank=True,
        verbose_name=pgettext_lazy('Room field', 'product class'))
    product_tax = models.ForeignKey(
        RoomTax, related_name='room_tax', blank=True, null=True,
        verbose_name=pgettext_lazy('Room field', 'product class'))
    name = models.CharField(
        pgettext_lazy('Room field', 'name'), unique=True, max_length=128)
    floor = models.IntegerField(
        pgettext_lazy('Room field', 'flour'),
        validators=[MinValueValidator(0)], null=True, blank=True, default=Decimal(0))
    description = models.TextField(
        verbose_name=pgettext_lazy('Room field', 'description'), blank=True, null=True)
    categories = models.ManyToManyField(
        RoomCategory, verbose_name=pgettext_lazy('Room field', 'categories'),
        related_name='rooms_cat')
    amenities = models.ManyToManyField(
        RoomAmenity, verbose_name=pgettext_lazy('Room field', 'amenities'),
        related_name='rooms_amenities')
    price = PriceField(
        pgettext_lazy('Room field', 'price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12,
        validators=[MinValueValidator(0)], default=Decimal(0), decimal_places=2)
    available_on = models.DateTimeField(
        pgettext_lazy('Room field', 'available on'), blank=True, null=True)
    attributes = HStoreField(pgettext_lazy('Room field', 'attributes'),
                             default={})
    updated_at = models.DateTimeField(
        pgettext_lazy('Room field', 'updated at'), auto_now=True, null=True)
    is_booked = models.BooleanField(
        pgettext_lazy('Room field', 'is booked'), default=False)

    objects = RoomManager()

    search_fields = [
        index.SearchField('name', partial_match=True),
        index.SearchField('description'),
        index.FilterField('available_on')]

    class Meta:
        app_label = 'room'
        verbose_name = pgettext_lazy('Room model', 'product')
        verbose_name_plural = pgettext_lazy('Rooms model', 'room')

    def __iter__(self):
        if not hasattr(self, '__variants'):
            setattr(self, '__variants', self.variants.all())
        return iter(getattr(self, '__variants'))

    def __repr__(self):
        class_ = type(self)
        return '<%s.%s(pk=%r, name=%r)>' % (
            class_.__module__, class_.__name__, self.pk, self.name)

    def __str__(self):
        return self.name

    def get_first_image(self):
        first_image = self.images.first()

        if first_image:
            return first_image.image
        return None

    def get_attribute(self, pk):
        return self.attributes.get(smart_text(pk))

    def set_attribute(self, pk, value_pk):
        self.attributes[smart_text(pk)] = smart_text(value_pk)

    def get_nightly_price(self):
        return self.room_price.all().get().nightly.gross

    def get_daytime_price(self):
        return self.room_price.all().get().daytime.gross

    def get_daily_price(self):
        return self.room_price.all().get().daily.gross

    def get_weekly_price(self):
        return self.room_price.all().get().weekly.gross

    def get_monthly_price(self):
        return self.room_price.all().get().monthly.gross

    def get_price_range(self, discounts=None,  **kwargs):
        if not self.variants.exists():
            price = calculate_discounted_price(self, self.price, discounts,
                                               **kwargs)
            return PriceRange(price, price)
        else:
            return super(Room, self).get_price_range(
                discounts=discounts, **kwargs)


class Pricing(models.Model):
    room = models.ForeignKey(
        Room, related_name='room_price', blank=True, null=True,
        verbose_name=pgettext_lazy('Pricing field', 'room'))
    package = models.ForeignKey(
        Package, related_name='package_price', blank=True, null=True,
        verbose_name=pgettext_lazy('Pricing field', 'package'))
    daily = PriceField(
        pgettext_lazy('Pricing field', 'daily price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12,
        validators=[MinValueValidator(0)], default=Decimal(0), decimal_places=2)
    nightly = PriceField(
        pgettext_lazy('Pricing field', 'nightly price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12,
        validators=[MinValueValidator(0)], default=Decimal(0), decimal_places=2)
    daytime = PriceField(
        pgettext_lazy('Pricing field', 'daytime price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12,
        validators=[MinValueValidator(0)], default=Decimal(0), decimal_places=2)
    weekly = PriceField(
        pgettext_lazy('Pricing field', 'weekly price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12,
        validators=[MinValueValidator(0)], default=Decimal(0), decimal_places=2)
    monthly = PriceField(
        pgettext_lazy('Pricing field', 'monthly price'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12,
        validators=[MinValueValidator(0)], default=Decimal(0), decimal_places=2)

    class Meta:
        verbose_name = pgettext_lazy('RoomPricing model', 'pricing')
        verbose_name_plural = pgettext_lazy('RoomPricing model', 'pricing')
        app_label = 'room'

    def __str__(self):
        return str(self.room.name) + ' ' + str(self.daily)


class RoomVariantManager(models.Manager):

    def get_low_stock(self):
        today = datetime.date.today()
        return self.get_queryset().filter(stock__quantity__lte=F('low_stock_threshold'))


@python_2_unicode_compatible
class RoomVariant(models.Model, Item):
    sku = models.CharField(
        pgettext_lazy('Room variant field', 'SKU'), max_length=32, unique=True)
    name = models.CharField(
        pgettext_lazy('Room variant field', 'variant name'), max_length=100,
        blank=True)
    price_override = PriceField(
        pgettext_lazy('Room variant field', 'price override'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    wholesale_override = PriceField(
        pgettext_lazy('Room variant field', 'wholesale override'),
        currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2,
        blank=True, null=True)
    
    product = models.ForeignKey(Room, related_name='room_variants')
    attributes = HStoreField(
        pgettext_lazy('Room variant field', 'attributes'), default={})
    images = models.ManyToManyField(
        'RoomImage', through='VariantImage',
        verbose_name=pgettext_lazy('Room variant field', 'images'))
    low_stock_threshold = models.IntegerField(
        pgettext_lazy('Room variant field', 'low stock threshold'),
        validators=[MinValueValidator(0)], null=True, blank=True, default=Decimal(10))
    objects = RoomVariantManager()
    
    class Meta:
        app_label = 'room'
        verbose_name = pgettext_lazy('Room variant model', 'room variant')
        verbose_name_plural = pgettext_lazy('Room variant model', 'room variants')

    def __str__(self):
        return self.name or self.display_variant()

    def check_quantity(self, quantity):
        available_quantity = self.get_stock_quantity()
        if quantity > available_quantity:
            raise InsufficientStock(self)

    def get_stock_pk(self):
        stock_pk = self.stock.all().values('pk')
        if stock_pk.exists():
            for st in stock_pk:
                stock_pk = st['pk']
        else:
            stock_pk = 0        
        return stock_pk

    def get_stock_quantity(self):
        if not len(self.stock.all()):
            return 0
        return max([stock.quantity_available for stock in self.stock.all()])

    def get_price_per_item(self, discounts=None, **kwargs):
        price = self.price_override or self.product.price
        price = calculate_discounted_price(self.product, price, discounts,
                                           **kwargs)
        return price

    def get_total_price_cost(self):
        cost = self.get_cost_price() * self.get_stock_quantity()
        return cost

    def get_absolute_url(self):
        slug = self.product.get_slug()
        product_id = self.product.id
        return reverse('product:details',
                       kwargs={'slug': slug, 'product_id': product_id})

    def as_data(self):
        return {
            'product_name': str(self),
            'product_id': self.product.pk,
            'variant_id': self.pk,
            'unit_price': str(self.get_price_per_item().gross)}

    def is_shipping_required(self):
        return self.product.product_class.is_shipping_required

    def is_in_stock(self):
        return any(
            [stock.quantity_available > 0 for stock in self.stock.all()])

    def get_attribute(self, pk):
        return self.attributes.get(smart_text(pk))

    def set_attribute(self, pk, value_pk):
        self.attributes[smart_text(pk)] = smart_text(value_pk)

    def display_variant(self, attributes=None):
        if attributes is None:
            attributes = self.product.product_class.variant_attributes.all()
        values = get_attributes_display_map(self, attributes)
        if values:
            return ', '.join(
                [' %s' % ( smart_text(value))
                 for (key, value) in six.iteritems(values)])            
        else:
            return smart_text(self.sku)

    def display_product(self):
        return '%s (%s)' % (smart_text(self.product),
                            smart_text(self))

    def get_first_image(self):
        return self.product.get_first_image()

    def select_stockrecord(self, quantity=1):
        # By default selects stock with lowest cost price
        stock = filter(
            lambda stock: stock.quantity_available >= quantity,
            self.stock.all())
        stock = sorted(stock, key=lambda stock: stock.cost_price, reverse=True)
        if stock:
            return stock[0]

    def get_cost_price(self):
        stock = self.select_stockrecord()
        if stock:
            if stock.cost_price:
                return stock.cost_price
            else:
                return 0
        else:
            return 0

    def product_category(self):
        category = self.product.categories.first().name
        return category


@python_2_unicode_compatible
class RoomAttribute(models.Model):
    slug = models.SlugField(
        pgettext_lazy('Room attribute field', 'internal name'),
        max_length=50, unique=True)
    name = models.CharField(
        pgettext_lazy('Room attribute field', 'display name'),
        max_length=100, unique=True)

    class Meta:
        ordering = ('slug', )
        verbose_name = pgettext_lazy('Room attribute model', 'room attribute')
        verbose_name_plural = pgettext_lazy('Room attribute model', 'room attributes')

    def __str__(self):
        return self.name

    def get_formfield_name(self):
        return slugify('attribute-%s' % self.slug)

    def has_values(self):
        return self.values.exists()


@python_2_unicode_compatible
class VariantAttribute(models.Model):
    slug = models.SlugField(
        pgettext_lazy('Variant attribute field', 'internal name'),
        max_length=50, unique=True)
    name = models.CharField(
        pgettext_lazy('Variant attribute field', 'display name'),
        max_length=100, unique=True)

    class Meta:
        ordering = ('slug', )
        verbose_name = pgettext_lazy('Variant attribute model', 'variant attribute')
        verbose_name_plural = pgettext_lazy('Variant attribute model', 'variant attributes')

    def __str__(self):
        return self.name

    def get_formfield_name(self):
        return slugify('variant-attribute-%s' % self.slug)

    def has_values(self):
        return self.values.exists()


@python_2_unicode_compatible
class AttributeChoiceValue(models.Model):
    name = models.CharField(
        pgettext_lazy('Attribute choice value field', 'display name'),
        max_length=100)
    slug = models.SlugField()
    color = models.CharField(
        pgettext_lazy('Attribute choice value field', 'color'),
        max_length=7,
        validators=[RegexValidator('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')],
        blank=True)
    attribute = models.ForeignKey(RoomAttribute, related_name='attribute_values')

    class Meta:
        unique_together = ('name', 'attribute')
        verbose_name = pgettext_lazy(
            'Attribute choice value model',
            'attribute choices value')
        verbose_name_plural = pgettext_lazy(
            'Attribute choice value model',
            'attribute choices values')

    def __str__(self):
        return self.name


class ImageManager(models.Manager):
    def first(self):
        try:
            return self.get_queryset()[0]
        except IndexError:
            pass


class RoomImage(models.Model):
    room = models.ForeignKey(
        Room, related_name='room_images',
        verbose_name=pgettext_lazy('Room image field', 'product'))
    image = VersatileImageField(
        upload_to='rooms', ppoi_field='ppoi', blank=False,
        verbose_name=pgettext_lazy('Room image field', 'image'))
    ppoi = PPOIField(verbose_name=pgettext_lazy('Room image field', 'ppoi'))
    alt = models.CharField(
        pgettext_lazy('Room image field', 'short description'),
        max_length=128, blank=True)
    order = models.PositiveIntegerField(
        pgettext_lazy('Room image field', 'order'),
        editable=False)

    objects = ImageManager()

    class Meta:
        ordering = ('order', )
        app_label = 'room'
        verbose_name = pgettext_lazy('Room image model', 'room image')
        verbose_name_plural = pgettext_lazy('Room image model', 'room images')

    def get_ordering_queryset(self):
        return self.product.images.all()

    def save(self, *args, **kwargs):
        if self.order is None:
            qs = self.get_ordering_queryset()
            existing_max = qs.aggregate(Max('order'))
            existing_max = existing_max.get('order__max')
            self.order = 0 if existing_max is None else existing_max + 1
        super(RoomImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        qs = self.get_ordering_queryset()
        qs.filter(order__gt=self.order).update(order=F('order') - 1)
        super(RoomImage, self).delete(*args, **kwargs)


class VariantImage(models.Model):
    variant = models.ForeignKey(
        'RoomVariant', related_name='variant_room_images',
        verbose_name=pgettext_lazy('Variant image field', 'variant'))
    image = models.ForeignKey(
        RoomImage, related_name='variant_room_images',
        verbose_name=pgettext_lazy('Variant image field', 'image'))

    class Meta:
        verbose_name = pgettext_lazy(
            'Variant image model', 'variant image')
        verbose_name_plural = pgettext_lazy('Variant image model', 'variant images')