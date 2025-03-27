from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Recipe
from .serializers import RecipeSerializer
class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        name = serializer.validated_data["name"].strip().lower()
        serializer.save(name=name, author=self.request.user)
