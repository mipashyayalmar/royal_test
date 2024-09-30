from django import forms
from .models import Orders

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['items_json', 'amount', 'name', 'email', 'address', 'city', 'state', 'zip_code', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['items_json'].widget.attrs.update({'class': 'form-control', 'id': 'items_json'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        # Add any additional field customizations here

from django import forms
from .models import Advertise

class AdvertiseForm(forms.ModelForm):
    class Meta:
        model = Advertise
        fields = ['name', 'image2']
