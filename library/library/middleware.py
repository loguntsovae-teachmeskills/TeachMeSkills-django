import datetime
import time
import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)

class FirstMiddleware:
    """
    Middleware, которая стоит в начале списка.
    Просто печатает, что запрос пришёл.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"[{datetime.datetime.now()}] 🚀 Первый middleware: пришёл запрос {request.method} {request.path}")
        response = self.get_response(request)
        return response


class LastMiddleware:
    """
    Middleware, которая стоит в конце списка.
    Добавляет заголовок и пишет, что ответ ушёл.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.foo = "I'm FOO"

        response = self.get_response(request)
        print(f"[{datetime.datetime.now()}] ✅ Последний middleware: ответ сформирован")
        response["X-From-Last-Middleware"] = "Yes, I'm the last!"
        return response


class RequestTimingMiddleware:
    """
    Измеряет время обработки запроса и:
      - пишет в логи
      - добавляет заголовок X-Process-Time (в секундах)
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        logger.info("HTTP %s %s -> %s in %.4fs",
                    request.method, request.path, getattr(response, "status_code", "?"), duration)
        return response