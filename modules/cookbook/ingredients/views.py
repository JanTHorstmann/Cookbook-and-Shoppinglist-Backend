from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status, serializers
from .models import Ingredient
from .serializers import IngredientSerializer

class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def perform_create(self, serializer):
        name = serializer.validated_data['name'].strip().lower()  # Einheitliche Speicherung
        ingredient, created = Ingredient.objects.get_or_create(name=name)

        if not created:  # Falls die Zutat bereits existiert
            raise serializers.ValidationError({'message': 'This ingredient already exists!'})

        serializer.instance = ingredient

    # def retrieve(self, request, pk=None):
    #     queryset = Ingredient.objects.all()
    #     user = get_object_or_404(queryset, pk=pk)
    #     serializer = IngredientSerializer(user)
    #     return Response(serializer.data)
