from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Favorite
from modules.cookbook.recipe.models import Recipe
from rest_framework.permissions import IsAuthenticated
from .serializers import FavoriteSerializer
from django.contrib.auth import get_user_model


User = get_user_model()
class FavoritesView(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        user = self.request.user
        return Favorite.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)