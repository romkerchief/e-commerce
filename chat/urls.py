from django.urls import path
from . import views # We'll create these views next

app_name = 'chat'

# URL patterns for the chat application
urlpatterns = [
    # URL for viewing a specific chat session (requires session ID)
    path('session/<int:session_id>/', views.chat_session_view, name='chat_session'),
    # URL for starting a chat about a specific product (requires product ID)
    path('start/product/<int:product_id>/', views.start_chat_for_product_view, name='start_chat_for_product'),
    # URL for starting a general chat with a specific seller (requires seller user ID)
    path('start/seller/<int:seller_id>/', views.start_chat_with_seller_view, name='start_chat_with_seller'),
    # URL for sellers to view a list of their chat sessions with buyers
    path('seller/my-chats/', views.seller_chat_list_view, name='seller_chat_list'),
    # URL for any logged-in user to view a list of all their chat sessions (as buyer or seller)
    path('my-chats/', views.my_chat_list_view, name='my_chat_list'),
]
