from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # auth
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    #profile
    path('profile/', ProfileView.as_view(), name='profile'),
    # marketplace
    path('products/', MarketplaceView.as_view()),
    path('post/', PostWasteView.as_view()),
    path('post/<int:pk>/', PostDetailView.as_view()), # retrieve/update/delete
    path('product/<int:pk>/', PublicProductDetailView.as_view()),  # public view

     # buy (function-based view)
    path('buy/<int:pk>/', buy_product),  

    # history
    path('orders/', OrderHistoryView.as_view()),
    path('my-posts/', PostHistoryView.as_view()),
]
