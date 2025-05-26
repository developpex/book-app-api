"""
URL mappings for the book API.
"""

from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from book.views import BookViewSet

router = DefaultRouter()
router.register("books", BookViewSet)

app_name = "book"

urlpatterns = [
    path("", include(router.urls))
]
