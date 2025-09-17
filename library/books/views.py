from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
import time
from .models import Book, Author
from .permissions import AuthorPermission
from .serializers import BookSerializer, AuthorSerializer

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Book, Author
from .permissions import AuthorPermission
from .serializers import BookSerializer, AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    Полный CRUD для Book.
    Здесь покажем кэширование списка книг через @cache_page.
    """
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = []

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["id", "title"]

    # @method_decorator(cache_page(5))
    def list(self, request, *args, **kwargs):
        if hasattr(cache, "_cache"):
            print("SUCCESS")
            for k in cache._cache.keys():
                print(k)
        else:
            print("Текущий backend не поддерживает прямой доступ к ключам")
        return super().list(request, *args, **kwargs)


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ReadOnly для авторов.
    Здесь пример кэширования с учётом авторизации.
    """
    permission_classes = [IsAuthenticated, AuthorPermission]
    serializer_class = AuthorSerializer
    queryset = Author.objects.filter(is_active=True).order_by("name")

    def get_queryset(self):
        if self.action == "list":
            return Author.objects.all()
        if self.action == "retrieve":
            return Author.objects.filter(is_active=True)
        queryset = self.queryset
        return queryset

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        elif self.action == "retrieve":
            return [IsAuthenticated(), AuthorPermission()]

    def list(self, request, *args, **kwargs):
        """
        Персональный кэш: у каждого пользователя свой ключ.
        Пример ключа в Redis: author_list_user_42
        """
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        # Ключ кэша «на пользователя»
        cache_key = f"author_list_user_{user.id}"
        data = cache.get(cache_key)
        if data is not None:
            return Response(data)

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Храним 120 секунд. В проде можно прикрутить версионирование/инвалидацию по событиям.
        cache.set(cache_key, data, timeout=120)
        return Response(data)

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization"))
    def retrieve(self, request, *args, **kwargs):
        time.sleep(1)
        return super().retrieve(request, *args, **kwargs)