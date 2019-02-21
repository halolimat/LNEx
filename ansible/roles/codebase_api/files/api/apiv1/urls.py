from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
  #url(r'^LNEx/register', views.LNExRegister, name='LNExRegister'),
  url(r'^LNEx/initZone', views.LNExInit, name='LNExInit'),
  url(r'^LNEx/destroyZone', views.LNExDestroy, name='LNExDestroy'),
  #url(r'^LNEx/extract', views.LNExExtract, name='LNExExtract'),
  url(r'^LNEx/results', views.LNExResults, name='LNExResults'),
  url(r'^LNEx/geoInfo', views.LNExGeoInfo, name='LNExGeoInfo'),
  url(r'^LNEx/bulkExtract', views.LNExBulkExtract, name='LNExBulkExtract'),
  url(r'^LNEx/photonID', views.LNExPhotonID, name='LNExPhotonID'),
  url(r'^LNEx/zoneReady', views.LNExZoneReady, name='LNExZoneReady'),
  url(r'^LNEx/fullBulkExtract', views.LNExFullBulkExtract, name='LNExFullBulkExtract')
]