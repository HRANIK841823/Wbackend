from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, 
    register_user, 
    change_password, 
    get_current_user
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'marketplace', ProductViewSet, basename='product')

urlpatterns = [
    # Auth Endpoints
    path('register/', register_user, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', change_password, name='change_password'),
    path('me/', get_current_user, name='current_user'),

    # Marketplace Endpoints (CRUD + Buy + History)
    path('', include(router.urls)),
]