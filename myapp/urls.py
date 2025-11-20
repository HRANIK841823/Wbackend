from django.urls import path, re_path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # auth
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),

    # profile
    path('profile/', ProfileView.as_view(), name='profile'),

    # marketplace
    path('products/', MarketplaceView.as_view()),
    path('post/', PostWasteView.as_view()),
    re_path(r'^post/(?P<pk>[0-9a-fA-F]{24})/$', PostDetailView.as_view()),  # ObjectId
    re_path(r'^product/(?P<pk>[0-9a-fA-F]{24})/$', PublicProductDetailView.as_view()),

    # buy (function-based view)
    re_path(r'^buy/(?P<pk>[0-9a-fA-F]{24})/$', buy_product),  

    # history
    path('orders/', OrderHistoryView.as_view()),
    path('my-posts/', PostHistoryView.as_view()),
]
