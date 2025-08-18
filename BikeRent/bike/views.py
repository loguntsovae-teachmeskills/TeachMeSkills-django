import json

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from .models import Bike, Station


@method_decorator(csrf_exempt, name="dispatch")
class BikeView(View):
    # localhost:8000/bikes/bikes/
    def get(self, request: HttpRequest):
        """Список всех велосипедов с пагинацией через Paginator"""
        try:
            page_number = int(request.GET.get("page", 1))
            per_page = int(request.GET.get("per_page", 20))
        except ValueError:
            return JsonResponse(
                {"error": "page и per_page должны быть числами"}, status=400
            )

        qs = (
            Bike.objects.all()
            .values(
                "id",
                "name",
                "brand",
                "category",
                "electricity",
                "colour",
                "available",
                "station__name",
            )
            .order_by("id")
        )

        paginator = Paginator(qs, per_page)

        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        data = {
            "count": paginator.count,  # общее число объектов
            "num_pages": paginator.num_pages,  # всего страниц
            "page": page_obj.number,  # текущая страница
            "per_page": per_page,  # размер страницы
            "results": list(page_obj.object_list),
        }

        return JsonResponse(data, safe=False)

    def post(self, request: HttpRequest):
        """Создание нового велосипеда"""
        try:
            data = json.loads(request.body)
            station = Station.objects.get(id=data["station_id"])
            bike = Bike.objects.create(
                name=data.get("name"),
                brand=data["brand"],
                category=data.get("category"),
                electricity=data.get("electricity", False),
                colour=data["colour"],
                available=data.get("available", True),
                station=station,
                comments=data.get("comments"),
            )
            return JsonResponse({"id": bike.id, "message": "Bike created"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def bike_to_dict(obj: Bike) -> dict:
    return {
        "id": obj.id,
        "category": obj.category,
        "name": obj.name,
        "brand": obj.brand,
        "electricity": obj.electricity,
        "colour": obj.colour,
        "available": obj.available,
        "comments": obj.comments,
        "preview": obj.preview.url if obj.preview else None,
        "station": obj.station_id,
    }


@method_decorator(csrf_exempt, name="dispatch")
class BikeDetailView(View):
    """Retrieve / Patch / Delete для Bike"""

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        bike = get_object_or_404(Bike, pk=pk)
        return JsonResponse(bike_to_dict(bike), status=200)

    def patch(self, request: HttpRequest, pk: int) -> HttpResponse:
        bike = get_object_or_404(Bike, pk=pk)
        try:
            data = json.loads(request.body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        updatable_fields = [
            "category",
            "name",
            "brand",
            "electricity",
            "colour",
            "comments",
        ]
        for field in updatable_fields:
            if field in data:
                setattr(bike, field, data[field])

        if "station" in data:
            station = get_object_or_404(Station, pk=data["station"])
            setattr(bike, "station", station)

        bike.save()
        return JsonResponse(bike_to_dict(bike), status=200)

    def delete(self, request: HttpRequest, pk: int) -> HttpResponse:
        bike = get_object_or_404(Bike, pk=pk)
        bike.delete()
        return JsonResponse({"status": "deleted"}, status=204, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class StationView(View):
    # localhost:8000/bikes/stations/
    def get(self, request: HttpRequest):
        """Список всех станций"""
        stations = Station.objects.all().values("id", "name", "address", "capacity")
        return JsonResponse(list(stations), safe=False)

    def post(self, request: HttpRequest):
        """Создание новой станции"""
        try:
            data = json.loads(request.body)
            station = Station.objects.create(
                name=data["name"],
                address=data["address"],
                capacity=data.get("capacity", 0),
            )
            return JsonResponse(
                {"id": station.id, "message": "Station created"}, status=201
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
