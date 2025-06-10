from home import models
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from customers.views import staff_member_required
from customers.forms import OrderStatusUpdateForm
import json
import requests #type: ignore
from .utils import *
from django.contrib import messages
from .forms import ProductForm
from .forms import ProductImageForm # Import ProductImageForm
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
        context['product'] = self.model.objects.get(slug=kwargs['slug'])
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
        exclude_object = Product.objects.exclude(slug=kwargs['slug'])
        paginator = Paginator(exclude_object,4)
        prod_list = paginator.get_page(None)
        context['product_list']=prod_list
        return context

@login_required
@staff_member_required # Or your specific staff decorator
def staff_order_detail_view(request, order_id):
    # Use pk or transaction_id based on your URL configuration.
    # The template uses order.transaction_id for display, but the URL might use pk (id).
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    # ShippingAddress might not exist for every order, handle gracefully.
    try:
        # Assuming a OneToOne or ForeignKey from ShippingAddress to Order.
        # If Order has a ForeignKey to ShippingAddress, it would be order.shippingaddress
        shipping_address = ShippingAddress.objects.get(order=order)
    except ShippingAddress.DoesNotExist:
        shipping_address = None
    except ShippingAddress.MultipleObjectsReturned:
        # Handle case if multiple shipping addresses are linked, though ideally this shouldn't happen.
        shipping_address = ShippingAddress.objects.filter(order=order).first()


    if request.method == 'POST':
        status_form = OrderStatusUpdateForm(request.POST, instance=order)
        if status_form.is_valid():
            status_form.save()
            messages.success(request, f"Order '{order.transaction_id}' status has been updated successfully.")
            # Redirect to the same page to show the update and success message.
            return redirect('staff_order_detail', order_id=order.id)
        else:
            messages.error(request, "Failed to update order status. Please review the errors below.")
    else:
        status_form = OrderStatusUpdateForm(instance=order)

    context = {
        'order': order,
        'order_items': order_items,
        'shipping_address': shipping_address,
        'status_form': status_form,
    }
    return render(request, 'staff/staff_order_detail.html', context)

@login_required
def ShippingView(request):
    context = {}
    form = FormShipping
    cart = cartData
    context.update(cart(request))
    if request.method == 'POST':
        form = FormShipping(request.POST)
        if form.is_valid():
            customer = request.user
            shipping,created = ShippingAddress.objects.get_or_create(
                user=customer,
                order=context['order'],
                email=request.POST.get('email'),
                kode_pos=request.POST.get('kode_pos'),
                kota=request.POST.get('kota'),
                address=request.POST.get('address'),
            )         
            shipping.save()
            CompleteOrder(request)
            return redirect('homey:index')
    context['form']=form
 
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