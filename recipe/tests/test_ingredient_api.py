from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')

class PublicIngredientsApiTest(TestCase):
    """
    test the publicly available ingredient api
    """
    def setUp(self):
        self.client= APIClient()

    def test_login_required(self):
        # test that lgoin is required to access the end point
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """
    test ingredients can be retrived by authorized user
    """
    def setUp(self):
        self.client= APIClient()
        self.user = get_user_model().objects.create_user(
            'test@londonappdev.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_ingredient_test(self):
        """
        docstring
        """
        Ingredient.objects.create(user = self.user, name ='Kale')
        Ingredient.objects.create(user=self.user, name ='Salt')
        res =self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients,many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_to_user(self):
        """
        test that only ingredients for authenticated user are returned
        """
        user2 =get_user_model().objects.create_user(
            'other@gmail.com',
            'other123'
        )
        Ingredient.objects.create(user = user2, name ='Viniger')
        ingredient = Ingredient.objects.create(user=self.user, name ='Tumeric')
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'],ingredient.name)