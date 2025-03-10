from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Ingredient
from django.urls import reverse

class IngredientTestCase(TestCase):
    def setUp(self):
        Ingredient.objects.create(name="Mehl")
        Ingredient.objects.create(name="brot")

    def test_ingredients_save_in_lowercase(self):
        ingredient = Ingredient.objects.create(name="Zucker")
        self.assertEqual(ingredient.name, "zucker")

    def test_ingredient_str_representation(self):
        ingredient = Ingredient.objects.create(name="zucker")
        self.assertEqual(str(ingredient), "Zucker")

    def test_ingredient_unique_constraint(self):
        Ingredient.objects.create(name="zucker")
        with self.assertRaises(Exception):  # Sollte einen Fehler werfen
            Ingredient.objects.create(name="ZUCKER") 

    def test_ingredient_empty_name(self):
        with self.assertRaises(ValueError):  # Erwarte jetzt explizit ValueError
            Ingredient.objects.create(name=" ")

    def test_case_insensitive_ingredient(self):
        Ingredient.objects.create(name="Salz")
        with self.assertRaises(Exception):
            Ingredient.objects.create(name="SALZ")  

class IngredientAPITestCase(APITestCase):
    def setUp(self):
        self.ingredient1 = Ingredient.objects.create(name="mehl")
        self.ingredient2 = Ingredient.objects.create(name="brot")
        self.url = reverse("ingredients-list")

    def test_get_ingredients(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Erwartet 2 Zutaten
        self.assertEqual(response.data[0]["name"], "Mehl")  # Großbuchstabe!
        self.assertEqual(response.data[1]["name"], "Brot")

    def test_create_ingredient_success(self):
        data = {"name": "Käse"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ingredient.objects.filter(name="käse").exists())

    def test_create_duplicate_ingredient(self):
        data = {"name": "Mehl"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "This ingredient already exists!")

    def test_create_empty_ingredient(self):
        data = {"name": ""}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_ingredient_detail(self):
        url = reverse("ingredients-detail", kwargs={"pk": self.ingredient1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Mehl")

    def test_update_ingredient(self):
        url = reverse("ingredients-detail", kwargs={"pk": self.ingredient1.id})
        data = {"name": "Weizenmehl"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Weizenmehl".capitalize())

    def test_delete_ingredient(self):
        url = reverse("ingredients-detail", kwargs={"pk": self.ingredient1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=self.ingredient1.id).exists())