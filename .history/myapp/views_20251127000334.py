# myapp/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from .models import CustomUser, Item, PurchaseHistory
from .serializers import (
    RegisterSerializer, UserSerializer, ProfileUpdateSerializer,
    ChangePasswordSerializer, MyTokenObtainPairSerializer,
    ItemSerializer, ItemCreateSerializer, PurchaseSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash


# -------------------------------
# Register
# -------------------------------
class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    queryset = CustomUser.objects.all()


# -------------------------------
# Login (JWT)
# -------------------------------
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


# -------------------------------
# Profile
# -------------------------------
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProfileUpdateSerializer
        return UserSerializer


# -------------------------------
# Change Password
# -------------------------------
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response({"old_password": "Wrong password."}, status=400)

            user.set_password(serializer.validated_data["new_password"])
            user.save()

            update_session_auth_hash(request, user)
            return Response({"detail": "Password updated successfully."})
        return Response(serializer.errors, status=400)


# -------------------------------
# Logout
# -------------------------------
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get("refresh"))
            token.blacklist()
            return Response({"detail": "Logged out."})
        except Exception:
            return Response({"detail": "Invalid token"}, status=400)


# -------------------------------
# Create Item
# -------------------------------
class CreateItemAPIView(generics.CreateAPIView):
    serializer_class = ItemCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


# -------------------------------
# User Items
# -------------------------------
class UserItemsAPIView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(seller=self.request.user)


# -------------------------------
# Item Detail Update/Delete
# -------------------------------
class ItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "_id"
    queryset = Item.objects.all()

    def perform_update(self, serializer):
        item = self.get_object()
        if item.seller != self.request.user:
            raise PermissionError("Not allowed.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.seller != self.request.user:
            raise PermissionError("Not allowed.")
        instance.delete()


# -------------------------------
# Marketplace Items
# -------------------------------
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


# -------------------------------
# Buy Item
# -------------------------------
class BuyItemAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, item_id):
        user = request.user

        try:
            item = Item.objects.get(_id=item_id)
        except Item.DoesNotExist:
            return Response({"detail": "Item not found"}, status=404)

        if item.status == "sold":
            return Response({"detail": "Item already sold"}, status=400)

        if item.seller == user:
            return Response({"detail": "You cannot buy your own item"}, status=400)

        if user.balance < item.price:
            return Response({"detail": "Insufficient balance"}, status=400)

        seller = item.seller

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
