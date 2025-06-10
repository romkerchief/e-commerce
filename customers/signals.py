from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, UserLevel, ValidStatus, SellerProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
            # Get or create default UserLevel and ValidStatus
            # You might want to create these in a data migration or admin panel first
            default_level, _ = UserLevel.objects.get_or_create(name="Pembeli")
            default_status, _ = ValidStatus.objects.get_or_create(name="Valid") # Or "Pending Verification"
            Profile.objects.create(user=instance, user_level=default_level, valid_status=default_status)

@receiver(post_save, sender=Profile)
def create_or_update_seller_profile(sender, instance, created, **kwargs):
    if instance.user_level and instance.user_level.name == "Penjual":
        SellerProfile.objects.get_or_create(profile=instance)
    # If user_level changes away from "Penjual", you might want to delete SellerProfile