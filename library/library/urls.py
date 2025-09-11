from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,    # POST /api/token/        -> access + refresh
    TokenRefreshView,       # POST /api/token/refresh -> новый access (и refresh если ROTATE)
    TokenVerifyView,        # POST /api/token/verify  -> проверить access/refresh
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("books/", include("books.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
