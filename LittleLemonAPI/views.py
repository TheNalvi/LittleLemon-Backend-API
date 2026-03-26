from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth.models import User, Group
from .models import MenuItem, Cart, OrderItem, Order
from .serializers import RegisterSerializer, MenuItemSerializer, UserIdSerializer, CartItemSerializer, OrderSerializer, OrderManagerSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import isManagerOrReadOnly, isManagerOnly
from rest_framework.exceptions import NotFound
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .pagination import StandardResultsSetPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = RegisterSerializer(request.user)
        return Response(serializer.data)
    
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'featured']
    search_fields = ['title', 'category__title']
    ordering_fields = ['price', 'category']
    pagination_class = StandardResultsSetPagination
    
    permission_classes = [isManagerOrReadOnly]
    
class SingeMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    permission_classes = [isManagerOrReadOnly]
    
class GroupManagementView(generics.ListCreateAPIView):
    serializer_class = RegisterSerializer
    def get_group(self):
        group_name = self.kwargs.get('group_name')
        
        if not group_name:
            return None
        try:
            return Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return None
        
    def get_queryset(self):
        group = self.get_group()
        if not group:
            raise NotFound(detail="Group is not found")
        return group.user_set.all()
    
    def post(self, request, *args, **kwargs):
        group_to_modify = self.get_group()
        if not group_to_modify:
            return Response({"message": "Group is not found"}, status=404)
        serializer = UserIdSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data['user_id']
        try:
            user_to_add = User.objects.get(pk=user_id)
            group_to_modify.user_set.add(user_to_add)
            response_serializer = RegisterSerializer(user_to_add)
            return Response(response_serializer.data, status=201)
        except User.DoesNotExist:
            return Response({"message": "User is not found"}, status=404)
    permission_classes = [isManagerOnly]
    
class ManagersRemoveView(generics.DestroyAPIView):
    permission_classes = [isManagerOnly]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        group_name = self.kwargs['group_name']
        user = get_object_or_404(User, pk=pk)
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return Response({"message": "Group is not found"})
        group.user_set.remove(user)
        return Response({"message": f"User {user.username} has been deleted from manager group"}, status=200)
    
class CartMenuItemView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        menu_item = serializer.validated_data['menuitem']
        quantity = serializer.validated_data['quantity']
        
        unit_price = menu_item.price
        price = quantity * unit_price
        
        serializer.save(user=self.request.user,price=price, unit_price=unit_price)
    
    def delete(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response({"message": "The cart has been deleted"})
    
class OrderMenuItemView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'user', 'delivery_crew', 'date']
    search_fields = ['user__username', 'order_items__menuitem__title']
    ordering_fields = ['total', 'date', 'status']
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        if user.groups.filter(name='delivery-crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"message:": "The cart is empty"})
        
        with transaction.atomic():
            total_price = sum([item.price for item in cart_items])
            
            order = Order.objects.create(user=user, total=total_price)
            
            order_items = []
            for item in cart_items:
                order_items.append(OrderItem(
                    order=order,
                    menuitem = item.menuitem,
                    quantity = item.quantity,
                    unit_price = item.unit_price,
                    price = item.price
                ))
                
            OrderItem.objects.bulk_create(order_items)
            cart_items.delete()
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.user.groups.filter(name='manager').exists():
            return OrderManagerSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()
        if user.groups.filter(name='delivery-crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)
            
    def patch(self, request, *args, **kwargs):
        user = request.user
        
        if user.groups.filter(name='manager').exists():
            return super().partial_update(request, *args, **kwargs)
        
        if user.groups.filter(name='delivery-crew'):
            if len(request.data) > 1 or 'status' not in request.data:
                return Response({"message": "Delivry-crew can only update the status fields"}, status=status.HTTP_400_BAD_REQUEST)
            
            return super().partial_update(request, *args, **kwargs)
        return Response({"message": "Customers cannot edit orders"}, status=status.HTTP_403_FORBIDDEN)
    
    def delete(self, request, *args, **kwargs):
        if request.user.groups.filter(name='manager').exists():
            return super().destroy(request, *args, **kwargs)
        return Response({"message": "Only managers can delete orders"}, status=status.HTTP_403_FORBIDDEN)
    
    def put(self, request, *args, **kwargs):
        if request.user.groups.filter(name='manager').exists():
            return super().update(request, *args, **kwargs)
        return Response({"message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class UsersView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer