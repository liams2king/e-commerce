from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Product, CartItem, Cart
import unicodedata

def index(request):
    products = Product.objects.all()
    item_name = request.GET.get('item_name', '')

    if item_name:
        item_name_normalized = unicodedata.normalize('NFKD', item_name).encode('ASCII', 'ignore').decode('utf-8').lower()
        products = [p for p in products if item_name_normalized in unicodedata.normalize('NFKD', p.title).encode('ASCII', 'ignore').decode('utf-8').lower()]

    paginator = Paginator(products, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_cart_quantity = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            total_cart_quantity = sum(item.quantity for item in cart.cartitem_set.all())
        except Cart.DoesNotExist:
            pass

    return render(request, 'shop/index.html', {
        'products': page_obj,
        'total_cart_quantity': total_cart_quantity,
    })
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"🛒 {product.title} ajouté au panier avec succès !")
    return redirect('home')

@login_required
def cart_view(request):
    cart = request.user.cart
    cart_items = cart.cartitem_set.all()
    total = sum(item.get_total_price for item in cart_items)


    return render(request, 'shop/cart.html', {
        'items': cart_items,
        'total': total
    })

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart=request.user.cart)
    item.delete()
    messages.success(request, "Produit supprimé du panier.")
    return redirect('cart_view')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Bienvenue ! Votre compte a été créé avec succès.")
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'shop/register.html', {'form': form})


@login_required
def update_cart(request):
    if request.method == 'POST':
        cart = request.user.cart
        for item in cart.cartitem_set.all():
            key = f"quantity_{item.id}"
            if key in request.POST:
                try:
                    qty = int(request.POST[key])
                    if qty > 0:
                        item.quantity = qty
                        item.save()
                    else:
                        # Si la quantité est 0 ou négative, supprimer l'item
                        item.delete()
                except ValueError:
                    pass  # Ignore si la quantité n'est pas un entier valide
    return redirect('cart_view')