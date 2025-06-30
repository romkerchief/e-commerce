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
    
    # This method is the key. It prevents the inline form from being displayed
    # on the "add" page, thus stopping the duplicate creation attempt.
    def get_inline_instances(self, request, obj=None):
        # Return no inlines when creating a new user (obj is None)
        if not obj:
            return list()
        # Otherwise, return the inlines as usual for the change page
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register your models here.
admin.site.register(Division)
admin.site.register(UserLevel)
admin.site.register(ValidStatus)