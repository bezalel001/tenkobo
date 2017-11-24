from rest_framework import generics
from rest_framework.response import Response 
from rest_framework.reverse import reverse
from rest_framework_gis.filters import DistanceToPointFilter

from .models import FuelStation, Category, Product, Location
from .serializers import FuelStationSerializer, CategorySerializer, ProductSerializer
from .serializers import LocationSerializer

class ApiRoot(generics.GenericAPIView):
	name = 'api-root'

	def get(self, request, *args, **kwargs):
		return Response({
			'fuel-stations': reverse(FuelStationList.name, request=request),
			'categories': reverse(CategoryList.name, request=request),
			'products': reverse(ProductList.name, request=request),
			'locations': reverse(LocationList.name, request=request)
			})

class FuelStationList(generics.ListCreateAPIView):
	queryset = FuelStation.objects.all()
	serializer_class = FuelStationSerializer
	distance_filter_field = 'geometry'
	filter_backends = (DistanceToPointFilter, )
	bbox_filter_include_overlapping = True # Optional
	name = 'fuelstation-list'


class FuelStationDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = FuelStation.objects.all()
	serializer_class = FuelStationSerializer
	name = 'fuelstation-detail'


class CategoryList(generics.ListCreateAPIView):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	name = 'category-list'


class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	name = 'category-detail'


class ProductList(generics.ListCreateAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	name = 'product-list'


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	name = 'product-detail'



class LocationList(generics.ListCreateAPIView):
	queryset = Location.objects.all()
	serializer_class = LocationSerializer
	name = 'location-list'



class LocationDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Location.objects.all()
	serializer_class = LocationSerializer
	name = 'location-detail'

