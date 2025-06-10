from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

# Create your models here.
# --- New Models for User Structure ---

class UserLevel(models.Model):
    # user_level_id will be Django's auto 'id' field
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Admin, Penjual, Pembeli")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "User Level"
        verbose_name_plural = "User Levels"

class ValidStatus(models.Model):
    # valid_status_id will be Django's auto 'id' field
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Valid, Invalid, Keluar")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Valid Status"
        verbose_name_plural = "Valid Statuses"

class Division(models.Model):
    # division_id will be Django's auto 'id' field
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Keuangan, Kas, Penjualan")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Division"
        verbose_name_plural = "Divisions"

# --- Enhanced Profile Model (replaces old UserProfile) ---

class Profile(models.Model):
    # profile_id will be Django's auto 'id' field.
    # The User model already has username, password, email.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    alamat = models.TextField(blank=True, help_text="Full address")
    phone_num = models.CharField(max_length=20, blank=True)

    # Foreign Keys to the new models
    user_level = models.ForeignKey(UserLevel, on_delete=models.PROTECT, null=True, blank=True)
    valid_status = models.ForeignKey(ValidStatus, on_delete=models.PROTECT, null=True, blank=True)
    division = models.ForeignKey(Division, on_delete=models.SET_NULL, null=True, blank=True)

    # Fields from your old UserProfile you might want to keep
    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class SellerProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='seller_specific_profile')
    store_name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.store_name:
            self.slug = slugify(self.store_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Seller Profile for {self.profile.user.username} - Store: {self.store_name}"
