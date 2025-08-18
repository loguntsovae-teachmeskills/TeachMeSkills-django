# cinema/management/commands/seed_cinema.py
import io
import random
from decimal import Decimal
from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import slugify

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # Pillow не обязателен, но очень желателен
    Image = ImageDraw = ImageFont = None

from faker import Faker

from cinema.models import (
    Movie, Actor, Director, Genre, Schedule,
)


class Command(BaseCommand):
    help = "Generate fake data for cinema models (genres, actors, directors, movies, schedules)."

    def add_arguments(self, parser):
        parser.add_argument("--movies", type=int, default=10, help="How many movies to create.")
        parser.add_argument("--actors", type=int, default=30, help="How many actors to create.")
        parser.add_argument("--directors", type=int, default=10, help="How many directors to create.")
        parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
        parser.add_argument("--clear", action="store_true", help="Clear existing data before seeding.")

    def handle(self, *args, **opts):
        movies_n = opts["movies"]
        actors_n = opts["actors"]
        directors_n = opts["directors"]
        seed = opts["seed"]
        clear = opts["clear"]

        if seed is not None:
            random.seed(seed)

        fake = Faker()
        if seed is not None:
            Faker.seed(seed)

        if clear:
            self._clear_all()

        self._ensure_genres()
        actors = self._make_actors(fake, actors_n)
        directors = self._make_directors(fake, directors_n)
        movies = self._make_movies(fake, movies_n, actors, directors)
        self._make_schedules(movies)

        self.stdout.write(self.style.SUCCESS(
            f"✅ Done. Created {len(actors)} actors, {len(directors)} directors, "
            f"{len(movies)} movies and schedules."
        ))

    # ---------------- utilities ----------------

    def _clear_all(self):
        self.stdout.write("Clearing existing data…")
        Schedule.objects.all().delete()
        # M2M связи чистятся каскадно через удаление фильмов
        Movie.objects.all().delete()
        Actor.objects.all().delete()
        Director.objects.all().delete()
        # Жанры можно оставить, но для чистоты:
        Genre.objects.all().delete()
        self.stdout.write(self.style.WARNING("All cinema data cleared."))

    def _ensure_genres(self):
        from cinema.models import Genre  # local to ensure import of choices
        created = 0
        for value, label in Genre.GenreNameChoices.choices:
            _, was_created = Genre.objects.get_or_create(name=value)
            if was_created:
                created += 1
        self.stdout.write(f"Genres ensured (created {created}, total {Genre.objects.count()}).")

    def _make_actors(self, fake: Faker, n: int):
        self.stdout.write(f"Creating {n} actors…")
        objs = []
        for _ in range(n):
            name = fake.name()
            dob = fake.date_of_birth(minimum_age=22, maximum_age=85)
            actor = Actor(name=name, dob=dob)
            self._attach_avatar(actor, slugify(name))
            actor.save()
            objs.append(actor)
        return objs

    def _make_directors(self, fake: Faker, n: int):
        self.stdout.write(f"Creating {n} directors…")
        objs = []
        for _ in range(n):
            name = fake.name()
            dob = fake.date_of_birth(minimum_age=25, maximum_age=88)
            director = Director(name=name, dob=dob)
            self._attach_avatar(director, slugify(name))
            director.save()
            objs.append(director)
        return objs

    def _make_movies(self, fake: Faker, n: int, actors, directors):
        self.stdout.write(f"Creating {n} movies…")
        all_genres = list(Genre.objects.all())
        objs = []

        for _ in range(n):
            title = fake.sentence(nb_words=random.randint(1, 4)).rstrip(".")
            year = random.randint(1970, timezone.now().year)
            movie = Movie.objects.create(name=title, year=year)

            # genres 1–3
            movie.genres.add(*random.sample(all_genres, k=random.randint(1, min(3, len(all_genres)))))

            # actors 3–7
            if actors:
                movie.actors.add(*random.sample(actors, k=min(len(actors), random.randint(3, 7))))

            # directors 1–2
            if directors:
                movie.directors.add(*random.sample(directors, k=min(len(directors), random.randint(1, 2))))

            objs.append(movie)

        self.stdout.write(f"Movies created: {len(objs)}")
        return objs

    def _make_schedules(self, movies):
        self.stdout.write("Creating schedules for each movie…")
        show_times = [time(12, 0), time(15, 0), time(18, 0), time(21, 0)]
        today = date.today()
        tz = timezone.get_current_timezone()

        total = 0
        for m in movies:
            sessions = random.randint(2, 5)
            for _ in range(sessions):
                day_offset = random.randint(0, 14)
                t = random.choice(show_times)
                naive_dt = datetime.combine(today + timedelta(days=day_offset), t)
                aware_dt = timezone.make_aware(naive_dt, tz)

                price = Decimal(random.choice([7.99, 8.99, 9.99, 11.99, 12.99, 14.99, 16.99, 19.99]))

                Schedule.objects.create(movie=m, movie_start=aware_dt, price=price)
                total += 1

        self.stdout.write(f"Schedules created: {total}")

    def _attach_avatar(self, instance, base_name: str):
        """
        Генерирует простой PNG-аватар 256x256 с инициалами.
        Если Pillow недоступен, прикладывает пустой файл, чтобы пройти валидацию ImageField.
        """
        filename = f"{base_name or 'avatar'}.png"
        if Image is None:
            # fallback: пустой PNG-заглушка
            instance.avatar.save(filename, ContentFile(b""), save=False)
            return

        # Создаём изображение
        img = Image.new("RGB", (256, 256), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)

        initials = "".join([w[0] for w in base_name.split("-")[:2]]).upper() or "A"
        # простая попытка отрисовать без гарантии наличия шрифта
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        text_w, text_h = draw.textbbox((0, 0), initials, font=font)[2:]
        draw.text(((256 - text_w) / 2, (256 - text_h) / 2), initials, fill=(50, 50, 50), font=font)

        # В память → ContentFile
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        instance.avatar.save(filename, ContentFile(buf.read()), save=False)