from django.db import models
from modules.shoppinglists.listcollection.models import ListCollection
from modules.cookbook.recipe.models import Recipe

class MealPlan(models.Model):
    list_collection = models.ForeignKey(ListCollection, on_delete=models.CASCADE, related_name="meal_plans")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MealPlan for {self.list_collection}"