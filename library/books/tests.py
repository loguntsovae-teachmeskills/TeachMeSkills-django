# books/tests/test_views.py
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from .models import Book, Author


class BookViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Базовые данные
        self.b1_title = "Alpha"
        self.b1 = Book.objects.create(title=self.b1_title)
        self.b2_title = "Beta"
        self.b2 = Book.objects.create(title=self.b2_title)
        self.b3_title = "Gamma"
        self.b3 = Book.objects.create(title=self.b3_title)

        # Имена роутов предполагаются как у DRF-роутера:
        # router.register("books", BookViewSet, basename="book")
        # Если у тебя другие — поправь здесь.
        self.list_url = reverse("book-list")
        # detail_url удобно получать функцией:
        self.detail_url = lambda pk: reverse("book-detail", kwargs={"pk": pk})

    def test_list_returns_books_ordered_by_id(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Проверяем порядок id по умолчанию (order_by("id"))
        ids = [item["id"] for item in resp.json()]
        self.assertEqual(ids, [self.b1.id, self.b2.id, self.b3.id])

    def test_create_book(self):
        title = "Django for Beginners"
        payload = {"title": title}
        self.assertFalse(Book.objects.filter(title=title).exists())
        resp = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title=title).exists())

    def test_retrieve_book(self):
        resp = self.client.get(self.detail_url(self.b2.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()["title"], self.b2_title)

    def test_partial_update_book(self):
        resp = self.client.patch(self.detail_url(self.b3.id), data={"title": "G"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.b3.refresh_from_db()
        self.assertEqual(self.b3.title, "G")

    def test_delete_book(self):
        resp = self.client.delete(self.detail_url(self.b1.id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(pk=self.b1.id).exists())

    def test_search_filter_by_title(self):
        # ?search=al — должно найти "Alpha"
        resp = self.client.get(self.list_url, {"search": "al"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [x["title"] for x in resp.json()]
        self.assertIn("Alpha", titles)
        # и не обязательно включать Beta/Gamma
        # (в зависимости от настроек поиска может вернуть частично совпавшие)

    def test_ordering_by_title_desc(self):
        resp = self.client.get(self.list_url, {"ordering": "-title"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [x["title"] for x in resp.json()]
        self.assertEqual(titles, sorted([self.b1.title, self.b2.title, self.b3.title], reverse=True))


class AuthorViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Предполагаем, что у Author есть поля name и is_active
        self.a1 = Author.objects.create(name="Charles", is_active=True)
        self.a2 = Author.objects.create(name="Arthur", is_active=True)
        self.a3 = Author.objects.create(name="Dormant", is_active=False)

        # router.register("authors", AuthorViewSet, basename="author")
        self.list_url = reverse("author-list")
        self.detail_url = lambda pk: reverse("author-detail", kwargs={"pk": pk})

    def test_list_returns_only_active_authors_ordered_by_name(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [x["name"] for x in resp.json()]
        # Только активные
        self.assertEqual(names, ["Arthur", "Charles"])  # отсортированы по name ASC

    def test_retrieve_author_allowed(self):
        # ReadOnlyModelViewSet — GET /authors/{id}/ разрешён
        resp = self.client.get(self.detail_url(self.a1.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()["name"], "Charles")
        resp = self.client.get(self.detail_url(self.a3.id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_create_author_not_allowed(self):
        # ReadOnlyModelViewSet — POST /authors/ должен вернуть 405
        resp = self.client.post(self.list_url, data={"name": "New", "is_active": True}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

