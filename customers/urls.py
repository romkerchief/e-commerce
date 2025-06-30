from django.urls import path,include
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from .views import (
    registerPage, seller_register_page, loginPage, logoutPage,
    verify_email, resend_verification, edit_profile, view_profile, customer_order_history_view, customer_order_detail_view, staff_register_view, staff_dashboard_view, staff_all_orders_view, staff_order_detail_view, staff_user_list_view, staff_user_detail_view, staff_user_orders_view, staff_user_edit_view, staff_product_list_view, staff_product_delete_view,
    seller_dashboard_view, seller_order_detail_view,
    pimpinan_dashboard_view, export_pimpinan_dashboard_pdf, export_pimpinan_dashboard_xlsx
)

app_name = 'customers' # Add this line

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
    path('staff/users/<int:pk>/', staff_user_detail_view, name='staff_user_detail'),
    path('staff/product/<int:pk>/delete/', staff_product_delete_view, name='staff_product_delete'),
    path('staff/products/', staff_product_list_view, name='staff_product_list'),
    path('staff/users/<int:user_id>/orders/', staff_user_orders_view, name='staff_user_orders'),
    path('staff/users/<int:pk>/edit/', staff_user_edit_view, name='staff_user_edit'),
    path('staff/users/', staff_user_list_view, name='staff_user_list'),
    path('pimpinan/dashboard/', pimpinan_dashboard_view, name='pimpinan_dashboard'),
    path('pimpinan/dashboard/export/pdf/', export_pimpinan_dashboard_pdf, name='export_pimpinan_pdf'),
    path('pimpinan/dashboard/export/xlsx/', export_pimpinan_dashboard_xlsx, name='export_pimpinan_xlsx'),
    
    # Password Reset URLs
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),

    # Password Change URLs (already present in your edit_profile.html, but good to have standard names)
    path('password_change/',
         auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'),
         name='password_change_done'),
]