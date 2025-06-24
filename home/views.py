from home import models
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
import json
import requests #type: ignore
from .utils import *
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.contrib import messages
from .forms import ProductForm, ProductImage, ProductImageForm, FormShipping
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

    def get_context_data(self,*args,**kwargs):
        # fakeStoreAPI()
        request = self.request
        context = super().get_context_data()
        # print("bum",context,"bum") 
        self.kwargs.update(self.extra_context)
        kwargs = self.kwargs
        for product in context["product_list"]:
            product_images = ProductImage.objects.filter(product=product.pk)
            print(product_images)
        if len(request.GET) != 0:
            if next(iter(request.GET)) == 'category-id':
                context['active'] = Category.objects.get(id=request.GET['category-id'])
        context.update(cartData(self.request))
        if context['items'] != "0":
            context.update(mergeFunction(request,context['items']))
        return context

class ProductDetail(TemplateView):
    model = Product
    def get_context_data(self,**kwargs):
        context = super().get_context_data()
        # Use product_slug from URL kwargs, category_slug is also available in kwargs if needed for filtering
        # Assuming product slugs are unique, category_slug might be for URL structure/SEO
        context['product'] = self.model.objects.get(slug=kwargs['product_slug'])
        product_obj = context['product']

        # Prepare images for the carousel
        carousel_image_urls = []
        if product_obj.main_image:
            carousel_image_urls.append(product_obj.main_image.url)
        
        # Add images from ProductImage, excluding any that might be duplicates of main_image if logic was more complex
        additional_images = ProductImage.objects.filter(product=product_obj.pk)
        for img_instance in additional_images:
            if img_instance.imageURL not in carousel_image_urls: # Avoid duplicates if main_image was also a ProductImage
                 carousel_image_urls.append(img_instance.imageURL)

        context["carousel_image_urls"] = carousel_image_urls
        exclude_object = Product.objects.exclude(slug=kwargs['product_slug'])
        paginator = Paginator(exclude_object,4)
        prod_list = paginator.get_page(None)
        context['product_list']=prod_list
        return context

@login_required
def ShippingView(request):
    """
    Handles the shipping address form submission.
    It validates the form, geocodes the address to get coordinates,
    and saves the shipping address to the session before redirecting to the payment page.
    """
    context = {}
    # Get cart data for the order summary and to link the shipping address
    context.update(cartData(request))

    # If cart is empty, redirect back to cart page
    if not context.get('items'):
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('homey:cart')
    
    if request.method == 'POST':
        form = FormShipping(request.POST)
        if form.is_valid():
            # Don't save to DB yet, we need to add user and order
            shipping = form.save(commit=False)
            shipping.user = request.user
            shipping.order = context['order']
            shipping.save() # Save the complete object, now with lat/lon if found.
            request.session['shipping_address_id'] = shipping.id  # Save shipping ID to session
            return redirect('homey:payment')
    else:
        # Pre-populate form with user's email for convenience
        form = FormShipping(initial={'email': request.user.email})

    context['form'] = form
    return render(request, 'home/checkout.html', context)
 
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

@login_required
def payment_view(request):
    """
    Handles payment processing and order confirmation.
    """
    shipping_address_id = request.session.get('shipping_address_id')
    if not shipping_address_id:
        messages.error(request, "Please enter shipping information first.")
        return redirect('homey:checkout')

    try:
        shipping_address = ShippingAddress.objects.get(pk=shipping_address_id, user=request.user)
        order = Order.objects.get(user=request.user, status__is_default=True)
        order_items = OrderItem.objects.filter(order=order)
    except (ShippingAddress.DoesNotExist, Order.DoesNotExist):
        messages.error(request, "Invalid checkout session. Please try again.")
        return redirect('homey:checkout')

    if request.method == 'POST':
        selected_payment_method = request.POST.get('selectedPaymentMethod')

        if selected_payment_method == 'creditCard':
            # Here you would integrate with a payment gateway (e.g., Stripe, Midtrans, etc.)
            # For now, we'll simulate success.
            messages.info(request, "Credit Card payment initiated (simulated).")
            CompleteOrder(request) # Mark order as complete
            del request.session['shipping_address_id']
            messages.success(request, "Payment successful! Your order has been placed.")
            return redirect('homey:index') # Redirect to a confirmation page later
        elif selected_payment_method == 'cashOnDelivery':
            # For COD, simply mark the order as complete and provide instructions.
            CompleteOrder(request) # Mark order as complete
            del request.session['shipping_address_id']
            messages.success(request, "Your order has been placed! Please prepare cash for delivery.")
            return redirect('homey:index') # Redirect to a confirmation page later
        elif selected_payment_method == 'eMoney':
            # For e-money, you might redirect to a page with QR codes or payment instructions.
            messages.info(request, "E-Money payment selected. Instructions will be provided on the confirmation page.")
            CompleteOrder(request) # Mark order as complete
            del request.session['shipping_address_id']
            messages.success(request, "Your order has been placed! Please follow e-money instructions.")
            return redirect('homey:index') # Redirect to a confirmation page later
        else:
            messages.error(request, "Invalid payment method selected.")
            return redirect('homey:payment') # Stay on payment page
    context = {
        'shipping_address': shipping_address,
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'home/payment.html', context)

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