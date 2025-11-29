from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model, update_session_auth_hash
from .models import Product
from .serializers import (
    UserRegistrationSerializer, 
    UserProfileSerializer, 
    ChangePasswordSerializer, 
    ProductSerializer
)

User = get_user_model()

# --- AUTH VIEWS ---

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if user.check_password(serializer.data.get('old_password')):
            user.set_password(serializer.data.get('new_password'))
            user.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)

# --- MARKETPLACE VIEWSET ---
from bson.objectid import ObjectId
from rest_framework.exceptions import NotFound # Import NotFound

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'title', 'description']
    lookup_field = 'id'
    
    # In myapp/views.py (inside ProductViewSet)

    def get_object(self):
        # 1. Get the lookup value (the ObjectId string) from the URL
        # All lines inside the function must be indented 4 spaces
        lookup_value = self.kwargs[self.lookup_field] 
        
        # Check if the lookup value is a valid ObjectId format
        if not ObjectId.is_valid(lookup_value):
            # Indented 8 spaces (inside the 'if' block)
            raise NotFound(detail="Not found.")

        # Convert the string to a MongoDB ObjectId instance
        object_id = ObjectId(lookup_value)

        # Start the 'try' block
        try:
            # Query the database using the field 'id'
            obj = Product.objects.get(id=object_id) 
            # This 'return' is inside the 'try' block (12 spaces)
            return obj
        
        # Start the 'except' block (aligned with 'try')
        except Exception as e:
            # Logging is inside the 'except' block (8 spaces)
            print(f"!!! CRASH DEBUG !!!: {type(e).__name__}: {e}") 
            # Raising the exception (8 spaces)
            raise NotFound(detail="Product not found.")
    def get_queryset(self):
        """
        Custom Queryset logic:
        1. Default: Show all 'available' items.
        2. Filters: category (via query param).
        3. Search: handled by filter_backends.
        """
        queryset = Product.objects.all()
        
        # Filter by Category if provided (e.g. ?category=Electronics)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # By default, for the main list, we only show 'available' items
        # UNLESS looking at specific history (handled in actions below)
        if self.action == 'list':
            return queryset.filter(status='available')
        
        return queryset

    def perform_create(self, serializer):
        # Automatically set seller to current user
        serializer.save(seller=self.request.user, status='available')

    def perform_update(self, serializer):
        # Users can only update their own items
        if self.get_object().seller == self.request.user:
            serializer.save()
        else:
            raise permissions.PermissionDenied("You cannot edit this item.")

    def perform_destroy(self, instance):
        # Users can only delete their own items
        if instance.seller == self.request.user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You cannot delete this item.")

    # --- CUSTOM ACTIONS ---

    @action(detail=True, methods=['post'])
    def buy(self, request, id=None): # Use 'id' instead of 'pk' for consistency with lookup_field
        """
        Logic to buy an item:
        1. Check if available.
        2. Check balance.
        3. Deduct balance, update status, set buyer.
        """
        
        # 1. Retrieve objects (using get_object() which handles ObjectId conversion)
        try:
            product = self.get_object() 
        except NotFound:
             return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
             
        buyer = request.user

        # Checks
        if product.status != 'available':
            return Response({'error': f'Item status is "{product.status}", purchase denied.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if product.seller == buyer:
            return Response({'error': 'You cannot buy your own item'}, status=status.HTTP_400_BAD_REQUEST)

        # Assuming 'balance' is a field on your custom User model
        if not hasattr(buyer, 'balance') or buyer.balance < product.price:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        # --- Transaction Logic ---
        # NOTE: Using a database transaction is ideal, but simplified here for MongoDB (which may not support ACID transactions across collections)
        try:
            # 1. Deduct from Buyer
            buyer.balance -= product.price
            buyer.save()

            # 2. Add to Seller
            # Fetch the seller again to ensure we have a fresh, savable model instance
            seller = product.seller
            seller.balance += product.price
            seller.save()

            # 3. Update Product
            product.status = 'sold'
            # Assign the buyer's actual User object to the 'buyer' field
            product.buyer = buyer 
            product.save()

            return Response({'message': 'Purchase successful!', 'new_balance': buyer.balance}, status=status.HTTP_200_OK)
            
        # Catch any exceptions during the save operations
        except Exception as e:
            # Log the full error for debugging
            print(f"!!! TRANSACTION CRASH DEBUG !!!: {type(e).__name__}: {e}")
            
            # You might need to add logic here to "rollback" the transaction 
            # (e.g., if buyer.save() succeeds but product.save() fails)
            
            return Response(
                {'error': 'A server error occurred during the transaction. Please contact support.', 
                 'detail': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def my_sell_history(self, request):
        """
        Show items the user has posted (Sold or Available)
        """
        products = Product.objects.filter(seller=request.user).order_by('-created_at')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    # @action(detail=False, methods=['get'])
    # def my_purchase_history(self, request):
    #     """
    #     Show items the user has bought
    #     """
    #     products = Product.objects.filter(buyer=request.user).order_by('-created_at')
    #     serializer = self.get_serializer(products, many=True)
    #     return Response(serializer.data)
    @api_view(['GET'])
    def my_purchase_history(request):

        user_id = request.user.id  # this is string
        user_object_id = ObjectId(user_id)  # convert to ObjectId

        products = Product.objects.filter(buyer_id=user_object_id)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)