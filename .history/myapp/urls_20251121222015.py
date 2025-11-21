from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # auth
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),

    # profile
    path('profile/', ProfileView.as_view()),

    # marketplace
    path('products/', MarketplaceView.as_view()),
    path('post/', PostWasteView.as_view()),
    path('post/<str:pk>/', PostDetailView.as_view()),
    path('product/<str:pk>/', PublicProductDetailView.as_view()),

    # buy
    path('buy/<str:pk>/', buy_product),

    # history
    path('orders/', OrderHistoryView.as_view()),
    path('my-posts/', PostHistoryView.as_view()),
]
