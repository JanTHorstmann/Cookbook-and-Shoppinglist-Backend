from django.urls import path, include
from .views import FavoritesView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'favorites', FavoritesView, basename='favorites')

urlpatterns = [
    path('', include(router.urls)),
]