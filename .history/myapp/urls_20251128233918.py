from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, 
    register_user, 
    change_password, 
    get_current_user,
    my_purchase_history,
    my_sell_history,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'marketplace', ProductViewSet, basename='product')

urlpatterns = [
    # Auth Endpoints
    path('auth/register/', register_user, name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', change_password, name='change_password'),
    path('auth/me/', get_current_user, name='current_user'),

    # My Purchase History outside the router
    path('my_purchase_history/', my_purchase_history, name='my_purchase_history'),
    path('my_sell_history/', my_sell_history, name='my_sell_history'),

    # Marketplace Router
    path('marketplace/', include(router.urls)),
]