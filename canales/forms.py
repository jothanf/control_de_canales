from django import forms
from .models import ProviderModel, AnimalModel

class ProviderModelForm(forms.ModelForm):
    class Meta:
        model = ProviderModel
        fields = [
            'name',
            'phone',
            'address',
            'credit_balance'
        ]



class AnimalForm(forms.ModelForm):
    class Meta:
        model = AnimalModel
        fields = [
            'identification',
            'live_price',
            'live_weight',
            'purchase_dates',
            'payment_terms',
            'slaughter_dates',
            'canal_price',
            'canal_weight',
            'other_expenses',
            'total_price_purchase',
            'provider',
        ]
