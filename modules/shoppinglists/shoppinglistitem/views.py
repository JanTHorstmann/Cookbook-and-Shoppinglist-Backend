from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import ShoppingListItem
from modules.shoppinglists.listcollection.models import ListCollection
from .serializers import ShoppingListItemSerializer

class ShoppingListItemViewSet(viewsets.ModelViewSet):
    queryset = ShoppingListItem.objects.all()
    serializer_class = ShoppingListItemSerializer
    permission_classes = [IsAuthenticated]  # Nur authentifizierte User dürfen darauf zugreifen

    def get_queryset(self):
        user = self.request.user
        return (
        ShoppingListItem.objects.filter(
            shopping_list__author=user
        ) | ShoppingListItem.objects.filter(
            shopping_list__participants=user
        )
    ).distinct()

    def perform_create(self, serializer):
        
        shopping_list_id = self.request.data.get("shopping_list")

        try:
            shopping_list = ListCollection.objects.get(id=shopping_list_id)
        except ListCollection.DoesNotExist:
            raise PermissionDenied("The specified shopping list does not exist.")

        user = self.request.user

        if not (shopping_list.author == user or user in shopping_list.participants.all()):
            raise PermissionDenied("You do not have permission to add items to this shopping list.")
        
        serializer.save(shopping_list=shopping_list)
