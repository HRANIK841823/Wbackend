# myapp/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterAPIView,
    MyTokenObtainPairView,
    ProfileView,
    ChangePasswordView,
    LogoutView,

    CreateItemAPIView,
    UserItemsAPIView,
    ItemDetailAPIView,
    MarketplaceAPIView,
    BuyItemAPIView,
)

urlpatterns = [

    # -------------------------
    # Authentication
    # -------------------------
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", MyTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # -------------------------
    # User Profile
    # -------------------------
    path("profile/", ProfileView.as_view(), name="profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),

    # -------------------------
    # Item APIs (Mongo-style IDs)
    # -------------------------
    path("items/create/", CreateItemAPIView.as_view(), name="item_create"),
    path("items/my/", UserItemsAPIView.as_view(), name="user_items"),
    path("items/<str:_id>/", ItemDetailAPIView.as_view(), name="item_detail"),
    path("marketplace/", MarketplaceAPIView.as_view(), name="marketplace"),
    path("items/buy/<str:item_id>/", BuyItemAPIView.as_view(), name="buy_item"),
]
