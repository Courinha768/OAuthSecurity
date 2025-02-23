from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.authentication.views import UserViewSet

router = DefaultRouter()
router.register(r'security', UserViewSet, basename='security')

urlpatterns = [
    path('', include(router.urls)),
]