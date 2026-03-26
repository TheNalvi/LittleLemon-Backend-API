from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Cart, OrderItem, Order

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
    
    def create(self, validated_data):
        user = User(
            username = validated_data['username'],
            email = validated_data.get('email')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"
        
class UserIdSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    
class CartItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']
        
        read_only_fields = ['user']
        
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']
        
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['user', 'total', 'date']
        
class OrderManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'total', 'date', 'status', 'delivery_crew', 'order_items']
        read_only_fields = ['id', 'user', 'total', 'date', 'order_items']