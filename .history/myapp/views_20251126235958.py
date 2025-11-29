# myapp/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import CustomUser
from .serializers import (
    RegisterSerializer, UserSerializer, ProfileUpdateSerializer,
    ChangePasswordSerializer, MyTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.contrib.auth import update_session_auth_hash

class RegisterAPIView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
    queryset = CustomUser.objects.all()

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = (permissions.AllowAny,)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProfileUpdateSerializer
        return UserSerializer

class ChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            if not user.check_password(old_password):
                return Response({'old_password': 'Wrong password.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            # Keep user logged in if using sessions (not required for JWT)
            try:
                update_session_auth_hash(request, user)
            except Exception:
                pass
            return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Optional: Logout using token blacklist (requires enabling blacklist app and migrations)
from rest_framework_simplejwt.tokens import RefreshToken

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#waste item views
# myapp/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .models import Item, PurchaseHistory
from .serializers import ItemSerializer, ItemCreateSerializer, PurchaseSerializer


# -------------------------
# Create Item
# -------------------------
class CreateItemAPIView(generics.CreateAPIView):
    serializer_class = ItemCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


# -------------------------
# User Item CRUD (own items only)
# -------------------------
class UserItemsAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(seller=self.request.user)


class ItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    queryset = Item.objects.all()

    def perform_update(self, serializer):
        item = self.get_object()
        if item.seller != self.request.user:
            raise PermissionError("You cannot edit another user's item.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.seller != self.request.user:
            raise PermissionError("You cannot delete another user's item.")
        instance.delete()


# -------------------------
# Marketplace Items (FILTERS ADDED)
# -------------------------
class MarketplaceAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Item.objects.all()

        category = self.request.query_params.get("category")
        status = self.request.query_params.get("status")
        search = self.request.query_params.get("search")

        if category and category != "All":
            queryset = queryset.filter(category__iexact=category)

        if status:
            queryset = queryset.filter(status__iexact=status)

        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset


# -------------------------
# Buy Item
# -------------------------
class BuyItemAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, item_id):
        user = request.user

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found"}, status=404)

        if item.status == "sold":
            return Response({"detail": "Item already sold"}, status=400)

        if item.seller == user:
            return Response({"detail": "You cannot buy your own item"}, status=400)

        if user.balance < item.price:
            return Response({"detail": "Insufficient balance"}, status=400)

        seller = item.seller

        # Atomic Transaction
        with transaction.atomic():
            user.balance -= item.price
            user.save()

            seller.balance += item.price
            seller.save()

            item.status = "sold"
            item.save()

            purchase = PurchaseHistory.objects.create(
                buyer=user,
                seller=seller,
                item=item,
                price=item.price
            )

        return Response(PurchaseSerializer(purchase).data, status=201)
