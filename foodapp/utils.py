# utils.py
from .models import Cart

def calculate_total_amount(user):
    cart_items = Cart.objects.filter(user=user)
    total_amount = sum(item.food.price * item.quantity for item in cart_items)
    return total_amount
