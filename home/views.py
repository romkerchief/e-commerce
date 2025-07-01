from home import models
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
import json
import requests #type: ignore
from .utils import *
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth
from django.contrib import messages
from .forms import ProductForm, ProductImage, ProductImageForm, FormShipping, ReviewForm
from customers.models import SellerProfile
from customers.views import seller_required
from django.forms import inlineformset_factory # Import inlineformset_factory
from django.views.generic import (
    TemplateView,
    DetailView,
    CreateView,
    UpdateView,
    ListView,
)
from django.urls import reverse_lazy


class HomeView(ListView):
    models = Product
    category = Category.objects.all()
    queryset = models.objects.all()
    extra_context = {
        'categories' : category
    }
    
    def get_queryset(self):
        request = self.request.GET
        if len(request) != 0:
            if next(iter(request)) == 'category':
                self.queryset = Product.objects.filter(category_id=self.request.GET['category'])

        return super().get_queryset()

    def get_ordering(self):
        request = self.request.GET
        if len(request) != 0:
            for i in request: 
                if i == 'more-filter':
                    ordering = [request["more-filter"]]
                    return ordering

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        
        request = self.request
        self.kwargs.update(self.extra_context)
        if len(request.GET) != 0:
            if next(iter(request.GET)) == 'category-id':
                context['active'] = Category.objects.get(id=request.GET['category-id'])
        
        # This part handles the cart display in the navbar
        # context.update(cartData(self.request))

        if self.template_name == 'home/indexhome.html':
            top_rated_products = Product.objects.annotate(
                average_rating=Avg('reviews__rating')
            ).filter(reviews__isnull=False).order_by('-average_rating')[:4] # Get top 4
            
            context['top_rated_list'] = top_rated_products
        
        return context

class ProductDetail(DetailView):
    model = Product
    template_name = 'home/detail.html'
    slug_url_kwarg = 'product_slug'

    def get_context_data(self, **kwargs):
        """
        This method prepares all the data needed to DISPLAY the page (GET request).
        """
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get reviews and calculate average rating
        reviews = product.reviews.all().order_by('-created_at')
        context['reviews'] = reviews
        context['review_form'] = ReviewForm()
        aggregation = reviews.aggregate(
            average_rating=Avg('rating'), 
            review_count=Count('id')
        )
        context['average_rating'] = aggregation.get('average_rating') or 0
        context['review_count'] = aggregation.get('review_count') or 0

        # Your existing code for the image carousel
        carousel_image_urls = []
        if product.main_image:
            carousel_image_urls.append(product.main_image.url)
        additional_images = ProductImage.objects.filter(product=product)
        for img_instance in additional_images:
            if img_instance.imageURL not in carousel_image_urls:
                carousel_image_urls.append(img_instance.imageURL)
        context["carousel_image_urls"] = carousel_image_urls
        
        return context

    def post(self, request, *args, **kwargs):
        """
        This method handles the form submission for new reviews (POST request).
        """
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to post a review.")
            return redirect('customers:customer_login')

        product = self.get_object()
        form = ReviewForm(request.POST)

        # Restriction logic for seller
        if product.seller == request.user:
            messages.error(request, "You cannot review your own product.")
            return redirect('homey:product_detail', category_slug=product.category.slug, product_slug=product.slug)

        if form.is_valid():
            # Check if user has already reviewed this product
            if Review.objects.filter(product=product, user=request.user).exists():
                messages.error(request, "You have already submitted a review for this product.")
            else:
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, "Thank you! Your review has been submitted.")
        else:
            messages.error(request, "There was an error with your submission. Please check the rating and comment fields.")

        # Redirect back to the same product page to see the new review
        return redirect('homey:product_detail', category_slug=product.category.slug, product_slug=product.slug)
    
def post(self, request, *args, **kwargs):
    # This method handles the form submission for new reviews
    if not request.user.is_authenticated:
        return redirect('customers:customer_login')

    product = self.get_object()
    form = ReviewForm(request.POST)

    # restriction logic
    if product.seller == request.user:
        messages.error(request, "You cannot review your own product.")
        return redirect('homey:product_detail', category_slug=product.category.slug, product_slug=product.slug)

    if form.is_valid():
        if Review.objects.filter(product=product, user=request.user).exists():
            messages.error(request, "You have already reviewed this product.")
        else:
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thank you! Your review has been submitted.")
    else:
        messages.error(request, "There was an error with your submission. Please check your rating and comment.")

    return redirect('homey:product_detail', category_slug=product.category.slug, product_slug=product.slug)

def fakeStoreAPI():
    # This function will store data from api to django.
    responses=requests.get('https://fakestoreapi.com/products?limit=5').json()

    for response in responses:
        category = Category.objects
        obj = Product.objects.create(
            category=Category.objects.get(name=response['category']),
            name=response['title'],
            img_product1=response['image'],
            price=response['price'],
            description=response['description']
        )
        obj.save()
        # try:
        #     cat,created = Category.objects.get_or_create(name=response['category'])

        #     print('mantap gann!')
        # except:
        #     print('error gan')
    print('sipp')

# --- Dashboard & Statistics ---

def check_is_pimpinan(user):
    """
    Checks if the user is a staff member and belongs to the 'Pimpinan' division.
    """
    # User must be a Django staff user first.
    if not user.is_staff:
        return False
    try:
        # This checks if the user's profile is linked to the 'Pimpinan' division.
        # It assumes a Profile model is linked to your User model (e.g., user.profile)
        # and that the Profile has a ForeignKey to a Division model.
        return user.profile.division.name == 'Pimpinan'
    except AttributeError:
        # This handles cases where user.profile doesn't exist, or user.profile.division is None.
        return False

@login_required
@user_passes_test(check_is_pimpinan)
def dashboard_statistik(request):
    """
    View for the analytics dashboard, accessible only by 'Pimpinan'.
    """
    # Data for Pie Chart: Sales by Category
    category_sales = OrderItem.objects.filter(order__complete=True)\
        .values('product__category__name')\
        .annotate(total_sales=Sum('get_total'))\
        .order_by('-total_sales')

    # Data for Line Chart: Sales per month
    sales_per_month = Order.objects.filter(complete=True)\
        .annotate(month=TruncMonth('date_ordered'))\
        .values('month')\
        .annotate(total_sales=Sum('get_cart_totals'))\
        .order_by('month')

    # Data for Bar Chart: Top 5 Best-Selling Products
    top_products = OrderItem.objects.filter(order__complete=True)\
        .values('product__name')\
        .annotate(total_quantity=Sum('quantity'))\
        .order_by('-total_quantity')[:5]

    context = {
        'pie_chart_labels': json.dumps([item['product__category__name'] for item in category_sales]),
        'pie_chart_data': json.dumps([float(item['total_sales']) for item in category_sales]),
        'line_chart_labels': json.dumps([s['month'].strftime('%B %Y') for s in sales_per_month]),
        'line_chart_data': json.dumps([float(s['total_sales']) for s in sales_per_month]),
        'bar_chart_labels': json.dumps([p['product__name'] for p in top_products]),
        'bar_chart_data': json.dumps([p['total_quantity'] for p in top_products]),
    }
    return render(request, 'home/dashboard.html', context)


@login_required
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    default_status = OrderStatus.objects.filter(is_default=True).first()
    if not default_status:
        messages.error(request, "System error: Default order status not configured.")
        return JsonResponse({'error': 'Default order status not configured'}, status=500)

    customer = request.user
    product = Product.objects.get(id=productId)
    # Use the default status (e.g., "Pending") for cart operations
    order, created = Order.objects.get_or_create(user=customer, status=default_status)

    orderItem,created = OrderItem.objects.get_or_create(order=order, product=product)
    if action =='add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item Was Added', safe=False)

# --- Seller Product Management Views ---


@login_required
@seller_required
def seller_product_create(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, prefix="product")
        # For creating a new product, we don't have an instance yet for the formset
        ImageFormSet = inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=3, can_delete=True)
        image_formset = ImageFormSet(request.POST, request.FILES, prefix="images")

        if product_form.is_valid() and image_formset.is_valid():
            product = product_form.save(commit=False)
            product.seller = request.user
            product.save() # Save the product first to get a PK

            # Save the image formset
            image_formset.instance = product
            image_formset.save()

            messages.success(request, f"Product '{product.name}' created successfully with images.")
            return redirect('seller_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        product_form = ProductForm(prefix="product")
        ImageFormSet = inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=3, can_delete=True)
        image_formset = ImageFormSet(prefix="images")
    
    context = {
        'product_form': product_form,
        'image_formset': image_formset,
        'action': 'Create'
    }
    return render(request, 'sellers/product_form.html', context)

@login_required
@seller_required
def seller_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    ImageFormSet = inlineformset_factory(Product, ProductImage, form=ProductImageForm, extra=1, can_delete=True)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product, prefix="product")
        image_formset = ImageFormSet(request.POST, request.FILES, instance=product, prefix="images")

        if product_form.is_valid() and image_formset.is_valid():
            product_form.save()
            image_formset.save()
            messages.success(request, f"Product '{product.name}' updated successfully.")
            return redirect('seller_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        product_form = ProductForm(instance=product, prefix="product")
        image_formset = ImageFormSet(instance=product, prefix="images")
    
    context = {
        'product_form': product_form,
        'image_formset': image_formset,
        'product': product,
        'action': 'Update'
    }
    return render(request, 'sellers/product_form.html', context)

@login_required
@seller_required
def seller_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        product_name = product.name # Get name before deleting for the message
        product.delete()
        messages.success(request, f"Product '{product_name}' deleted successfully.")
        return redirect('seller_dashboard')
    
    context = {
        'product': product
    }
    return render(request, 'sellers/product_confirm_delete.html', context)

# --- Public Store Page View ---
def store_detail_view(request, store_slug):
    try:
        seller_profile = get_object_or_404(SellerProfile, slug=store_slug)
        # Access the user (seller) through the profile, then the SellerProfile
        seller_user = seller_profile.profile.user
        products = Product.objects.filter(seller=seller_user).order_by('-upload_time')
        
        context = {
            'seller_profile': seller_profile,
            'products': products,
        }
        return render(request, 'home/store_detail.html', context)
    except SellerProfile.DoesNotExist:
        # Handle case where store slug doesn't exist, maybe redirect to a 404 page or homepage
        messages.error(request, "The requested store does not exist.")
        return redirect('homey:index')

@login_required
def cart(request):
    """
    This is the new dedicated view for the shopping cart.
    """
    try:
        # We look for an order with the default "in cart" status
        cart_status = OrderStatus.objects.get(is_default=True)
        order = Order.objects.get(user=request.user, status=cart_status)
        items = order.orderitem_set.all()
    except (OrderStatus.DoesNotExist, Order.DoesNotExist):
        # If the user has no active cart, we create placeholder objects to avoid errors
        order = {'get_cart_totals': 0, 'get_cart_items': 0}
        items = []
        messages.info(request, "Your cart is currently empty.")
        
    context = {'items': items, 'order': order}
    return render(request, 'home/cart.html', context)

# In home/views.py
@login_required
def checkout(request):
    """
    Step 1 of Checkout: Collect Shipping Information
    """
    try:
        # THE FIX IS ON THIS LINE: Use is_default=True instead of a hardcoded name
        cart_status = OrderStatus.objects.get(is_default=True)
        order = Order.objects.get(user=request.user, status=cart_status)
        items = order.orderitem_set.all()

        if items.count() == 0:
            messages.warning(request, "Your cart is empty. Please add items before checking out.")
            return redirect('homey:cart')
    except (OrderStatus.DoesNotExist, Order.DoesNotExist):
        messages.error(request, "You do not have an active order.")
        return redirect('homey:cart')

    # The rest of the function remains the same
    if request.method == 'POST':
        form = FormShipping(request.POST)
        if form.is_valid():
            request.session['shipping_address'] = form.cleaned_data
            return redirect('homey:payment')
    else:
        # Check if shipping address is already in the session from a previous step
        if 'shipping_address' in request.session:
            form = FormShipping(initial=request.session['shipping_address'])
        else:
            # If not, initialize with the user's email as a default
            form = FormShipping(initial={'email': request.user.email})
        
    context = {'form': form, 'items': items, 'order': order}
    return render(request, 'home/checkout.html', context)

@login_required
def process_payment(request):
    """
    Step 2 of Checkout: Choose Payment and Finalize Order
    """
    try:
        # THE FIX IS ON THIS LINE: Use is_default=True here as well for consistency
        cart_status = OrderStatus.objects.get(is_default=True)
        order = Order.objects.get(user=request.user, status=cart_status)
        order_items = order.orderitem_set.all()
    except (OrderStatus.DoesNotExist, Order.DoesNotExist):
        messages.error(request, "Your cart is empty or the order could not be found.")
        return redirect('homey:cart')
    
    # The rest of the function remains the same
    shipping_address_data = request.session.get('shipping_address')
    if not shipping_address_data:
        messages.error(request, "Shipping address is missing. Please fill it out first.")
        return redirect('homey:checkout')

    if request.method == 'POST':
        # ... all the POST logic is correct and stays the same ...
        shipping_address = ShippingAddress.objects.create(
            user=request.user,
            order=order,
            address=shipping_address_data['address'],
            kota=shipping_address_data['kota'],
            kode_pos=shipping_address_data['kode_pos'],
            email=shipping_address_data['email']
        )
        
        processing_status, _ = OrderStatus.objects.get_or_create(name="Processing")
        order.status = processing_status
        order.save()

        # Pass the payment method to the confirmation page via a temporary session key
        # and clear the shipping address data now that it's saved to the database.
        request.session['last_order_payment_method'] = request.POST.get('paymentMethod')
        if 'shipping_address' in request.session:
            del request.session['shipping_address']

        return redirect('homey:order_confirmation', transaction_id=order.transaction_id)

    context = {
        'order': order, 
        'order_items': order_items, 
        'shipping_address': shipping_address_data
    }
    return render(request, 'home/payment.html', context)

@login_required
def order_confirmation(request, transaction_id):
    """
    Step 3: Show a "Thank You" page and mock QR code if needed.
    """
    try:
        order = Order.objects.get(user=request.user, transaction_id=transaction_id)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('homey:index')

    # Pop the payment method from the session.
    # .pop() gets the value and deletes the key in one atomic operation.
    # It returns None if the key doesn't exist (e.g., if the user revisits the page).
    payment_method = request.session.pop('last_order_payment_method', None)

    context = {'order': order, 'payment_method': payment_method}
    return render(request, 'home/order_confirmation.html', context)