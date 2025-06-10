from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ['name','slug']
	prepopulated_fields = {'slug':('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin): 
	list_display = ['name', 'price', 'upload_time', 'slug', 'seller'] 
	list_filter = ['category', 'seller'] 
	search_fields = ['name', 'description', 'seller__username'] 


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin): 
	list_display = ['user','id','status','date_order','transaction_id']
	list_filter = ['status', 'date_order']
	search_fields = ['user__username', 'transaction_id']
	readonly_fields = ('transaction_id', 'date_order')

admin.site.register(OrderItem)
admin.site.register(ProductImage)
@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_default', 'is_final', 'description')
    list_filter = ('is_default', 'is_final')

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin): 
	list_display = ['user','order','address']