from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Order, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# serializers.py


from rest_framework import serializers
from .models import UserProfile

# serializers.py

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    email = serializers.EmailField(source="user.email")
    # ADD THIS LINE 👇
    id = serializers.IntegerField(source="user.id", read_only=True) 
    
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        # ADD 'id' TO FIELDS 👇
        fields = ["id", "username", "email", "phone_number", "avatar","balance"]

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            # This automatically detects if it's localhost, 10.0.2.2, or a real domain
            return request.build_absolute_uri(obj.avatar.url) 
        return None



class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    phoneNumber = serializers.CharField(write_only=True)
    avatar = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'phoneNumber', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        phone = validated_data.pop('phoneNumber')
        avatar = validated_data.pop('avatar', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        # Save Profile
        user.profile.phone_number = phone
        if avatar:
            user.profile.avatar = avatar
        user.profile.save()

        return user


class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
