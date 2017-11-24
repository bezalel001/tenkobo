from django.contrib.gis.geos import Point

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Location, FuelStation, Category, Product


class FuelStationSerializer(serializers.HyperlinkedModelSerializer):
	products = serializers.HyperlinkedRelatedField(
		many=True,
		read_only=True,
		view_name='product-detail')

	class Meta:
		model = FuelStation
		fields = (
			'url', 'pk', 'name', 'description', 
			'products', 'location', 'position',
			'is_operational', 'is_featured', 'is_open', 
			'hidden', 'updated_at')


class CategorySerializer(serializers.HyperlinkedModelSerializer):
	products = serializers.HyperlinkedRelatedField(
		many=True,
		read_only=True,
		view_name='product-detail')

	class Meta:
		model = Category
		fields = (
			'url', 'pk', 'name', 'products',
			'description', 'hidden')


class ProductSerializer(serializers.HyperlinkedModelSerializer):
	# We want to display the product category's name instead of the id
	category = serializers.SlugRelatedField(queryset=Category.objects.all(),
		slug_field='name')
	fuel_station = serializers.SlugRelatedField(queryset=FuelStation.objects.all(),
		slug_field='name')

	class Meta:
		model = Product
		fields = (
			'url', 'pk', 'name', 
			'description', 'category', 'fuel_station', 
			'price', 'available_on',
			'is_available', 'is_featured',
			'updated_at')



class LocationSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Location
        geo_field = "point"

        # you can also explicitly declare which fields you want to include
        # as with a ModelSerializer.
        fields = ('id', 'street', 'city', 'state')