from django.urls import path, include
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from apps.consumers.views import ConsumerViewSet, ManageViewSet

router = DefaultRouter()
router.register(r'security', ConsumerViewSet, basename='security')
router.register(r'manage', ManageViewSet, basename='manage')

schema_view = get_schema_view(
   openapi.Info(
      title="OAuth API",
      default_version='v0.0.1',
      description="OAuth security by António Courinha",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="antoniocourinha768@gmail.com"),
      license=openapi.License(name=""),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include(router.urls)),
    # path('swagger.<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)