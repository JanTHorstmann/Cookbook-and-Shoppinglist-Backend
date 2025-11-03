from django.test import TestCase
from modules.cookbook.recipe_ingredients.models import RecipeIngredient
from modules.cookbook.ingredients.models import Ingredient
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from decimal import Decimal

class RecipeIngredientTestCase(TestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(name="Ei")
        self.recipe_ingredient = RecipeIngredient.objects.create(
            ingredient=self.ingredient,
            amount=Decimal("1.00"),
            unit="Stück"
        )

    def test_recipe_ingredient_creation(self):
        """Checks whether the recipe ingredient object is created correctly."""
        self.assertEqual(self.recipe_ingredient.ingredient.name, "ei")
        self.assertEqual(self.recipe_ingredient.amount, Decimal("1.00"))
        self.assertEqual(self.recipe_ingredient.unit, "Stück")

    def test_recipe_ingredient_str(self):
        """Checks whether __str__() is formatted correctly."""
        self.assertEqual(str(self.recipe_ingredient), "1.00 Stück Ei")

    def test_recipe_ingredient_unique_together(self):
        """Ensures that ingredient + amount is unique."""
        with self.assertRaises(IntegrityError):
            RecipeIngredient.objects.create(ingredient=self.ingredient, amount=Decimal("1.00"), unit="Stück")

    def test_create_recipe_ingredient(self):
        """Tests the creation of a new RecipeIngredient."""
        ingredient = Ingredient.objects.create(name="Milch")
        recipe_ingredient = RecipeIngredient.objects.create(
            ingredient=ingredient,
            amount=Decimal("200.00"),  # DecimalField erwartet Zahlen
            unit="ml"
        )

        self.assertEqual(recipe_ingredient.ingredient.name, "milch")
        self.assertEqual(recipe_ingredient.amount, Decimal("200.00"))
        self.assertEqual(recipe_ingredient.unit, "ml")

    def test_delete_ingredient_cascade(self):
        """Checks whether linked RecipeIngredient entries are deleted when the Ingredient is deleted."""
        ingredient_id = self.ingredient.id  # ID vor dem Löschen speichern
        self.ingredient.delete()

        self.assertFalse(RecipeIngredient.objects.filter(ingredient_id=ingredient_id).exists())

    def test_recipe_ingredient_empty_amount(self):
        """Tests whether an empty amount (None) is rejected."""
        with self.assertRaises(ValidationError):
            recipe_ingredient = RecipeIngredient(ingredient=self.ingredient, amount=None, unit="Stück")
            recipe_ingredient.full_clean()

    def test_delete_recipe_ingredient_keeps_ingredient(self):
        """Stellt sicher, dass Ingredient nicht gelöscht wird, wenn RecipeIngredient gelöscht wird."""
        self.recipe_ingredient.delete()
        self.assertTrue(Ingredient.objects.filter(id=self.ingredient.id).exists())
