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

# ----------------- User Registration -----------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    parser_classes = [MultiPartParser, FormParser]

# ----------------- Profile -----------------
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

# ----------------- Marketplace -----------------
class MarketplaceView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.filter(status="available").order_by('-created_at')
        category = self.request.query_params.get('category')
        if category and category != 'All':
            queryset = queryset.filter(category=category)
        return queryset

# ----------------- Post Waste -----------------
class PostWasteView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='available')

# ----------------- Public Product Detail -----------------
class PublicProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# ----------------- Post Detail (Edit/Delete) -----------------
class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

# ----------------- Buy Product -----------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    buyer = request.user.profile
    seller = product.user.profile

    if product.user == request.user:
        return Response({"detail": "You cannot buy your own product."}, status=status.HTTP_400_BAD_REQUEST)

    if product.status != "available":
        return Response({"detail": "Product is not available."}, status=status.HTTP_400_BAD_REQUEST)

    if buyer.balance < product.price:
        return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)

    # Transaction
    buyer.balance -= product.price
    seller.balance += product.price
    buyer.save()
    seller.save()

    # Update product
    product.status = "sold"
    product.save()

    # Create order record
    Order.objects.create(
        product=product,
        buyer=request.user
    )

    return Response({"detail": "Product purchased successfully."}, status=status.HTTP_200_OK)

# ----------------- Order History -----------------
class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(buyer=self.request.user)

# ----------------- Post History -----------------
class PostHistoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)
