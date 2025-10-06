from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ShoppingListItem
from .serializers import ShoppingListItemSerializer

class ShoppingListItemViewSet(viewsets.ModelViewSet):
    queryset = ShoppingListItem.objects.all()
    serializer_class = ShoppingListItemSerializer
    permission_classes = [IsAuthenticated]  # Nur authentifizierte User dürfen darauf zugreifen

    def get_queryset(self):
        user = self.request.user
        return ShoppingListItem.objects.filter(
            shopping_list__author=user
        ) | ShoppingListItem.objects.filter(
            shopping_list__participants=user
        )

    def perform_create(self, serializer):
        shopping_list_id = self.request.data.get('shopping_list')
        serializer.save(shopping_list_id=shopping_list_id)
