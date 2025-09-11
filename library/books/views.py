from rest_framework import viewsets, filters

from . import permissions
from .models import Book, Author
from .permissions import AuthorPermission
from .serializers import BookSerializer, AuthorSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class BookViewSet(viewsets.ModelViewSet):
    """
    Полный CRUD для Book:
    - GET /books/         список (с поиском и сортировкой)
    - POST /books/        создать
    - GET /books/{id}/    получить
    - PUT/PATCH /books/{id}/ обновить
    - DELETE /books/{id}/ удалить
    """
    queryset = Book.objects.all().order_by("id")
    serializer_class = BookSerializer
    permission_classes = []

    # Поиск и сортировка: ?search=alfa, ?ordering=title или ?ordering=-id
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["id", "title"]


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, AuthorPermission]
    serializer_class = AuthorSerializer
    queryset = Author.objects.filter(is_active=True).order_by("name")

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        elif self.action == "retrieve":
            return [IsAuthenticated(), AuthorPermission()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
