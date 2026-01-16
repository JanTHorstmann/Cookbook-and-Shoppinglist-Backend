from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_204_NO_CONTENT
from .models import Recipe
from .serializers import RecipeSerializer
from rest_framework.permissions import IsAuthenticated
from modules.cookbook.favorites.models import Favorite
from django.db.models import Exists, OuterRef

class RecipeViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_queryset(self):
        user = self.request.user

        return Recipe.objects.annotate(
            is_favorite=Exists(
                Favorite.objects.filter(
                    user=user,
                    recipe=OuterRef("pk")
                )
            )
        )

    def perform_create(self, serializer):
        name = serializer.validated_data["name"].strip().lower()
        serializer.save(name=name, author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=HTTP_204_NO_CONTENT)
