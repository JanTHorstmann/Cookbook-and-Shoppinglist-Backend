from django.db import models
from django.contrib.auth import get_user_model
from modules.cookbook.recipe_ingredients.models import RecipeIngredient
from django_resized import ResizedImageField

class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Einfach"),
        ("medium", "Mittel"),
        ("hard", "Schwierig"),
    ]

    CATEGORY_CHOICES = [
        ("breakfast", "Frühstück"),
        ("lunch", "Mittagessen"),
        ("dinner", "Abendessen"),
        ("snacks", "Snacks"),
    ]

    name = models.CharField(max_length=255)
    instructions = models.TextField()
    preparation_time = models.PositiveIntegerField(help_text="Preparation time in minutes")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='breakfast')
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(RecipeIngredient)
    recipe_img = ResizedImageField(size=[500, 300],
        upload_to="images/recipes/",
        force_format="JPEG",  # oder "PNG"
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        self.name = self.name.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name.capitalize()