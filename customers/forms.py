from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from . import models
from home.models import Order as HomeOrder
from home.models import OrderStatus # type: ignore
	
class FormLogIn(forms.ModelForm):
	class Meta:
		model = User
		fields = [
			'username',
			'password'
		]
		
		widgets = {
			'username':forms.TextInput(
				attrs={
					'class':"form-control mb-3",	
				}
			),

			'password':forms.PasswordInput(
				attrs={
					'class':"form-control mb-3",
					'type':'password'				
				}
			)

		}

# class FormLogIn2(forms.form):
# 	username = forms.CharField(max_length=255, required=True)
#     password = forms.CharField(widget=forms.PasswordInput, required=True)

#     def clean(self):
#         username = self.cleaned_data.get('username')
#         password = self.cleaned_data.get('password')
#         user = authenticate(username=username, password=password)

#         if not user or not user.is_active:

#             raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        
#         return self.cleaned_data

#     def login(self, request):
#         username = self.cleaned_data.get('username')
#         password = self.cleaned_data.get('password')
#         user = authenticate(request, username=username, password=password)
#         return user

class FormSignUp(UserCreationForm):
	# New fields for the Profile model
	full_name = forms.CharField(
		max_length=255,
		required=True, 
		label="Nama Lengkap",
		widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Nama Lengkap Anda'})
	)
	alamat = forms.CharField(
		required=True, 
		label="Alamat",
		widget=forms.Textarea(attrs={'class': 'form-control mb-3', 'placeholder': 'Alamat Lengkap', 'rows': 3})
	)
	phone_num = forms.CharField(
		max_length=20,
		required=True, 
		label="Nomor Telepon",
		widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Nomor Telepon (e.g., 08123...)'})
	)
	password1 = forms.CharField(
		strip=False,
		widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}),
	)

	password2 = forms.CharField(
		label=("Password confirmation"),
		widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}),
		strip=False,
		help_text=("Enter the same password as before, for verification."),
	)

	class Meta:
		model = User
		fields = (
			'username',
			'email',
			'password1',
			'password2',
		)	
		widgets = {
			'username':forms.TextInput(
				attrs={
					'class':"form-control mb-3",
				}
			),
			'email':forms.EmailInput(
				attrs={
					'class':"form-control mb-3",
					'placeholder':"ex. name@gmail.com",
					'type':	'email'			
				}
			),
		}
	def clean_email(self):
		email = self.cleaned_data.get('email')
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError("Email sudah terdaftar.")
		try:
			validate_email(email)
		except ValidationError:
			raise forms.ValidationError("Format Email tidak valid.")
		return email

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control mb-3'})
    )

    class Meta:
        model = models.Profile
        fields = ['full_name', 'alamat', 'phone_num']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3}),
            'phone_num': forms.TextInput(attrs={'class': 'form-control mb-3'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate the email field from the related User instance
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if the email is being changed to one that already exists for another user
        if self.instance and self.instance.user and User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError("Email ini sudah digunakan oleh pengguna lain.")
        return email

class SellerSignUpForm(UserCreationForm):
    
    full_name = forms.CharField( # This field is for the main Profile
        max_length=255,
        required=True,
        label="Nama Lengkap",
        widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Nama Lengkap Anda'})
    )
    alamat = forms.CharField(
          max_length=255,
          required=False, # Making optional for now, can be True
          label='alamat',
          widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'alamat anda'})
	)
    phone_num = forms.CharField(
          max_length=20,
          required=False, # Making optional for now, can be True
          label='nomor HP',
          widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Nomor handphone anda'})
	)
    store_name = forms.CharField( # This field is for SellerProfile
          max_length=255,
          required=True,
          label='Nama Toko',
          widget=forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'nama toko anda'}),
	)
    # Explicitly define password fields to match FormSignUp styling
    password1 = forms.CharField(
		strip=False,
        label="Password",
		widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}),
	)
    password2 = forms.CharField(
		strip=False,
        label="Konfirmasi Password",
		widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'}),
        help_text=("Enter the same password as before, for verification."),
	)
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'alamat', 'phone_num', 'store_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control mb-3', 'placeholder': "ex. name@gmail.com"})
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email sudah terdaftar.")
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Format Email tidak valid.")
        return email

class SellerProfileUpdateForm(forms.ModelForm):
      class Meta:
            model = models.SellerProfile
            fields = ['store_name']
            widgets = {
                  'store_name': forms.TextInput(attrs={'class': 'form-control mb-3', 'placeholder': 'Nama toko anda'}),
			}

class StaffSignUpForm(FormSignUp): # Your existing StaffSignUpForm
    user_level = forms.ModelChoiceField(
        queryset=models.UserLevel.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Staff Role / User Level"
    )
    division = forms.ModelChoiceField(
        queryset=models.Division.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Division"
    )

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = HomeOrder
        fields = ['status']
        labels = {
            'status': 'Update Order Status to:'
        }
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].queryset = OrderStatus.objects.all() # Populate choices
        self.fields['status'].help_text = "Select the new status for this order."

class StaffUserBaseForm(forms.ModelForm):
    """Form for staff to edit core User model fields."""
    class Meta:
        model = User
        # Carefully select fields staff can edit. Password is handled separately.
        # is_superuser should probably only be editable by other superusers.
        fields = ['username', 'email', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control mb-3', 'readonly': 'readonly'}), # Username often not editable
            'email': forms.EmailInput(attrs={'class': 'form-control mb-3'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input ml-2'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input ml-2'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input ml-2'}),
        }
        labels = {
            'is_active': 'Is Active',
            'is_staff': 'Is Staff User',
            'is_superuser': 'Is Superuser',
        }

class StaffProfileEditForm(forms.ModelForm):
    """Form for staff to edit Profile model fields."""
    class Meta:
        model = models.Profile
        fields = ['full_name', 'alamat', 'phone_num', 'user_level', 'valid_status', 'division']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'alamat': forms.Textarea(attrs={'class': 'form-control mb-3', 'rows': 3}),
            'phone_num': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'user_level': forms.Select(attrs={'class': 'form-control mb-3'}),
            'valid_status': forms.Select(attrs={'class': 'form-control mb-3'}),
            'division': forms.Select(attrs={'class': 'form-control mb-3'}),
        }
