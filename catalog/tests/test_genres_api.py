"""
Tests for the catalog api
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Genre
from catalog.serializers import GenreSerializer

GENRE_URL = reverse("catalog:genre-list")


def detail_url(genre_id):
    """Create and return a genre detail url"""
    return reverse("catalog:genre-detail", args=[genre_id])


def create_genre(**params):
    """Create and return a genre"""
    defaults = {
        "name": "Genre Name"
    }
    defaults.update(params)

    genre = Genre.objects.create(**defaults)
    return genre


class PublicGenreApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_genre(self):
        """Test auth is required to call API."""
        res = self.client.get(GENRE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGenreApiTests(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@example.com", "userpass123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_genres(self):
        """Test retrieving a list of genres."""
        create_genre(name="Fantasy")
        create_genre(name="History")

        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        genres = Genre.objects.all().order_by("-name")
        serializer = GenreSerializer(genres, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_update_genre(self):
        """Test for updating a genre"""
        genre = create_genre(name="Fantasy")
        payload = {
            "name": "History"
        }
        url = detail_url(genre.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        genre.refresh_from_db()
        self.assertEqual(genre.name, payload["name"])

    def test_delete_genre(self):
        genre = create_genre(name="Fantasy")

        url = detail_url(genre.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Genre.objects.filter(id=genre.id).exists())
