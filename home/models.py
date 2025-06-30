from django.db import models
from django.utils.text import slugify
from django.db.models.base import ModelState
from django.contrib.auth.models import User
from django.db.models.fields import NullBooleanField
import random
from django.http import JsonResponse, HttpResponseRedirect



class Category(models.Model):
    name            = models.CharField(max_length=255,unique=True)
    logo_category   = models.ImageField(null=True,blank=True,upload_to='logo/')
    slug            = models.SlugField(null=True,blank=True)

    @property
    def imageURL(self):
        try:
            url = self.logo_category.url
        except:
            url = ''
        return url

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    category        = models.ForeignKey(Category,related_name='product', on_delete=models.CASCADE)
    seller          = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    name            = models.CharField(max_length=255,unique=True)
    old_price       = models.DecimalField(blank=True,null=True,max_digits=12,decimal_places=2)
    price           = models.DecimalField(max_digits=12,decimal_places=2)
    main_image      = models.ImageField(upload_to='images/', blank=True, null=True)
    description     = models.TextField()
    upload_time     = models.DateField(auto_now_add=True)
    stock           = models.IntegerField(default=1)
    slug            = models.SlugField(blank=True)

    @property
    def imageThumbnail(self):
        images = ProductImage.objects.filter(product=self.pk)
        if images.exists():
            return images[0].imageURL
        return '/static/empty.png'


    def save(self,*args,**kwargs):
        # put args for avoiding error force_insert
        self.slug = slugify(self.name)
        super(Product,self).save()

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(null=True,blank=False,upload_to='images/')

    @property
    def imageURL(self):
        try:
            if self.image: # Check if a file is associated
                url = self.image.url
            else:
                url = '/static/empty.png' # No file associated
        except ValueError: # Handles cases where .url might be invalid if no file
            url = '/static/empty.png'
        return url

    def __str__(self):
        return self.product.name

class OrderStatus(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Pending, Processing, Shipped, Delivered, Cancelled")
    description = models.CharField(max_length=255, blank=True, null=True, help_text="Optional description of the status")
    is_default = models.BooleanField(default=False, help_text="Is this the default status for new orders?")
    is_final = models.BooleanField(default=False, help_text="Does this status mean the order is closed (e.g., Delivered, Cancelled)?")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Order Statuses"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank= True)
    date_order = models.DateTimeField(auto_now_add=True)
    # complete = models.BooleanField(default=False, null=True, blank=False) # We'll replace this
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, unique=True)
    
    def __str__(self):
        return str(self.id)

    def save(self,*args,**kwargs):
        if not self.transaction_id: # Only generate if not already set
            anjay = random.randrange(100,99999999)
            self.transaction_id = str(anjay) # Ensure it's a string
        if not self.status_id and not kwargs.get('skip_default_status'): # Set default status if not provided
            default_status = OrderStatus.objects.filter(is_default=True).first()
            if default_status:
                self.status = default_status
        super(Order,self).save()

    @property
    def get_cart_totals(self):
        orderitem = self.orderitem_set.all()
        return sum([item.get_total for item in orderitem])
   
    @property
    def get_cart_items(self):
        orderitem = self.orderitem_set.all()
        return sum([item.quantity for item in orderitem])
    
    @property
    def is_complete(self):
        return self.status and self.status.is_final
    

class OrderItem(models.Model):
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, blank=True)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, blank=True)
    quantity = models.IntegerField(default=0, null=True,blank=True) 
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.product)

    @property
    def get_total(self):
        print(self.quantity)
        return self.product.price * self.quantity

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank= True)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, blank=True)
    email = models.EmailField(max_length=200,null=True)
    kota = models.CharField(max_length=255, null=True)
    kode_pos = models.CharField(max_length=10, null=True, blank=True)
    address = models.CharField(max_length=255, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.address

    def get_absolute_url(self):
        return reverse('homey:index')