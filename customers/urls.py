from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    registerPage, seller_register_page, loginPage, logoutPage,
    verify_email, resend_verification, edit_profile, view_profile, customer_order_history_view, customer_order_detail_view, staff_register_view, staff_dashboard_view, staff_all_orders_view, staff_order_detail_view,
    seller_dashboard_view, seller_order_detail_view
)

urlpatterns = [
	path('register/',registerPage,name='register'),
	path('seller/register/', seller_register_page, name='seller_register'),
	path('login/',loginPage,name='customer_login'),
	path('logout/',logoutPage,name='logout'),
    path('verify-email/', verify_email, name='verify_email'),
    path('resend-verification/', resend_verification, name='resend_verification'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/', view_profile, name='view_profile'),
    path('seller/dashboard/', seller_dashboard_view, name='seller_dashboard'),
    path('seller/order/<str:order_transaction_id>/', seller_order_detail_view, name='seller_order_detail'),
    path('order-history/', customer_order_history_view, name='customer_order_history'),
    path('order-detail/<str:order_transaction_id>/', customer_order_detail_view, name='customer_order_detail'),
    path('staff/register/', staff_register_view, name='staff_register'),
    path('staff/dashboard/', staff_dashboard_view, name='staff_dashboard'),
    path('staff/all-orders/', staff_all_orders_view, name='staff_all_orders'),
    path('staff/order-detail/<str:order_transaction_id>/', staff_order_detail_view, name='staff_order_detail'),
] 
