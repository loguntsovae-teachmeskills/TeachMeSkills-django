from django.contrib import admin

from .models import Bike, Station


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "brand")
    list_filter = (
        "available",
        "electricity",
    )


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    pass
