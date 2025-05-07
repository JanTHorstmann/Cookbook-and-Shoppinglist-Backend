from django.urls import path, include
from .views import ShoppingListItemViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'shoppinglistitem', ShoppingListItemViewSet, basename='shoppinglistitem')

urlpatterns = [
    path('', include(router.urls)),
]