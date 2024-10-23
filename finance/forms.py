from django import forms

class BacktestForm(forms.Form):
    initial_investment = forms.FloatField(
        label='Initial Investment',
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Enter initial investment amount',
            'class': 'form-control'
        })
    )