# myapp/urls.py
from django.urls import path
from .views import (
    CreateItemAPIView, UserItemsAPIView, ItemDetailAPIView,
    MarketplaceAPIView, BuyItemAPIView,RegisterAPIView, MyTokenObtainPairView, ProfileView, ChangePasswordView, LogoutView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='auth_register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),  # login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('profile/', ProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    #waste item api
    path('items/create/', CreateItemAPIView.as_view(), name='item_create'),
    path('items/my/', UserItemsAPIView.as_view(), name='user_items'),
    path('items/<str:_id>/', ItemDetailAPIView.as_view(), name='item_detail'),
    path('marketplace/', MarketplaceAPIView.as_view(), name='marketplace'),
    path('items/buy/<str:item_id>/', BuyItemAPIView.as_view(), name='buy_item'),
]
