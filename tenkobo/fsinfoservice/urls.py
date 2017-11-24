from django.conf.urls import url 


from fsinfoservice import views

urlpatterns = [
    
    url(r'^$', views.ApiRoot.as_view(), name=views.ApiRoot.name),
    url(r'^fuel-stations/$', views.FuelStationList.as_view(),
    	name=views.FuelStationList.name),
    url(r'^fuel-stations/(?P<pk>[0-9]+)/$', views.FuelStationDetail.as_view(),
    	name=views.FuelStationDetail.name),
    url(r'^product-categories/$', views.CategoryList.as_view(),
    	name=views.CategoryList.name),
    url(r'^product-categories/(?P<pk>[0-9]+)/$', views.CategoryDetail.as_view(),
    	name=views.CategoryDetail.name),
    url(r'^products/$', views.ProductList.as_view(),
    	name=views.ProductList.name),
    url(r'^products/(?P<pk>[0-9]+)/$', views.ProductDetail.as_view(),
    	name=views.ProductDetail.name),  
    url(r'^fuel-station-locations/$', views.LocationList.as_view(),
        name=views.LocationList.name),
    url(r'^fuel-station-locations/(?P<pk>[0-9]+)/$', views.LocationDetail.as_view(),
        name=views.LocationDetail.name),  
]