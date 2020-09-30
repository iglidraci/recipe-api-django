from core.models import Ingredient
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='anjeza-test@gmail.com', password='anjeza'):
    # create a sample user
    return get_user_model().objects.create_user(email,password)



class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        # test creating a new user with email is successful
        email = 'test@gmail.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(email=email,password=password)
        self.assertEqual(user.email,email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test the email for a new user is normolized
        email = 'igl@Gmail.COM'
        user = get_user_model().objects.create_user(email,'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None,'test123')

    def test_super_user_is_created(self):
        # test creating a new super user
        user = get_user_model().objects.create_superuser('test@gmail.com','test123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        #test the tag string representation
        tag = models.Tag.objects.create(
            user = sample_user(),
            name = 'vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingridiants_str(self):
        """
        test the ingredient string representation
        """
        ingredient = models.Ingredient.objects.create(
            user = sample_user(),
            name = 'Cucumber'
        )
        self.assertEquals(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """
        test the recipe string representation
        """
        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title = 'Steak and mushroom souce',
            time_minutes = 5,
            price = 5.00
        )
        self.assertEqual(str(recipe), recipe.title)