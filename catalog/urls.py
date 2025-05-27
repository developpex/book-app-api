"""
URL mappings for the genre API.
"""

from django.urls import (
    path,
    include
)
from rest_framework.routers import DefaultRouter

from catalog.views import GenreViewSet, AuthorViewSet

router = DefaultRouter()
router.register("genres", GenreViewSet)
router.register("authors", AuthorViewSet)

app_name = "catalog"

urlpatterns = [
    path("", include(router.urls))
]
