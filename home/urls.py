from django.urls import path
from .views import (
    HomeView, ProductDetail, updateItem,
    seller_product_create, seller_product_update, seller_product_delete, dashboard_statistik,
    store_detail_view,
    cart, checkout, process_payment, order_confirmation,
)


app_name = 'homey'
urlpatterns = [
    path('',HomeView.as_view(template_name='home/indexhome.html',paginate_by=4),name='index'),
    path('products/',HomeView.as_view(template_name='home/producthome.html',paginate_by=6),name='product'),
    path('products/<slug:category_slug>/<slug:product_slug>/',ProductDetail.as_view(template_name='home/detail.html'),name='product_detail'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('payment/', process_payment, name='payment'), # This is the single URL for payment handling
    path('order-confirmation/<str:transaction_id>/', order_confirmation, name='order_confirmation'),    path('update-item/',updateItem, name='update-item'),
    path('seller/product/create/', seller_product_create, name='seller_product_create'),
    path('seller/product/<int:pk>/update/', seller_product_update, name='seller_product_update'),
    path('seller/product/<int:pk>/delete/', seller_product_delete, name='seller_product_delete'),
    path('store/<slug:store_slug>/', store_detail_view, name='store_detail'),
    path('dashboard/', dashboard_statistik, name='dashboard'),
]
