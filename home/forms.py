from django import forms
from .models import Product, ProductImage # Assuming ProductImage might be used later

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Include fields that the seller should be able to edit/create
        # 'seller' is excluded as it's set in the view
        # 'slug' is excluded as it's auto-generated
        fields = ['name', 'category', 'main_image', 'description', 'old_price', 'price', 'stock'] # Add 'image' from ProductImage if you handle it here
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'old_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            # 'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}), # If you add 'available' field to Product model
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file mb-2'}),
        }