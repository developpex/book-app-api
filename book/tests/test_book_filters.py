"""
Test for book filters
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.serializers import BookSerializer
from catalog.models import Genre, Author

BOOK_URL = reverse("book:book-list")


def create_user(email="user@example.com", password="testpass123"):
    """Create and return a user"""
    return get_user_model().objects.create_user(email=email, password=password)


def create_genre(name="Default Genre"):
    """Create and return a genre"""
    return Genre.objects.create(name=name)


def create_author(name="Default Author"):
    """Create and return an author"""
    return Author.objects.create(name=name)


def create_book(user, **params):
    """Creates and return a book"""
    defaults = {
        "title": "Sample Book",
        "price": 10.00,
        "link": "http://example.com",
    }
    defaults.update(params)
    book = Book.objects.create(user=user, **defaults)
    return book


class BookFilterTests(TestCase):
    """Test for filtering books"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_filter_books_by_genres(self):
        """Test to filter a book by genre"""
        genre1 = create_genre("Programming")
        genre2 = create_genre("Memoir")
        book1 = create_book(user=self.user, title="Book One")
        book2 = create_book(user=self.user, title="Book Two")
        book3 = create_book(user=self.user, title="Book Three")

        book1.genres.add(genre1)
        book2.genres.add(genre2)

        res = self.client.get(BOOK_URL, {"genres": "Programming,Memoir"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer1 = BookSerializer(book1)
        serializer2 = BookSerializer(book2)
        serializer3 = BookSerializer(book3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_books_by_authors(self):
        """Test to filter a book by author"""
        author1 = create_author("Author One")
        author2 = create_author("Author Two")
        book1 = create_book(user=self.user, title="Book One")
        book2 = create_book(user=self.user, title="Book Two")
        book3 = create_book(user=self.user, title="Book Three")

        book1.authors.add(author1)
        book2.authors.add(author2)

        res = self.client.get(BOOK_URL, {"authors": "Author One,Author Two"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer1 = BookSerializer(book1)
        serializer2 = BookSerializer(book2)
        serializer3 = BookSerializer(book3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_books_by_genres_and_authors(self):
        """Test  to filter a book by genre and author"""
        genre = create_genre("Fantasy")
        author = create_author("Tolkien")

        book1 = create_book(user=self.user, title="LOTR")
        book1.genres.add(genre)
        book1.authors.add(author)

        book2 = create_book(user=self.user, title="Other Book")

        res = self.client.get(BOOK_URL, {"genres": "Fantasy", "authors": "Tolkien"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer1 = BookSerializer(book1)
        serializer2 = BookSerializer(book2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
