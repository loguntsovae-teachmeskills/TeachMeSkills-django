from django.contrib import admin

from bike.models import Bike


from django.contrib import messages

def set_as_available(modeladmin, request, queryset):
    already_available = queryset.filter(available=True).count()
    not_available = queryset.filter(available=False).count()

    # Обновляем только те, что были недоступны
    queryset.filter(available=False).update(available=True)

    # Сообщение с деталями
    if not_available > 0:
        modeladmin.message_user(
            request,
            f"✅ {not_available} объектов установлены как доступные.",
            messages.SUCCESS,
        )
    if already_available > 0:
        modeladmin.message_user(
            request,
            f"ℹ️ {already_available} объектов уже были доступны.",
            messages.INFO,
        )


@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    actions = [set_as_available]
    list_display = ("category", "name", "brand", "display_station", "available", "electricity")
    list_filter = (
        "available",
        "electricity",
        "station",
        "brand",
        "name",
    )
    list_editable = ("available", "electricity")
    search_fields = ("name", "brand", "station__name")
    ordering = ("-name",)
    readonly_fields = (
        "created_at", "updated_at", "deleted_at", "electricity",
    )
    fieldsets = (
        (None, {"fields": ("category", "name", "brand", "station")}),
        ("Основная информация", {"fields": ("available", "electricity")}),
        ("Даты", {"fields": ("created_at", "updated_at", "deleted_at")}),
    )

    def display_station(self, obj):
        return f"{obj.station.name}-{obj.station.address}"
    display_station.short_description = "Station"
