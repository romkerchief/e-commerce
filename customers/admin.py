from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, UserLevel, ValidStatus, Division, SellerProfile

class ProfileInline(admin.StackedInline):
        model = Profile
        can_delete = False
        verbose_name_plural = 'Profile'
        fk_name = 'user'

class SellerProfileInline(admin.StackedInline):
    model = SellerProfile
    can_delete = False 
    verbose_name_plural = 'Seller Specific Profile'
    fields = ('store_name', 'slug') # Specify fields to show
    readonly_fields = ('slug',) # Make slug read-only as it's auto-generated

class ProfileAdmin(admin.ModelAdmin):
    inlines = (SellerProfileInline,)
    list_display = ('user', 'full_name', 'user_level', 'email_verified')
    search_fields = ('user__username', 'full_name', 'user__email')
    list_filter = ('user_level', 'email_verified', 'valid_status')

    # Define a new User admin
class UserAdmin(BaseUserAdmin):
        inlines = (ProfileInline,)
        # to list_display or list_filter if you want to see/filter by these in the User list view
        # list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'profile__user_level', 'profile__valid_status')
        # list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__user_level', 'profile__valid_status')
    # Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.
admin.site.register(Profile, ProfileAdmin) # Register Profile with its own admin and the SellerProfile inline
admin.site.register(Division)
admin.site.register(UserLevel)
admin.site.register(ValidStatus)