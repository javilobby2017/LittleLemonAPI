from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import Group, User
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes, action
from rest_framework import permissions, viewsets, status
from .serializers import GroupSerializer, UserSerializer, MenuItemSerializer, CartSerializer, OrderItem, OrderSerializer
from .models import MenuItem, Cart
from django.core.paginator import Paginator, EmptyPage

from rest_framework.permissions import IsAuthenticated


@api_view()
def single_item(request, id):
    item = get_object_or_404(MenuItem,pk=id)
    serialized_item = MenuItemSerializer(item)
    return Response(serialized_item.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message":"Some secert message"})

@api_view
@permission_classes([IsAuthenticated])
def manager_view(request):
    return Response({"message":"only Manager should see this"})



class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({"status": "Cart cleared."})

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show orders for the logged-in user
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)

        # Optional: Move items from Cart to OrderItem
        cart_items = Cart.objects.filter(user=self.request.user)
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
        cart_items.delete()