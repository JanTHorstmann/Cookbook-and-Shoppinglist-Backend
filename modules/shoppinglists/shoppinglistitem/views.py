from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ShoppingListItem
from .serializers import ShoppingListItemSerializer

class ShoppingListItemViewSet(viewsets.ModelViewSet):
    queryset = ShoppingListItem.objects.all()
    serializer_class = ShoppingListItemSerializer
    permission_classes = [IsAuthenticated]  # Nur authentifizierte User dürfen darauf zugreifen

    def get_queryset(self):
        return ShoppingListItem.objects.filter(shopping_list=self.request.shopping_list)

    def perform_create(self, serializer):
        serializer.save(author=self.request.shopping_list)
