from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from home.models import Product
from .models import ChatSession, ChatMessage
from django.db.models import Q
from django.http import HttpResponseForbidden
from customers.views import seller_required # Import seller_required decorator

@login_required
# Ensures only logged-in users can access this view
def start_chat_for_product_view(request, product_id):
    """
    View to initiate or redirect to a chat session related to a specific product.
    Looks for an existing session between the buyer, seller, and product.
    If none exists, creates a new one.
    """
    # Get the product and its seller, or return 404 if not found
    product = get_object_or_404(Product, id=product_id)
    seller = product.seller
    buyer = request.user

    if buyer == seller:
        # Prevent seller from chatting with themselves about their product
        # Or handle as desired, e.g., redirect with a message
        return redirect(product.get_absolute_url()) # Assuming Product model has get_absolute_url

    # Look for an existing session for this buyer, seller, and product
    session = ChatSession.objects.filter(buyer=buyer, seller=seller, product=product).first()

    if not session:
        # If no session exists, create a new one
        session = ChatSession.objects.create(buyer=buyer, seller=seller, product=product)
    
    return redirect('chat:chat_session', session_id=session.id)

@login_required
# Ensures only logged-in users can access this view
def start_chat_with_seller_view(request, seller_id):
    """
    View to initiate or redirect to a general chat session with a specific seller.
    Looks for an existing session between the buyer and seller with no product context.
    If none exists, creates a new one.
    """
    # Get the seller user object, or return 404 if not found
    seller = get_object_or_404(User, id=seller_id)
    buyer = request.user

    if buyer == seller:
        # Prevent user from chatting with themselves
        # Redirect to a relevant page, e.g., their own profile or homepage
        return redirect('customers:view_profile') 

    # For a general chat (no specific product), product is None.
    # Look for an existing general session between this buyer and seller
    session = ChatSession.objects.filter(buyer=buyer, seller=seller, product__isnull=True).first()

    if not session:
        session = ChatSession.objects.create(buyer=buyer, seller=seller, product=None)
        
    return redirect('chat:chat_session', session_id=session.id)

@login_required
# Ensures only logged-in users can access this view
def chat_session_view(request, session_id):
    """
    View to display a specific chat session and handle sending new messages.
    Ensures the logged-in user is a participant of the session.
    """
    # Get the chat session object, or return 404 if not found
    session = get_object_or_404(ChatSession, id=session_id)

    # Security check: Ensure the current user is either the buyer or the seller in this session
    if request.user != session.buyer and request.user != session.seller:
        return HttpResponseForbidden("You are not authorized to view this chat.")

    messages = session.messages.all().order_by('timestamp')
    
    # Mark messages as read if the current user is the recipient
    # For simplicity, we'll assume if they view the session, they've read messages not sent by them.
    # A more robust solution might involve AJAX to mark as read.
    # Determine the other participant to mark their messages as read
    recipient = session.seller if request.user == session.buyer else session.buyer
    ChatMessage.objects.filter(session=session, sender=recipient, is_read=False).update(is_read=True)

    # Basic form handling for sending a new message (can be improved with a Django Form)
    # If the request method is POST, process the new message
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ChatMessage.objects.create(session=session, sender=request.user, content=content)
            return redirect('chat:chat_session', session_id=session.id) # Redirect to refresh messages

    context = {
        'session': session,
        'chat_messages': messages,
        'recipient': recipient, # The other user in the chat
    }
    # Render the chat session template with the context data
    return render(request, 'chat/chat_session.html', context)

@login_required
@seller_required # Ensure only sellers can access this
def seller_chat_list_view(request):
    """
    Displays a list of chat sessions for the logged-in seller.
    """
    chat_sessions = ChatSession.objects.filter(
        seller=request.user
    ).select_related('buyer', 'product').order_by('-updated_at')
    context = {
        'chat_sessions': chat_sessions,
        'page_title': "My Chats with Buyers"
    }
    return render(request, 'chat/seller_chat_list.html', context)

@login_required

def my_chat_list_view(request):
    """
    Displays a list of all chat sessions for the logged-in user (as buyer or seller).
    """
    chat_sessions = ChatSession.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('buyer', 'seller', 'product').distinct().order_by('-updated_at')
    context = {
        'chat_sessions': chat_sessions,
        'page_title': "My Conversations"
    }
    return render(request, 'chat/my_chat_list.html', context)
