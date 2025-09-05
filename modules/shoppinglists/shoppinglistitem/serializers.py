from rest_framework import serializers
from .models import ShoppingListItem
from modules.cookbook.ingredients.models import Ingredient

class ShoppingListItemSerializer(serializers.ModelSerializer):
    ingredient = serializers.CharField()

    class Meta:
        model = ShoppingListItem
        fields = ["ingredient", "amount", "unit", "shopping_list"]

    def create(self, validated_data):
        ingredient_name = validated_data["ingredient"].strip().lower()
        shopping_amount = validated_data["amount"]
        unit = validated_data["unit"]
        shopping_list = validated_data["shopping_list"]

        # Ingredient abrufen oder erstellen
        ingredient, _ = Ingredient.objects.get_or_create(name=ingredient_name)

        # ShoppingListItem abrufen oder erstellen
        shopping_item, created = ShoppingListItem.objects.get_or_create(
            ingredient=ingredient,
            shopping_list=shopping_list,
            defaults={"amount": shopping_amount, "unit": unit},
        )

        if not created:
            # Falls das Item existiert, Menge aktualisieren
            shopping_item.amount += shopping_amount
            shopping_item.save()

        return shopping_item
            