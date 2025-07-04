from .models import Cart

def cart_item_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.cartitem_set.count()
        except Cart.DoesNotExist:
            count = 0
    else:
        count = 0
    return {'cart_item_count': count}


def cart_totals(request):
    total_cart_price = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_cart_price = sum(item.get_total_price for item in cart.cartitem_set.all())
        except Cart.DoesNotExist:
            total_cart_price = 0
    return {'total_cart_price': total_cart_price}