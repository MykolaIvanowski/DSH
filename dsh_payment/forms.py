from django import forms
from dsh_payment.models import DeliveryAddress


class DeliveryForm(forms.ModelForm):
    delivery_full_name = forms.CharField(label="",widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Full name'}),required=True)
    delivery_email = forms.CharField(label="",widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Email'}),required=True)
    delivery_address1 = forms.CharField(label="",widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Delivery address1'}),required=True)
    delivery_address2 = forms.CharField(label="",widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Delivery address2'}),required=False)
    delivery_city = forms.CharField(label="",widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'City'}),required=True)
    delivery_state = forms.CharField(label="",widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'State'}),required=False)
    delivery_zipcode = forms.CharField(label="",widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Zipcode'}),required=False)
    delivery_country = forms.CharField(label="",widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Country'}),required=True)

    class Meta:
        model = DeliveryAddress
        fields = ['delivery_full_name', 'delivery_email', 'delivery_address1', 'delivery_address2', 'delivery_city',
                  'delivery_state', 'delivery_zipcode', 'delivery_country']
        exclude = ['user',]

class PaymentForm(forms.ModelForm):
    card_name = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder':'Name on card'}), required=True)
    card_number = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Card number'}), required=True)
    card_expired_date = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Expiration date'}), required=True)
    card_cvv_number = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'CVV code'}), required=True)
    card_address1 = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Address'}), required=True)
    card_adrress2 = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder': 'Address'}), required=False)
    card_city = forms.CharField(label="", widget= forms.TextInput(
        attrs={'class': 'form-control', 'placeholder':'City'}), required=True)
    card_state = forms.CharField(label="", widget= forms.TextInput(
        attrs={'class': 'form-control','placeholder': 'State'}), required=True)
    card_zipcode = forms.CharField(label="", widget = forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Zipcode'}), required=True)
    card_country = forms.CharField(label="", widget = forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'country'}), required=True )
