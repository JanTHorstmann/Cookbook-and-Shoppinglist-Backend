from rest_framework import serializers
from .models import Recipe 
from modules.cookbook.recipe_ingredients.serializers import RecipeIngredientSerializer
from modules.cookbook.ingredients.models import Ingredient 
# from modules.cookbook.recipe_ingredients.models import RecipeIngredient 


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = ["id", "name", "instructions", "preparation_time", "difficulty", "author", "ingredients", "recipe_img"]

    def create(self, validated_data):     
        from modules.cookbook.recipe_ingredients.models import RecipeIngredient   
        ingredients_data = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)


        
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient_name = ingredient_data["ingredient"].strip().lower()
            ingredient, created = Ingredient.objects.get_or_create(name=ingredient_name)

            recipe_ingredient, _ = RecipeIngredient.objects.get_or_create(
                ingredient=ingredient, 
                amount=ingredient_data["amount"]
            )
            recipe_ingredients.append(recipe_ingredient)
        
        recipe.ingredients.set(recipe_ingredients)

        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['name'] = instance.name.capitalize()
        return representation