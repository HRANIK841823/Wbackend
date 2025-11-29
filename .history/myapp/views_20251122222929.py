from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import User
from .models import Product, Order, UserProfile
from .serializers import (
    UserProfileSerializer,
    ProductSerializer,
    RegisterSerializer,
    OrderSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        print("========== DEBUG ==========")
        print("DATA:", request.data)
        print("FILES:", request.FILES)
        print("===========================")
        return super().post(request, *args, **kwargs)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user.profile)
        return Response(serializer.data)


class MarketplaceView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Product.objects.filter(status="available").order_by('-created_at')
        category = self.request.query_params.get("category")
        if category and category != "All":
            qs = qs.filter(category=category)
        return qs


class PostWasteView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='available')


class PublicProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=404)

    buyer = request.user.profile
    seller = product.user.profile

    if product.user == request.user:
        return Response({"detail": "Cannot buy your own product."}, status=400)

    if product.status != "available":
        return Response({"detail": "Not available."}, status=400)

    if buyer.balance < product.price:
        return Response({"detail": "Insufficient balance."}, status=400)

    # Transfer
    buyer.balance -= product.price
    seller.balance += product.price
    buyer.save()
    seller.save()

    product.status = "sold"
    product.save()

    Order.objects.create(product=product, buyer=request.user)

    return Response({"detail": "Purchase successful."})


class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)


class PostHistoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)
