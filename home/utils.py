from django.contrib.auth.models import update_last_login
from .models import *


def cartData(request):
    if request.user.is_authenticated:
        default_status = OrderStatus.objects.filter(is_default=True).first()
        if not default_status:
            # This case should ideally not happen if statuses are set up correctly.
            # Handle error appropriately, e.g., log or raise an exception.
            # For now, return an empty cart.
            return {'items': [], 'order': {'get_cart_items': '0', 'get_cart_totals': '0'}}

        customer = request.user
        try:
            # Get or create the active cart (order with default status)
            order, created = Order.objects.get_or_create(user=customer, status=default_status)
            items = order.orderitem_set.all()
        except Exception as e: # More specific exception handling could be better
            print(f"Error in cartData: {e}")
            # Fallback to an empty cart representation
            items = []
            order = {'get_cart_items': '0', 'get_cart_totals': '0', 'id': None} # Ensure order has an id for CompleteOrder
    else:
        items = []
        order = {'get_cart_items': '0', 'get_cart_totals': '0', 'id': None}
        # items = order['get_cart_totals'] # This line was redundant and potentially problematic
    return {'items': items, 'order': order}


def CompleteOrder(request):
    #def ini fungsinya untuk memproses order yg sudah di kirimkan
    cart = cartData(request)
    if request.user.is_authenticated:
        try:
            order_to_complete = Order.objects.get(id=cart['order'].id, user=request.user)
            
            # Transition to "Processing" status (or another appropriate status after checkout)
            processing_status = OrderStatus.objects.get(name="Processing") # Assuming "Processing" status exists
            
            order_to_complete.status = processing_status
            order_to_complete.save() # This will also generate transaction_id if not present
            
        except Order.DoesNotExist:
            print(f"Order with id {cart['order'].id} not found for user {request.user.username} in CompleteOrder.")
        except OrderStatus.DoesNotExist:
            print(f"OrderStatus 'Processing' not found. Please create it in the admin.")
        except Exception as e:
            print(f"Error in CompleteOrder: {e}")

base = 'https://api.whatsapp.com/send?phone=6281388762268&text='
def whatsappLinkCheckout(request,context):
    items = context
    if len(items) > 0:
        # context yg diambil adalah queryset dari list product yg dicheckout oleh pengguna
        productName = [item.product.name for item in items]
        productNumber = [item.quantity for item in items]
        #Dua variable ini digunakan untuk menampung list nama product yg akan dibeli 
        
        title = ""
        for i,a in zip(productName,productNumber):
            title += str(i) +" Jumlahnya: "+ str(a)
            title += ', '

        textWA = f'Permisi Bu aryani Saya ingin memesan:%0A{title}%0ADikirim Ke :%0ACatatan :%0ASekian Terimakasih.'
        linked = {'link':base + textWA.replace(' ', '%20')}
        return linked
    else:
        return {'link':'Failed'}

def paginationFilter(request):
    full_path = request.get_full_path()
    yolo = False
    if len(request.GET) != 0:
        yolo = True
        return {'path':full_path,'aye':yolo}
    return {'aye':yolo}
    
def whatsappLinkBuyNow(request,context):
    product = context["product"]
    textWA = f'Permisi Bu aryani Saya ingin memesan:%0A{product.name}%0AJumlahnya :%0ADikirim Ke :%0ACatatan :%0ASekian Terimakasih.'
    linked = {'link':base + textWA.replace(' ', '%20')}
    return linked

def mergeFunction(request,context):
    #run all whatsapp things
    dictionary = {}
    dictionary.update(whatsappLinkCheckout(request,context))
    dictionary.update(paginationFilter(request))
    return dictionary