from django.urls import path, include
from .views import ListCollectionView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'listcollection', ListCollectionView, basename='listcollection')

urlpatterns = [
    path('', include(router.urls)),
]