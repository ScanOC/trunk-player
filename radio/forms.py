import re
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from .models import Unit, StripePlanMatrix, Profile

class PaymentForm(forms.Form):
    #stripe_token = forms.CharField(label='stripe_token', max_length=100)
    cardholder_name = forms.CharField(label='cardholder name', max_length=100)
    plan_type = forms.ModelChoiceField(
                    queryset=StripePlanMatrix.objects.filter(active=True),
                    empty_label=None,
                    )

 
class RegistrationForm(forms.Form):
 
    username = forms.RegexField(regex=r'^\w+$', widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Username"), error_messages={ 'invalid': _("This value must contain only letters, numbers and underscores.") })
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label=_("Password (again)"))
 
    def clean_username(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("The username already exists. Please try another one."))
 
    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields did not match."))
        return self.cleaned_data


class UnitEditForm(forms.ModelForm):

    class Meta:
        model = Unit
        fields = ['description',]


class UserForm(forms.ModelForm):
    username = forms.CharField(
                       widget=forms.TextInput(attrs={'readonly':'readonly'})
               )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
