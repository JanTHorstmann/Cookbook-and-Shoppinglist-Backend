from django.db import models
from modules.cookbook.ingredients.models import Ingredient 
from django.contrib.auth import get_user_model

class ShoppingListItem(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="shopping_list_items")
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    unit = models.CharField(max_length=50, blank=False)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        unique_together = ("ingredient", "author")

    def __str__(self):
        return f"{self.amount} {self.unit} {self.ingredient.name.capitalize()}"
