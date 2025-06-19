from django.db import models
from django.contrib.auth.models import User
from home.models import Product # Assuming a chat can be related to a product

class ChatSession(models.Model):
    """
    Represents a chat conversation between a buyer and a seller,
    optionally linked to a specific product.
    """
    # User who initiated or is considered the 'buyer' in this session
    buyer = models.ForeignKey(User, related_name='buyer_chat_sessions', on_delete=models.CASCADE)
    # User who is the 'seller' in this session
    seller = models.ForeignKey(User, related_name='seller_chat_sessions', on_delete=models.CASCADE)
    # Optional: Link to the product this chat is about
    product = models.ForeignKey(Product, related_name='chat_sessions', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) # Timestamp of session creation
    updated_at = models.DateTimeField(auto_now=True) # Timestamp of the last message or update

    class Meta:
        # Ensures a unique chat session for a specific buyer, seller, and product combination.
        # If product is NULL, it allows for one general chat session between a buyer and seller.
        unique_together = ('buyer', 'seller', 'product') # Prevents multiple sessions for the same context if product is involved
        ordering = ['-updated_at'] # Order sessions by the most recently active

    def __str__(self):
        if self.product:
            return f"Chat between {self.buyer.username} and {self.seller.username} about {self.product.name}"
        return f"Chat between {self.buyer.username} and {self.seller.username}"
class ChatMessage(models.Model):
    """
    Represents a single message within a ChatSession.
    """
    # The chat session this message belongs to
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    # The user who sent this message
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    # recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE) # Can be inferred from session and sender
    # The actual content of the message
    content = models.TextField()
    # Timestamp when the message was sent
    timestamp = models.DateTimeField(auto_now_add=True)
    # Flag to indicate if the recipient has read the message
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # When a new message is saved, update the parent session's 'updated_at' timestamp
        # to reflect the latest activity.
        self.session.updated_at = self.timestamp
        self.session.save(update_fields=['updated_at'])
