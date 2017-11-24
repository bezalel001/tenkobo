from __future__ import unicode_literals

import datetime

from django.conf import settings
from django.db import models
from django.db.models import F, Q, Max
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import pgettext_lazy as _
from django.contrib.postgres.fields import HStoreField

from django_prices.models import Price, PriceField
from mptt.models import MPTTModel
from mptt.managers import TreeManager
from satchless.item import InsufficientStock, Item, ItemRange
from versatileimagefield.fields import VersatileImageField


@python_2_unicode_compatible
class Category(MPTTModel): # eg 1. Industrial fuel, 2. Chemical Products
    name = models.CharField(_('Category field', 'name'), max_length=200)
    slug = models.SlugField(_('Category field', 'slug'), max_length=200)
    description = models.TextField(_('Category field', 'description'), blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children',
     verbose_name=_('Category field', 'parent'))
    hidden = models.BooleanField(_('Category field', 'hidden'), default=False)

    objects = models.Manager()
    tree = TreeManager()

    class Meta:
        verbose_name = _('Category model', 'category')
        verbose_name_plural = _('Category model', 'categories')
        app_label = 'product'
        permissions = ('vew_category', _('Permission description', 'Can view categories'),
            ('edit_category', _('Permission description', 'Can edit categories')))

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ProductType(models.Model):
    name = models.CharField(_('Product type field', 'name'), max_length=200)
    has_variants = models.BooleanField(_('Product type field', 'has variants'), default=True) # different volumes, weight
    product_attributes = models.ManyToManyField('ProductAttribute', related_name='product_type', blank=True,
        verbose_name=_('Product type field', 'product attributes')) # attributes shared by all products of the same  type
    variant_atttributes = models.ManyToManyField('ProductVariant', related_name='product_type', blank=True,
        verbose_name=_('Product type field', 'variant attributes')) # attributes that distingush products of the same type
    is_shipping_required = models.BooleanField(_('Product type field', 'is shipping required'), default=True)

    class Meta:
        verbose_name = _('Product type model', 'product type')
        verbose_name_plural = _('Product type model', 'product types')
        app_label = 'product'

    def __str__(self):
        return self.name


class ProductManager(models.Manager):

    def get_available_products(self):
        today = datetime.date.today()
        return self.get_queryset().filter(Q(available_on__lte=today) | Q(available_on__isnull=True)).filter(
            is_published=True)


@python_2_unicode_compatible
class Product(models.Model, ItemRange):
    product_type = models.ForeignKey(ProductType, related_name='products',
     verbose_name=_('Product field', 'product type')) # this type of product
    name = models.CharField(_('Product field', 'name'), max_length=200)
    description = models.TextField(verbose_name=_('Product field', 'description'))
    categories = models.ManyToManyField(Category, verbose_name=_('Product field', 'categories'), related_name='products')
    price = PriceField(_('Product field', 'price'), currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2)
    available_on = models.DateField(_('Product field', 'available on'), blank=True, null=True)
    is_published  = models.BooleanField(_('Product field', 'is published'), default=True)
    attributes = HStoreField(_('Product field', 'attributes'), default={})
    updated_at = models.DateTimeField(_('Product field', 'updated at'), auto_now=True, null=True)
    is_featured = models.BooleanField(_('Product field', 'is featured'), default=False)

    objects = ProductManager()

    # search_fields = [
    #     index.SearchField('name', partial_match=True),
    #     index.SearchField('description'),
    #     index.FilterField('available_on'),
    #     index.FilterField('is_published')]

    class Meta:
        app_label ='product'
        verbose_name = _('Product model', 'product')
        verbose_name_plural  = _('Product model', 'products')
        permissions = (('view_product', _('Permission description', 'Can view product')),
            ('edit_product', _('Permission description', 'Can edit products')))

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ProductVariant(models.Model, Item):
    code = models.CharField(_('Product variant field', 'code'), max_length=32, unique=True)
    namd = models.CharField(_('Product variant field', 'namd'), max_length=128, blank=True)
    price_override = PriceField(_('Product variant field', 'price override'),
     currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2, blank=True, null=True)
    product = models.ForeignKey(Product, related_name='variants')
    attributes  = HStoreField(_('Product variant field', 'attributes'), default={})
    images = models.ManyToManyField('ProductImage', through='VariantImage', 
        verbose_name=_('Product variant field', 'images'))

    class Meta:
        app_label = 'products'
        verbose_name = _('Product variant model', 'product variant')
        verbose_name_plural = _('Product variant model', 'product variants')

    def __str__(self):
        return self.name or self.display_variant()


@python_2_unicode_compatible
class StockLocation(models.Model):
    name = models.CharField(_('Stock location field', 'location'), max_length=128)

    class Meta:
        permissions = (('vew_stock_location', _('Permission description', 'Can view stock location')),
            ('edit_stock_location', _('Permission description', 'Can edit stock location')))

    def __str__(self):
        return self.name


class StockManager(models.Manager):

    def allocate_stock(self, stock, quantity):
        stock.quantity_allocated = F('quantity_allocated') + quantity
        stock.save(update_fields=['quantity_allocated'])

    def deallocate_stock(self, stock, quantity):
        stock.quantity_allocated = F('quantity_allocated') - quantity
        stock.save(update_fields=['quantity_allocated'])

    def decrease_stock(self, stock, quantity):
        stock.quantity = F('quantity') - quantity
        stock.quantity_allocated = F('quantity_allocated') - quantity
        stock.save(update_fields=['quantity', 'quantity_allocated'])


@python_2_unicode_compatible
class Stock(models.Model):
    variant = models.ForeignKey(ProductType, related_name='stock', verbose_name=_('Stock item field', 'variant'))
    location = models.ForeignKey(StockLocation, null=True)
    quantity = models.IntegerField(_('Stock item field', 'quantity'), validators=[MinValueValidator(0)], default=Decimal(1))
    quantity_allocated = models.IntegerField(_('Stock item field', 'allocated quantity'),
     validators=[MinValueValidator(0)], default=Decimal(0))
    cost_price = PriceField(_('Stock item field', 'cost price'), currency=settings.DEFAULT_CURRENCY, 
        max_digits=12, decimal_places=2, blank=True, null=True)

    objects = StockManager()

    class Meta:
        app_label = 'product'
        unique_together = ('variant', 'location')

    def __str__(self):
        return '%s - %s' % (self.variant.name, self.location)

    @property
    def quantity_available(self):
        return max(self.quantity - self.quantity_allocated, 0)


@python_2_unicode_compatible
class ProductAttribute(models.Model):
    slug = models.SlugField(_('Product attribute field', 'internal name'), max_length=50, unique=True)
    name = models.CharField(_('Product attribute field', 'display name'), max_length=100)

    class Meta:
        ordering = ('slug', )
        verbose_name = _('Product attribute model', 'product attribute')
        verbose_name_plural = _('Product attribute model', 'product attributes')

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class AttributeChoiceValue(models.Model):
    name = models.CharField(_('Attribute choice value field', 'display name'), max_length=100)
    slug = models.SlugField()
    volume = models.DecimalField(_('Attribute choice value field', 'volume'), max_digits=12, decimal_places=2)
    attribute = models.ForeignKey(ProductAttribute, related_name='values')

    class Meta:
        unique_together = ('name', 'attribute')
        verbose_name = _('Attribute choice value model', 'attribute choices value')
        verbose_name_plural = _('Attribute choice value model', 'attribute choices values')

    def __str__(self):
        return self.name

class ImageManager(models.Manager):

    def first(self):
        try:
            return self.get_queryset()[0]
        except IndexError:
            pass 


class ProductImage(model.Model):
    product = models.ForeignKey(Product, related_name='images',
        verbose_name=_('Product image field', 'product'))
    image = VersatileImageField(upload_to='products', ppoi_field='ppoi', blank=False,
        verbose_name=_('Product image field', 'image'))
    ppoi =PPOIField(verbose_name=_('Product image field', 'ppoi'))
    alt = models.CharField(_('Product image field', 'short description'), max_length=200, blank=True)
    order = models.PositiveIntegerField(_('Product image field', 'order'), editable=False)

    objects = ImageManager()

    class Meta:
        ordering = ('order', )
        app_label = 'product'
        verbose_name = _('Product image model', 'product image')
        verbose_name_plural = _('Product image model', 'product images')

    def get_ordering_queryset(self):
        return self.product.images.all()

    def save(self, *args, **kwargs):
        if self.order is None:
            qs = self.get_ordering_queryset()
            existing_max = qs.aggregate(Max('order'))
            existing_max = existing_max.get('order__max')
            self.order = 0 if existing_max is None else existing_max + 1
        super(ProductImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        qs = self.get_ordering_queryset()
        qs.filter(order__gt=self.order).update(order=F('order') - 1)
        super(ProductImage, self).delete(*args, **kwargs)


class VariantImage(models.Model):
    variant = models.ForeignKey(ProductVariant, related_name='variant_images',
        verbose_name=_('Variant image field', 'variant'))
    image = models.ForeignKey(ProductImage, related_name='variant_images', 
        verbose_name=_('Variant image field', 'image'))

    class Meta:
        verbose_name = _('Variant image model', 'variant image')
        verbose_name_plural = _('Variant image model', 'variant images')



