from django.urls import path

from cinema.views import MovieListView


urlpatterns = [
    path("movies/", MovieListView.as_view(), name="movie-list"),
]
