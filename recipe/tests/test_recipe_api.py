from os import name
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.test import TestCase
from django.test import client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
import tempfile
import os

from PIL import Image




RECIPES_URL = reverse('recipe:recipe-list')

# /api/recipe/recipes

#/api/recipe/recipes/1/

def image_upload_url(recipe_id):
    """
    return url for recipe image upload
    """
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

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

    def test_create_basic_recipe(self):
        """
        test creating  a recipe without tags and igredients, just basic
        """
        paylaod ={
            'title':'Kek me cokollat',
            'time_minutes':5,
            'price':5.00
        }
        res = self.client.post(RECIPES_URL, paylaod)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id = res.data['id'])
        for key in paylaod.keys():
            self.assertEqual(paylaod[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """
        test reacitng a recipe with tags
        """
        tag1 = sample_tag(user= self.user, name='Vegan')
        tag2 = sample_tag(user= self.user, name = 'Meat')
        paylaod ={
            'title':'Avocado Lime cheescake',
            'tags':[tag1.id, tag2.id],
            'time_minutes': 5,
            'price': 5.00
        }

        res = self.client.post(RECIPES_URL, paylaod)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id= res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(),2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredient(self):
        """
        docstring
        """
        ingredient1 = sample_ingredient(user =self.user, name = 'Praws')
        ingredient2 =  sample_ingredient(user =self.user, name ='ginger')
        payload = {
            'title':'Thai ajsfdasf',
            'ingredients':[ingredient1.id, ingredient2.id],
            'time_minutes':2,
            'price':20.00
        }
        res =self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """
        test updating a recipe with patch
        """
        recipe = sample_recipe(user = self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user = self.user, name ='Curry')
        payload = {
            'title':'chicken tikka',
            'tags':{new_tag.id}
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        # you have to refresh the object to get the updated values from db
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags),1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """
        test updatioing a recipe with PUT
        """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload= {
            'title':'spageti carbonara',
            'time_minutes':25,
            'price':5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url,payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title,payload['title'])
        self.assertEqual(recipe.time_minutes,payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(),0)


class RecipeImageUploadTests(TestCase):
    """
    docstring
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@testlondongmaiasf.com',
            'tesdfsdfds'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user= self.user)

    def tearDown(self):
        # make sure the image is removed after running the test
        self.recipe.image.delete()

    def test_upload_image(self):
        """
        testing uploading a valid image to recipe
        """
        url = image_upload_url(self.recipe.id)
        # create a temp file in the system
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10,10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """
        test uploading a invalid image
        """
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image':'string instead'}, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
