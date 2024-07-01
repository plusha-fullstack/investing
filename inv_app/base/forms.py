from django import forms
from .models import Portfolio

class PortfolioForm(forms.ModelForm):
    day_of_deal = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Portfolio
        fields = ['type', 'ticker', 'amount', 'buy_price','day_of_deal']

# class SellForm(forms.Form):
#     type = forms.ChoiceField(choices=Portfolio.TYPE_CHOICES)
#     ticker = forms.CharField(max_length=10)
#     amount = forms.DecimalField(max_digits=20, decimal_places=8)
