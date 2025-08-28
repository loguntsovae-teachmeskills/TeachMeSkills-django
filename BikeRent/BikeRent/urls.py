from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("bikes/", include("bike.urls")),
    path("rents/", include("rent.urls")),
]
