import json

from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from bike.models import Station


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
