# cinema/admin.py
from django.contrib import admin
from cinema.models import Schedule, Movie, Genre, Actor, Director


# ==============================
# Inlines
# ==============================
class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0
    fields = ("movie_start", "price")
    ordering = ("movie_start",)
    verbose_name = "Сеанс"
    verbose_name_plural = "Сеансы"


class MovieActorInline(admin.TabularInline):
    """
    Инлайн для связи Movie <-> Actor через скрытую through-модель.
    Используется в MovieAdmin и ActorAdmin.
    """
    model = Movie.actors.through
    extra = 1
    # При желании можно показать только актёра, а movie скрыть — но Django сам подставит текущий объект
    autocomplete_fields = ("actor",)
    verbose_name = "Актёр"
    verbose_name_plural = "Актёры"


class MovieDirectorInline(admin.TabularInline):
    model = Movie.directors.through
    extra = 1
    autocomplete_fields = ("director",)
    verbose_name = "Режиссёр"
    verbose_name_plural = "Режиссёры"


class MovieGenreInline(admin.TabularInline):
    model = Movie.genres.through
    extra = 1
    autocomplete_fields = ("genre",)
    verbose_name = "Жанр"
    verbose_name_plural = "Жанры"


# ==============================
# ModelAdmins
# ==============================
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("name", "year")
    list_filter = ("year", "genres")
    search_fields = ("name",)
    ordering = ("-year", "name")
    # Редактируем M2M через инлайны, чтобы не дублировать виджеты справа
    exclude = ("genres", "actors", "directors")

    inlines = [
        ScheduleInline,
        MovieActorInline,
        MovieDirectorInline,
        MovieGenreInline,
    ]


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ("name", "dob")
    search_fields = ("name",)
    date_hierarchy = "dob"
    ordering = ("name",)

    # Инлайн связи с фильмами; у through-модели два FK, укажем какой использовать
    class AttachedMovieInline(MovieActorInline):
        fk_name = "actor"

    inlines = [AttachedMovieInline]


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("name", "dob")
    search_fields = ("name",)
    date_hierarchy = "dob"
    ordering = ("name",)

    class AttachedMovieInline(MovieDirectorInline):
        fk_name = "director"

    inlines = [AttachedMovieInline]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("name",)
    search_fields = ("name",)
    ordering = ("name",)

    class AttachedMovieInline(MovieGenreInline):
        fk_name = "genre"

    inlines = [AttachedMovieInline]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("movie", "movie_start", "price")
    list_filter = ("movie",)
    date_hierarchy = "movie_start"
    search_fields = ("movie__name",)
    ordering = ("-movie_start",)
    autocomplete_fields = ("movie",)