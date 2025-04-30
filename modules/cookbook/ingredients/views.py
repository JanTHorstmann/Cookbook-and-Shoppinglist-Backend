from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Ingredient
from .serializers import IngredientSerializer

class IngredientViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def perform_create(self, serializer):
        name = serializer.validated_data['name'].strip().lower()
        ingredient, created = Ingredient.objects.get_or_create(name=name)

        if not created:
            raise serializers.ValidationError({'message': 'This ingredient already exists!'})

        serializer.instance = ingredient
