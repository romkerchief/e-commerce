from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, UserLevel, ValidStatus, SellerProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print(">>> THE create_user_profile SIGNAL IS RUNNING! <<<") # Add this line
        # Get or create default UserLevel and ValidStatus
        default_level, _ = UserLevel.objects.get_or_create(name="Pembeli")
        default_status, _ = ValidStatus.objects.get_or_create(name="Valid")
        
        # Use get_or_create instead of create. This is the fix.
        # It will not fail if a profile already exists.
        Profile.objects.get_or_create(
            user=instance, 
            defaults={
                'user_level': default_level,
                'valid_status': default_status
            }
        )

@receiver(post_save, sender=Profile)
def create_or_update_seller_profile(sender, instance, created, **kwargs):
    if instance.user_level and instance.user_level.name == "Penjual":
        SellerProfile.objects.get_or_create(profile=instance)
    # If user_level changes away from "Penjual", you might want to delete SellerProfile