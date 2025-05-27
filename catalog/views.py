"""
Views for the Catalog Api
"""
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from catalog.models import Genre, Author
from catalog.serializers import GenreSerializer, AuthorSerializer


class BaseCatalogViewSet(mixins.ListModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """Base view set for recipe attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.order_by("-name")


@extend_schema(tags=["Genre"])
class GenreViewSet(BaseCatalogViewSet):
    """Views for manage genre API."""
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


@extend_schema(tags=["Author"])
class AuthorViewSet(BaseCatalogViewSet):
    """Views for manage author API."""
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()
