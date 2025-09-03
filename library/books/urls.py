from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet

# создаем роутер и регистрируем вьюсет
router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'authors', AuthorViewSet)

urlpatterns = [
    path("", include(router.urls)),
]


# localhost:8000/books/books/
# localhost:8000/books/books/<int:id>/

# localhost:8000/books/author/
# localhost:8000/books/authors/<int:id>/

