from cProfile import label

from django import forms


class DeliveryForm(forms.ModelForm):
    pass

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
