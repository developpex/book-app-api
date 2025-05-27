"""
Tests for book APIs
"""
import os
import tempfile
from decimal import Decimal

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import (
    Book
)
from book.serializers import (
    BookSerializer, BookDetailSerializer
)
from catalog.models import Genre, Author

BOOK_URL = reverse("book:book-list")


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def detail_url(book_id):
    """Create and return a book detail URL."""
    return reverse("book:book-detail", args=[book_id])


def image_upload_url(book_id):
    """Create and return an image upload URL."""
    return reverse("book:book-upload-image", args=[book_id])


def create_book(user, **params):
    """Create and return a book"""
    defaults = {
        "title": "Sample book title",
        "price": Decimal("5.25"),
        "description": "Sample book description",
        "link": "http://example.com/book.pdf"
    }
    defaults.update(params)

    book = Book.objects.create(user=user, **defaults)
    return book


class PublicBookAPITests(TestCase):
    """Test unauthenticated API request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@example.com",
            password="userpass123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_book(self):
        """Test retrieving a list of books"""
        create_book(user=self.user)
        create_book(user=self.user)

        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        books = Book.objects.all().order_by("-id")
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_book_list_limited_to_user(self):
        """Test list of books is limited to authenticated user."""
        new_user = create_user(
            email="newuser@example.com",
            password="testpass123"
        )

        create_book(user=self.user)
        create_book(user=new_user)

        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        books = Book.objects.filter(user=self.user)
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_get_book_detail(self):
        """Test get book detail"""
        book = create_book(self.user)

        url = detail_url(book.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = BookDetailSerializer(book)
        self.assertEqual(res.data, serializer.data)

    def test_create_book(self):
        """Test creating a book"""
        payload = {
            "title": "Sample book",
            "price": Decimal("5.99"),
            "link": "https://example.com/book.pdf"
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=res.data["id"])
        for key, value in payload.items():
            self.assertEqual(getattr(book, key), value)
        self.assertEqual(book.user, self.user)

    def test_partial_update(self):
        """Test the partial update of a book"""
        original_link = "https://example.com/book.pdf"
        book = create_book(
            user=self.user,
            title="Sample book title",
            link=original_link
        )

        payload = {
            "title": "New book title"
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.link, original_link)
        self.assertEqual(book.user, self.user)

    def test_full_update(self):
        """Test full update of book."""
        book = create_book(
            user=self.user,
            title="Sample book title",
            link="https://exmaple.com/book.pdf",
            description="Sample book description.",
        )

        payload = {
            "title": "New book title",
            "link": "https://example.com/new-book.pdf",
            "description": "New book description",
            "price": Decimal("2.50"),
        }
        url = detail_url(book.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(book, key), value)
        self.assertEqual(book.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the book user results in an error."""
        new_user = create_user(email="user2@example.com", password="test123")
        book = create_book(user=self.user)

        payload = {"user": new_user.id}
        url = detail_url(book.id)
        self.client.patch(url, payload)

        book.refresh_from_db()
        self.assertEqual(book.user, self.user)

    def test_delete_book(self):
        """Test deleting a book successful."""
        book = create_book(user=self.user)

        url = detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_book_other_users_book_error(self):
        """Test trying to delete another users book gives error."""
        new_user = create_user(email="user2@example.com", password="test123")
        book = create_book(user=new_user)

        url = detail_url(book.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        self.assertTrue(Book.objects.filter(id=book.id).exists())

    def test_create_book_with_new_genres(self):
        """Test creating a book with new genres"""
        payload = {
            "title": "New book title",
            "link": "https://example.com/new-book.pdf",
            "description": "New book description",
            "price": Decimal("2.50"),
            "genres": [
                {"name": "Fantasy"},
                {"name": "History"}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        books = Book.objects.filter(user=self.user)
        self.assertEqual(books.count(), 1)

        book = books[0]
        self.assertEqual(book.genres.count(), 2)

        for genre in payload["genres"]:
            genre_exist = book.genres.filter(
                name=genre["name"].strip().title()
            ).exists()
            self.assertTrue(genre_exist)

    def test_create_book_with_existing_genres(self):
        """Test Creating a recipe with an existing genre"""
        fantasy_genre = Genre.objects.create(name="Fantasy")
        payload = {
            "title": "New book title",
            "link": "https://example.com/new-book.pdf",
            "description": "New book description",
            "price": Decimal("2.50"),
            "genres": [
                {"name": "Fantasy"},
                {"name": "History"}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        books = Book.objects.filter(user=self.user)
        self.assertEqual(books.count(), 1)

        book = books[0]
        self.assertEqual(book.genres.count(), 2)
        self.assertIn(fantasy_genre, book.genres.all())

        for genre in payload["genres"]:
            genre_exist = book.genres.filter(
                name=genre["name"].strip().title()
            ).exists()
            self.assertTrue(genre_exist)

    def test_genre_name_normalization_on_book_create(self):
        """Test that genre names are normalized on creation."""
        payload = {
            "title": "Normalize Test Book",
            "link": "https://example.com/book.pdf",
            "description": "Testing genre normalization",
            "price": Decimal("3.00"),
            "genres": [
                {"name": "  fantasy  "},
                {"name": "HISTORY"},
                {"name": "sCiEncE fICtioN"}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        expected_names = ["Fantasy", "History", "Science Fiction"]
        for name in expected_names:
            exists = Genre.objects.filter(name=name).exists()
            self.assertTrue(exists)

    def test_reuse_normalized_genre(self):
        """Test that existing normalized genre is reused."""
        Genre.objects.create(name="Fantasy")

        payload = {
            "title": "Another Book",
            "link": "https://example.com/book.pdf",
            "description": "Reuse genre test",
            "price": Decimal("5.00"),
            "genres": [
                {"name": "  FANtAsY "}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Genre.objects.filter(name__iexact="fantasy").count(), 1)

    def test_create_genre_on_update(self):
        """Test creating a genre on an update of the book"""
        book = create_book(user=self.user)
        payload = {
            "genres": [{"name": "Fantasy"}]
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_genre = Genre.objects.get(name="Fantasy")
        self.assertIn(new_genre, book.genres.all())

    def test_get_existing_genre_on_update(self):
        """Test getting existing genre when updating a book"""
        genre = Genre.objects.create(name="Fantasy")
        book = create_book(user=self.user)
        book.genres.add(genre)

        new_genre = Genre.objects.create(name="History")
        payload = {
            "genres": [{"name": "History"}]
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertIn(new_genre, book.genres.all())
        self.assertNotIn(genre, book.genres.all())

    def test_clear_book_genres(self):
        """Test clearing a recipes genres"""
        genre = Genre.objects.create(name="Fantasy")
        book = create_book(user=self.user)
        book.genres.add(genre)

        payload = {
            "genres": []
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertEqual(book.genres.count(), 0)

    def test_create_book_with_new_authors(self):
        """Test creating a book with new authors"""
        payload = {
            "title": "New book title",
            "link": "https://example.com/new-book.pdf",
            "description": "New book description",
            "price": Decimal("2.50"),
            "authors": [
                {"name": "Author_one"},
                {"name": "Author_two"}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        books = Book.objects.filter(user=self.user)
        self.assertEqual(books.count(), 1)

        book = books[0]
        self.assertEqual(book.authors.count(), 2)

        for author in payload["authors"]:
            author_exist = book.authors.filter(
                name=author["name"].strip().title()
            ).exists()
            self.assertTrue(author_exist)

    def test_create_book_with_existing_authors(self):
        """Test Creating a recipe with an existing author"""
        fantasy_author = Author.objects.create(name="Author_One")
        payload = {
            "title": "New book title",
            "link": "https://example.com/new-book.pdf",
            "description": "New book description",
            "price": Decimal("2.50"),
            "authors": [
                {"name": "Author_One"},
                {"name": "Author_Two"}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        books = Book.objects.filter(user=self.user)
        self.assertEqual(books.count(), 1)

        book = books[0]
        self.assertEqual(book.authors.count(), 2)
        self.assertIn(fantasy_author, book.authors.all())

        for author in payload["authors"]:
            author_exist = book.authors.filter(
                name=author["name"].strip().title()
            ).exists()
            self.assertTrue(author_exist)

    def test_author_name_normalization_on_book_create(self):
        """Test that author names are normalized on creation."""
        payload = {
            "title": "Normalize Test Book",
            "link": "https://example.com/book.pdf",
            "description": "Testing author normalization",
            "price": Decimal("3.00"),
            "authors": [
                {"name": "  author_one  "},
                {"name": "AUTHOR_TWO"},
                {"name": "AuthOr ONe"}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        expected_names = ["Author_One", "Author_Two", "Author One"]
        for name in expected_names:
            exists = Author.objects.filter(name=name).exists()
            self.assertTrue(exists)

    def test_reuse_normalized_author(self):
        """Test that existing normalized author is reused."""
        Author.objects.create(name="Author_One")

        payload = {
            "title": "Another Book",
            "link": "https://example.com/book.pdf",
            "description": "Reuse author test",
            "price": Decimal("5.00"),
            "authors": [
                {"name": "  Author ONE "}
            ]
        }

        res = self.client.post(BOOK_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Author.objects.filter(name__iexact="Author One").count(), 1)

    def test_create_author_on_update(self):
        """Test creating a author on an update of the book"""
        book = create_book(user=self.user)
        payload = {
            "authors": [{"name": "Author_One"}]
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_author = Author.objects.get(name="Author_One")
        self.assertIn(new_author, book.authors.all())

    def test_get_existing_author_on_update(self):
        """Test getting existing author when updating a book"""
        author = Author.objects.create(name="Author_one")
        book = create_book(user=self.user)
        book.authors.add(author)

        new_author = Author.objects.create(name="Author_Two")
        payload = {
            "authors": [{"name": "Author_Two"}]
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertIn(new_author, book.authors.all())
        self.assertNotIn(author, book.authors.all())

    def test_clear_book_authors(self):
        """Test clearing a recipes authors"""
        author = Author.objects.create(name="Author_One")
        book = create_book(user=self.user)
        book.authors.add(author)

        payload = {
            "authors": []
        }

        url = detail_url(book.id)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertEqual(book.authors.count(), 0)


class ImageUploadTest(TestCase):
    """Tests for the image upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="user@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_book(user=self.user)

    def tearDown(self):
        self.recipe.image.delete(0)

    def test_upload_image(self):
        """Test uploading image to a recipe."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as image_file:
            img = Image.new("RGB", (10, 10))
            img.save(image_file, format="JPEG")
            # go to beginning of the file, pointer is on te end after uploading
            image_file.seek(0)
            payload = {
                "image": image_file
            }
            res = self.client.post(url, payload, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image"""
        url = image_upload_url(self.recipe.id)
        payload = {
            "image": "not an image"
        }

        res = self.client.post(url, payload, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
