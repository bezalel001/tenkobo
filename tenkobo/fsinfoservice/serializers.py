import geocoder
import json

from rest_framework import serializers
from django.contrib.gis.geos import Point, GEOSGeometry
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField

from .models import Location, FuelStation, Category, Product

class LocationSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """
    point = GeometrySerializerMethodField()

    def get_point(self, obj):
    	return Point(obj.point[0], obj.point[1])

    class Meta:
        model = Location
        geo_field = "point"

        fields = ('id', 'street', 'city', 'state')

    # def get_point(self, obj):
    # 	g = geocoder.google(obj)
    # 	return g.latlng


class FuelStationSerializer(serializers.HyperlinkedModelSerializer):
	products = serializers.HyperlinkedRelatedField(
		many=True,
		read_only=True,
		view_name='product-detail')
	location = LocationSerializer(required=True)

	class Meta:
		model = FuelStation
		fields = (
			'url', 'pk', 'name', 'description', 
			'products', 'location', 'is_operational', 
			'is_featured', 'is_open', 'updated_at', 'hidden')



	def create(self, validated_data):
		location_data = validated_data.pop('location')
		location = Location.objects.create(**location_data)		
		return FuelStation.objects.create(
			location=location, 
			**validated_data)


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



