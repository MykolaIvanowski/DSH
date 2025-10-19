from django import forms
from dsh_payment.models import Order


class DeliveryForm(forms.ModelForm):
    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First name'}), required=True)
    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last name'}), required=True)
    email = forms.EmailField(label="", widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Your email'}), required=True)
    phone = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Your phone'}), required=True)
    street_home = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Delivery address street, home, apartment'}), required=True)
    city = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'City'}), required=True)
    state = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'State'}), required=True)
    zipcode = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Zipcode'}), required=True)
    country = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Country'}), required=False)

    class Meta:
        model = Order
        fields = ['first_name','last_name','email','phone','street_home','city','state','zipcode','country']


        #exclude = ['date_delivered',] #TODO 'amount_paid', 'status', 'date_ordered'


class PaymentForm(forms.Form):
    card_name = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder':'Name on card'}), required=True)
    card_number = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Card number'}), required=True)
    card_expired_date = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Expiration date (MM/YY)'}), required=True)
    card_cvv_number = forms.CharField(label="", widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'CVV code'}), required=True)

