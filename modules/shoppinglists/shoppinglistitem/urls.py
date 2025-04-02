from django.urls import path, include
from .views import ShoppingListItemViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'shoppingliistitem', ShoppingListItemViewSet, basename='shoppingliistitem')

urlpatterns = [
    path('', include(router.urls)),
]