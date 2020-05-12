from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT = {
    ('S', 'Stripe'),
    ('P', 'PayStack')

}

class CheckoutForm(forms.Form):
    shippingAddress = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'id':"address", 
        "class":"form-control",
        "placeholder":"1234 Main St"

    }))
    shippingAddress2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'id':"address-2",
        'class':"form-control", 
        'placeholder':"Apartment or suite" 
    }))
    shippingCountry = CountryField(blank_label="(select country)").formfield(required=False,widget=CountrySelectWidget(attrs={
        "class":"  custom-select d-block w-100",
        "id":"country" 
        })
    )
    shippingZip = forms.CharField(required=False,widget=forms.TextInput(attrs={
        "class":"form-control", "id":"zip", "placeholder":"zip code" 
    }))
    billingAddress = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'id':"address", 
        "class":"form-control", 
        "placeholder":"1234 Main St"
    }))
    billingAddress2 = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'id':"address-2",
        'class':"form-control", 
        'placeholder':"Apartment or suite"
    }))
    billingCountry = CountryField(blank_label="(select country)").formfield(required=False,widget=CountrySelectWidget(attrs={
        "class":"  custom-select d-block w-100",
        "id":"country" 
        })
    )
    billingZip = forms.CharField(required=False,widget=forms.TextInput(attrs={
        "class":"form-control", "id":"zip","placeholder":"zip code" 
    }))
    same_billing_address = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={
        "class":"custom-control-input same_billing_address", 'id':'same_billing_address'
    }))
    set_default_shipping = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={
        "class":"custom-control-input", 'id':'set_default_shipping'
    }))
    use_default_shipping = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={
        "class":"custom-control-input use_default_shipping" , 'id':'use_default_shipping'
    }))
    set_default_billing = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={
        "class":"custom-control-input set_default_billing", 'id':'set_default_billing'
    }))
    use_default_billing = forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={
        "class":"custom-control-input use_default_billing" ,'id':'use_default_billing'
    }))
    paymentOption= forms.ChoiceField( choices=PAYMENT,widget=forms.RadioSelect())


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        "class": 'form-control',
        "placeholder": "Promo Code"
    }))

class RefundForm(forms.Form):
    ref_code = forms.CharField(widget=forms.TextInput(attrs={
        "class": 'form-control',
        "placeholder": "Reference Code"
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        "class": 'form-control',
        "placeholder": "State Your Reasons For Refund",
        "col": 2,
        'rows':3
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
         "class": 'form-control',
        "placeholder": "email "
    }))