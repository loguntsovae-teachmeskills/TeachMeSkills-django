# orm_training.py
# Учебные задания по Django ORM для моделей Author и Book.
#
# Модели (даны для справки):
# class Author(models.Model):
#     name = models.CharField(max_length=100)
#     is_active = models.BooleanField(default=False)
#
# class Book(models.Model):
#     title = models.CharField(max_length=100)
#     author = models.ForeignKey("Author", on_delete=models.PROTECT,
#                                null=True, blank=True, related_name="books")

from typing import Iterable, List, Optional, Tuple
from django.db import transaction
from django.db import models
from django.db.models import (
    QuerySet, Count, Avg, Max, Min, F, Q, Case, When, Value, BooleanField, IntegerField,
    OuterRef, Subquery, Exists
)
from django.db.models.functions import Length, Lower, Upper, Concat, Coalesce
from .models import Author, Book


# =========================
# БАЗА: выборки и фильтры
# =========================

def t01_all_books() -> QuerySet[Book]:
    """Вернуть QuerySet всех книг."""
    return Book.objects.all()

def t02_all_authors() -> QuerySet[Author]:
    """Вернуть QuerySet всех авторов."""
    return Author.objects.all()

def t03_books_with_author() -> QuerySet[Book]:
    """Книги, у которых автор не NULL."""
    return Book.objects.filter(author__isnull=False)

def t04_books_without_author() -> QuerySet[Book]:
    """Книги без автора (author IS NULL)."""
    raise NotImplementedError

def t05_active_authors() -> QuerySet[Author]:
    """Только активные авторы (is_active=True)."""
    return Author.objects.filter(is_active=True)

def t06_author_by_name_exact(name: str) -> QuerySet[Author]:
    """Автор(ы) с точным совпадением имени (case-sensitive/insensitive на ваше усмотрение — укажите в докстроке)."""
    return Author.objects.filter(name__iexact=name)

def t07_authors_name_icontains(substr: str) -> QuerySet[Author]:
    """Автор(ы), чьё имя содержит подстроку (без учёта регистра)."""
    return Author.objects.filter(name__icontains=substr)

def t08_books_title_startswith(prefix: str) -> QuerySet[Book]:
    """Книги, название которых начинается с prefix (без учёта регистра)."""
    return Book.objects.filter(title__istartswith=prefix)

def t10_books_ordered_by_title_asc() -> QuerySet[Book]:
    """Книги, отсортированные по title по возрастанию."""
    return Book.objects.order_by("title")

def t11_first_n_books_by_id(n: int) -> QuerySet[Book]:
    """Первые n книг по возрастанию id (срез QuerySet)."""
    return Book.objects.order_by("id")[:n]

def t12_last_book_by_id() -> Optional[Book]:
    """Последняя книга по id (или None, если таблица пуста)."""
    return Book.objects.order_by("-id").first()


# =========================
# VALUES / VALUES_LIST
# =========================

def t15_values_titles() -> QuerySet:
    """Вернуть список словарей с ключом 'title' для всех книг (values('title'))."""
    return Book.objects.values("title")

def t16_values_list_author_ids(flat: bool = True) -> Iterable[int]:
    """Вернуть набор ID авторов, встречающихся у книг (values_list с distinct)."""
    raise NotImplementedError

def t17_values_books_as_pairs() -> Iterable[Tuple[int, str]]:
    """Вернуть пары (id, title) для всех книг (values_list)."""
    return Book.objects.values_list("id", "title")


# =========================
# АННОТАЦИИ / АГРЕГАЦИИ
# =========================

def t18_total_books_count() -> int:
    """Общее число книг (aggregate Count)."""
    return Book.objects.aggregate(total_books_count=Count("id"))["total_books_count"]

def t19_books_per_author() -> QuerySet[Author]:
    """Аннотировать авторов числом их книг: .annotate(num_books=Count('books'))."""
    return Author.objects.annotate(num_books=Count('books'))

def t20_top_k_authors_by_books(k: int) -> QuerySet[Author]:
    """Топ-k авторов по числу книг (при равенстве — любая стабильная сортировка)."""
    raise NotImplementedError

def t21_authors_with_avg_title_length() -> QuerySet[Author]:
    """Аннотировать авторов средней длиной названий их книг (используйте Length и Avg)."""
    raise NotImplementedError

def t22_books_with_author_name_annotation() -> QuerySet[Book]:
    """Аннотировать книги полем author_name = имя автора (Coalesce для NULL -> '—')."""
    raise NotImplementedError

def t23_authors_prolific_flag(min_books: int) -> QuerySet[Author]:
    """Аннотировать авторов булевым полем is_prolific: True, если книг >= min_books (Case/When)."""
    raise NotImplementedError

def t24_counts_split_by_active_flag() -> QuerySet:
    """Сгруппировать авторов по is_active и отдать counts (values('is_active').annotate(cnt=Count('id')))."""
    raise NotImplementedError

def t25_filtered_aggregate_active_books() -> int:
    """Подсчитать количество книг у активных авторов (Count с filter=Q(...))."""
    raise NotImplementedError

def t26_order_books_by_title_length_desc() -> QuerySet[Book]:
    """Отсортировать книги по длине названия по убыванию (Length + order_by)."""
    books = Book.objects.annotate(title_length=Length("title")).order_by("-title_length")
    return books


# =========================
# F, Q, CASE/WHEN
# =========================

def t27_complex_author_name_filter() -> QuerySet[Author]:
    """Вернуть активных авторов, у которых имя содержит 'a' ИЛИ 'e' (Q-объекты, icontains)."""
    query_1 = Q(name__icontains="a")
    query_2 = Q(name__icontains="e")
    authors = Author.objects.filter(is_active=True).filter(query_1 | query_2)

    # все авторы, которые или активны или bob содержат
    query_1 = Q(is_active=True)
    query_2 = Q(name__icontains="bob")
    authors = Author.objects.filter(query_1 | query_2)

    return authors

def t28_case_label_books() -> QuerySet[Book]:
    """Аннотировать книги label: 'SHORT' если title < 5 символов, иначе 'LONG' (Case/When, Length)."""
    raise NotImplementedError

def t29_title_uppercase_qs() -> QuerySet[Book]:
    """Вернуть QS книг, аннотированных upper_title = Upper('title') (без сохранения в БД)."""
    raise NotImplementedError

def t30_author_display_field() -> QuerySet[Author]:
    """Аннотировать display = Concat(name, Value(' ('), Coalesce(Count('books'), Value(0)), Value(')')).
       Подумайте, как аккуратно посчитать Count в Concat (подсказка: отдельная аннотация, затем Concat)."""
    raise NotImplementedError


# =========================
# SUBQUERY / EXISTS / OUTER REF
# =========================

def t31_authors_with_has_books_flag() -> QuerySet[Author]:
    """Аннотировать authors: has_books = Exists(подзапрос по Book с OuterRef('pk'))."""
    raise NotImplementedError

def t32_books_with_author_book_count() -> QuerySet[Book]:
    """Аннотировать каждую книгу числом всех книг её автора (Subquery на Count по author_id)."""
    raise NotImplementedError

def t33_books_with_author_first_book_id() -> QuerySet[Book]:
    """Аннотировать книгу полем first_book_id = id самой ранней (по id) книги этого автора (Subquery)."""
    raise NotImplementedError

def t34_authors_with_any_untitled_book_flag() -> QuerySet[Author]:
    """has_empty_title: Exists книги автора c пустым title ('')."""
    raise NotImplementedError


# =========================
# SELECT_RELATED / PREFETCH_RELATED / ONLY / DEFER
# =========================

def t36_books_select_related_author() -> QuerySet[Book]:
    """Книги с select_related('author')."""
    raise NotImplementedError

def t37_authors_prefetch_only_their_active_books() -> QuerySet[Author]:
    """Авторы с Prefetch на 'books' так, чтобы подтянуть только книги с непустым title и author!=NULL."""
    raise NotImplementedError

def t38_books_only_id_and_title() -> QuerySet[Book]:
    """Вернуть книги с only('id', 'title')."""
    raise NotImplementedError

def t39_books_defer_title() -> QuerySet[Book]:
    """Вернуть книги с defer('title')."""
    raise NotImplementedError


# =========================
# EXISTS / COUNT / LEN
# =========================

def t40_any_inactive_author_with_books() -> bool:
    """Вернуть True, если существует хотя бы один неактивный автор с >=1 книгой (используйте exists())."""
    raise NotImplementedError

def t41_orphan_books_count() -> int:
    """Сколько книг без автора (author IS NULL) — используйте .count()."""
    raise NotImplementedError

def t42_distinct_authors_count_from_books() -> int:
    """Сколько уникальных авторов встречается у книг (distinct count author_id)."""
    raise NotImplementedError


# =========================
# ОБНОВЛЕНИЯ / УДАЛЕНИЯ / BULK
# =========================

def t43_null_author_for_inactive_authors_books() -> int:
    """Сделать author=NULL у всех книг, где текущий author неактивен. Вернуть кол-во изменённых строк."""
    return Book.objects.filter(author__is_active=False).update(author=None)

def t44_delete_authors_without_books() -> Tuple[int, dict]:
    """Удалить всех авторов без книг. Вернуть результат .delete()."""
    return Author.objects.annotate(book_number=Coalesce(Count('books'), Value(0))).filter(book_number=0).delete()

def t45_bulk_create_books(author: Optional[Author], titles: List[str]) -> List[Book]:
    """Сделать bulk_create книг с указанным автором (или без автора, если None). Вернуть созданные объекты."""
    raise NotImplementedError

def t46_bulk_update_titles_prefix(prefix: str) -> int:
    """Обновить ВСЕМ книгам title = prefix + title (одним .update(), без Python-циклов).
       Подсказка: Concat(Value(prefix), F('title')). Вернуть число изменённых."""
    raise NotImplementedError

def t47_get_or_create_author(name: str, active: bool = False) -> Tuple[Author, bool]:
    """get_or_create по имени. is_active проставлять из аргумента."""
    raise NotImplementedError

def t48_update_or_create_book(title: str, author: Optional[Author]) -> Tuple[Book, bool]:
    """update_or_create книгу по title, проставляя/обновляя author."""
    raise NotImplementedError


# =========================
# ТРАНЗАКЦИИ / АТОМАРНОСТЬ
# =========================

def t49_atomic_create_author_and_books(author_name: str, titles: List[str]) -> Author:
    """В одной транзакции: создать автора (неактивного) и несколько его книг. В случае ошибки откатить всё."""
    raise NotImplementedError

def t50_toggle_active_for_authors_without_books() -> int:
    """В одной транзакции инвертировать is_active у всех авторов БЕЗ книг. Вернуть число обновлённых."""
    raise NotImplementedError


# =========================
# СЛЕЙСИНГ / ПАГИНАЦИЯ / ORDER BY
# =========================

def t51_paginate_books(page: int, per_page: int) -> QuerySet[Book]:
    """Вернуть срез книг для заданной страницы (1-индексация страниц). Отсортируйте по id ASC."""
    raise NotImplementedError

def t52_reverse_order_books_by_id() -> QuerySet[Book]:
    """Вернуть книги в порядке id DESC (используйте order_by('-id') или .reverse())."""
    raise NotImplementedError


# =========================
# UNION / INTERSECTION / DIFFERENCE
# =========================

def t53_authors_name_starts_a_or_b() -> QuerySet[Author]:
    """Объединить два QS: имена на 'A%' и на 'B%' (union)."""
    a_authors = Author.objects.filter(name__startswith='A')
    b_authors = Author.objects.filter(name__startswith='B')
    authors = a_authors.union(b_authors)


    return a_authors

def t54_intersection_example(substr: str) -> QuerySet[Author]:
    """Пересечение: авторы, имя которых содержит substr, и одновременно активны (intersection)."""
    raise NotImplementedError

def t55_difference_example() -> QuerySet[Author]:
    """Разность: активные авторы МИНУС авторы, у которых есть хотя бы одна книга."""
    raise NotImplementedError


# =========================
# ОКОННЫЕ ФУНКЦИИ (опционально)
# =========================
# * Можно пропустить, если у вас SQLite < 3.25 или старый Django.
# from django.db.models.expressions import Window
# from django.db.models.functions import RowNumber, Rank, DenseRank

def t56_rank_authors_by_book_count() -> QuerySet[Author]:
    """Аннотировать авторов ранком по числу книг (на ваше усмотрение Rank/DenseRank + order_by).
       Требуются оконные функции БД."""
    raise NotImplementedError


# =========================
# ОПТИМИЗАЦИЯ ЗАПРОСОВ (эвристики)
# =========================

def t57_books_with_authors_min_queries() -> List[Tuple[str, Optional[str]]]:
    """Вернуть список кортежей (book_title, author_name_or_None) c минимальным числом SQL-запросов.
       Подсказка: select_related + итерация.
       Формально верните Python-структуру, чтобы было удобно проверить в тестах."""
    raise NotImplementedError

def t58_authors_with_prefetched_books_min_queries() -> List[Tuple[str, int]]:
    """Вернуть [(author_name, num_books), ...] с минимальным числом запросов.
       Подсказка: prefetch_related / Prefetch."""
    raise NotImplementedError


# =========================
# ФУНКЦИИ ДЛЯ ПРОВЕРОК/ДЕМО-ДАННЫХ (без оценок)
# =========================

def demo_reset():
    """Удаляет всё из таблиц."""
    Book.objects.all().delete()
    Author.objects.all().delete()

def demo_seed():
    """
    Создаёт небольшой набор данных для ручной проверки.
    Не является «правильным ответом», используется только для удобства.
    """
    demo_reset()

    a1 = Author.objects.create(name="Alice Munro", is_active=True)
    a2 = Author.objects.create(name="Boris Pasternak", is_active=True)
    a3 = Author.objects.create(name="Charles Bukowski", is_active=False)
    a4 = Author.objects.create(name="bob marley", is_active=False)
    a5 = Author.objects.create(name="Анна", is_active=True)
    a6 = Author.objects.create(name="Без Книг", is_active=False)

    Book.objects.bulk_create([
        Book(title="Lives of Girls and Women", author=a1),
        Book(title="Runaway", author=a1),
        Book(title="The Door", author=a1),

        Book(title="Doctor Zhivago", author=a2),
        Book(title="Safe Conduct", author=a2),

        Book(title="Post Office", author=a3),
        Book(title="Women", author=a3),

        Book(title="No Woman No Cry", author=a4),

        Book(title="Книга 1", author=a5),
        Book(title="Книга 2", author=a5),

        Book(title="Untitled with digits 2025", author=None),
        Book(title="", author=a3),  # пустой title
    ])

    # Обновим флаг активности как угодно — это просто демо
    a4.is_active = True
    a4.save(update_fields=["is_active"])

def demo_info() -> str:
    """Короткая памятка по запуску в Django shell."""
    return (
        "Пример использования:\n"
        "  from app.orm_training import demo_seed, t01_all_books\n"
        "  demo_seed()\n"
        "  list(t01_all_books())\n"
        "Пишите свои тесты к функциям t01..t58.\n"
    )
