from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

# /api/recipe/recipes

#/api/recipe/recipes/1/

def detail_url(recipe_id):
    """
    return recipe detail url
    """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    # create and return a sample tag
    return Tag.objects.create(
        user=user,
        name = name
    )

def sample_ingredient(user, name = 'Cinnamon'):
    return Ingredient.objects.create(
        user =user,
        name = name
    )

def sample_recipe(user, **params):
    """
    Create and return a sample reciepe
    """
    defaults = {
        'title':'sample recipe',
        'time_minutes':10,
        'price': 5.00
    }
    # in case we pass params we update the defauls
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """
    test unauthenticated recipe access
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        test the authentication is required
        """
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """
    test unauthenitacved recipe api
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmial.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retireve_recipes(self):
        """
        docstring
        """
        sample_recipe(user = self.user)
        sample_recipe(user = self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """
        test retrieveing recipe to user
        """
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'pas123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        res =self.client.get(RECIPES_URL)
        recipies = Recipe.objects.filter(user = self.user)
        serializer = RecipeSerializer(recipies, many= True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """
        test viewing a recipe detail
        """
        recipe = sample_recipe(user= self.user)
        recipe.tags.add(sample_tag(user = self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url  = detail_url(recipe.id)

        res = self.client.get(url)
        # many = False here beacause we have only one recipe
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)