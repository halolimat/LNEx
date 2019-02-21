from django.conf.urls import include, url
from django.contrib import admin
from django.http import HttpResponse
import json


def stdmsg(request):
  msg = {
    "DisasterRecord": "0.0.1",
    "LNEx": "0.0.1",
    "DSapi": "0.0.1"
  }
  return HttpResponse(json.dumps(msg,indent=2,sort_keys=True), content_type="application/json")

def errmsg(request):
  msg = {"error": "invalid url"}
  return HttpResponse(json.dumps(msg,indent=2,sort_keys=True), content_type="application/json")

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', stdmsg),
    url(r'^apiv1/', include('apiv1.urls')),
    url(r'', errmsg)
]