from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import ShoppingListItem
from modules.shoppinglists.listcollection.models import ListCollection
from modules.cookbook.ingredients.models import Ingredient
from .serializers import ShoppingListItemSerializer
from rest_framework.response import Response
from rest_framework import status

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


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pk = kwargs.get('pk')
    
        try:
            list_item_instance = ShoppingListItem.objects.get(pk=pk)
        except ShoppingListItem.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
    
        user = request.user
        shopping_list = list_item_instance.shopping_list
        is_author = shopping_list.author == user
        is_participant = shopping_list.participants.filter(pk=user.pk).exists()
    
        if not (is_author or is_participant):
            return Response(
                {"detail": "You do not have permission to edit this item."},
                status=status.HTTP_403_FORBIDDEN
            )
    
        serializer = self.get_serializer(list_item_instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    
        return Response(serializer.data, status=status.HTTP_200_OK)
