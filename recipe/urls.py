from django.urls import path, include
from rest_framework import urlpatterns
from rest_framework.routers import DefaultRouter

from recipe import views

# default router will automaticlly registers the appropriate url for all the actions

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientsViewSet)
router.register('recipe',views.RecipeViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
