import datetime
import geocoder, json
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import pgettext_lazy as _
from django.db.models import F, Q, Max
from django.contrib.gis.geos import GEOSGeometry

from django_prices.models import Price, PriceField
from geoposition.fields import GeopositionField


class Location(gis_models.Model):
    '''
    A model which holds information about a particular location
    '''
    street = gis_models.CharField(max_length=255)
    city = gis_models.CharField(max_length=100)
    state = gis_models.CharField(max_length=100)
    point = gis_models.PointField(null=True, spatial_index=True, geography=True)

    def get_lat_lng(self):
    	geojson = self.point.json
    	coordinates = json.loads(geojson).get('coordinates')
    	return [coordinates[1], coordinates[0]]

    def get_point(self):
    	return '{0}, {1}, {2}'.format(self.street, self.city, self.state)

    def save(self, *args, **kwargs):
        goecoded = geocoder.google(self)
        self.point = GEOSGeometry(json.dumps(goecoded.geometry))
        super(Location, self).save(*args, **kwargs)


    def __str__(self):
    	return '{0}, {1}, {2}'.format(self.street, self.city, self.state)


class FuelStationManager(models.Manager):

    def get_operational_fuel_stations(self):
        today = datetime.date.today()
        return self.get_queryset().filter(
        	Q(updated_at__lte=today) | Q(updated_at__isnull=True)).filter(
            is_open=True)


class FuelStation(models.Model):
	name = models.CharField(_('Fuel station field', 'name'), max_length=200)
	slug = models.SlugField(_('Fuel station field', 'slug'), max_length=200)
	description = models.TextField(_('Fuel station field', 'description'), blank=True)
	hidden = models.BooleanField(_('Fuel station field', 'hidden'), default=False)
	is_operational = models.BooleanField(_('Fuel station field', 'is operational'), default=False)
	is_featured = models.BooleanField(_('Fuel station field', 'is featured'), default=False)
	is_open = models.BooleanField(_('Fuel station field', 'is featured'), default=False)
	updated_at = models.DateTimeField(_('Fuel station field', 'updated at'), auto_now=True, null=True)
	location = models.OneToOneField(Location)
	position = GeopositionField()


	class Meta:
		ordering = ('-updated_at', 'position', 'name', 'location__point')

	def __str__(self):
		return self.name



class Category(models.Model): # eg 1. Industrial fuel, 2. Chemical Products
    name = models.CharField(_('Category field', 'name'), max_length=200)
    slug = models.SlugField(_('Category field', 'slug'), max_length=200)
    description = models.TextField(_('Category field', 'description'), blank=True)
    hidden = models.BooleanField(_('Category field', 'hidden'), default=False)

    class Meta:
        verbose_name = _('Category model', 'category')
        verbose_name_plural = _('Category model', 'categories')
        app_label = 'fsinfoservice'
        # permissions = ('vew_category', _('Permission description', 'Can view categories'),
        #     ('edit_category', _('Permission description', 'Can edit categories')))

    def __str__(self):
        return self.name


class ProductManager(models.Manager):

    def get_available_products(self):
        today = datetime.date.today()
        return self.get_queryset().filter(Q(available_on__lte=today) | Q(available_on__isnull=True)).filter(
            is_available=True)


class Product(models.Model):
    fuel_station = models.ForeignKey(FuelStation, verbose_name=_('Product field', 'fuel station'), related_name='products')
    name = models.CharField(_('Product field', 'name'), max_length=200)
    description = models.TextField(verbose_name=_('Product field', 'description'))
    category = models.ForeignKey(Category, verbose_name=_('Product field', 'category'), related_name='products')
    price = PriceField(_('Product field', 'price'), currency=settings.DEFAULT_CURRENCY, max_digits=12, decimal_places=2)
    available_on = models.DateField(_('Product field', 'available on'), blank=True, null=True)
    is_available  = models.BooleanField(_('Product field', 'is available'), default=True)    
    updated_at = models.DateTimeField(_('Product field', 'updated at'), auto_now=True, null=True)
    is_featured = models.BooleanField(_('Product field', 'is featured'), default=False)

    objects = ProductManager()

    class Meta:
        app_label ='fsinfoservice'
        verbose_name = _('Product model', 'product')
        verbose_name_plural  = _('Product model', 'products')
        # permissions = (('view_product', _('Permission description', 'Can view product')),
        #     ('edit_product', _('Permission description', 'Can edit products')))

    def __str__(self):
        return self.name


class OpeningHours(models.Model):
	WEEKDAYS = [
		(1, _('Monday', 'monday')),
		(2, _('Tuesday', 'tuesday')),
		(3, _('Wednesday', 'wednesday')),
		(4, _('Thursday', 'thursday')),
		(5, _('Friday', 'friday')),
		(6, _('Saturday', 'saturday')),
		(7, _('Sunday', 'sunday')),
	]
	store = models.ForeignKey(
	FuelStation, related_name='opening_hours'
	)
	weekday = models.IntegerField(
	choices=WEEKDAYS,
	unique=True
	)
	from_hour = models.TimeField(_('Fuel station field', 'open at'))
	to_hour = models.TimeField(_('Fueld station field', 'close at'))

