from django.db.models import query
from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe import serializers
from rest_framework.decorators import action
from rest_framework.response import Response


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                mixins.ListModelMixin,
                mixins.CreateModelMixin):
    """
    Base viewset for user owned recipe attributes
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # return objects for the current authenticated user only
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """
        create a new object
        """
        serializer.save(user=self.request.user)



class TagViewSet(BaseRecipeAttrViewSet):
    # manage tags in the database
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientsViewSet(BaseRecipeAttrViewSet):
    """
    manage ingredients in the database
    """
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    manage recieps in the database
    """
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    authentication_classes  = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    #private function
    def __params_to_ints(self, qs):
        # convert a list of string id into a list of ints
        # our_string = '1,2,3,4'
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """
        retrieve the recipes for authenticated user
        """
        # retrive get params for tags
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self.__params_to_ints(tags)
            # django sintax to filter on foreign keys
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ing_ids = self.__params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ing_ids)
        #return this instead of the main query set
        return queryset.filter(user = self.request.user).distinct()

    def get_serializer_class(self):
        """
        return approprieate serializer class
        """
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'upload_image':
            return serializers.RecipImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        # overide the create recipe
        serializer.save(user = self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """
        upload an image to a recipe
        """
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data =request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status = status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
