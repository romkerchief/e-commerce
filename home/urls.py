from django.urls import path
from .views import (
    HomeView, ProductDetail, ShippingView, updateItem,
    seller_product_create, seller_product_update, seller_product_delete,
    store_detail_view
)


app_name = 'homey'
urlpatterns = [
    path('',HomeView.as_view(template_name='home/indexhome.html',paginate_by=4),name='index'),
    path('products/',HomeView.as_view(template_name='home/producthome.html',paginate_by=6),name='product'),
    path('products/<slug:slug>/',ProductDetail.as_view(template_name='home/detail.html'),name='detail'),
    path('cart/',HomeView.as_view(template_name='home/cart.html'),name="cart"),
    path('checkout/',ShippingView,name='checkout'),
    path('update-item/',updateItem, name='update-item'),
    path('seller/product/create/', seller_product_create, name='seller_product_create'),
    path('seller/product/<int:pk>/update/', seller_product_update, name='seller_product_update'),
    path('seller/product/<int:pk>/delete/', seller_product_delete, name='seller_product_delete'),
    path('store/<slug:store_slug>/', store_detail_view, name='store_detail'),
]
