from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from baramogo import settings
from .models import *
from django import forms
import datetime
import django.forms.utils
import django.forms.widgets


class CreateUserForm(UserCreationForm):
    ACCT_TYPE_CHOICES = (
        ('email', 'E-mail'),
        ('phone', 'Téléphone')
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'mogo002', 'autocomplete': 'off', 'required': 'required'}),
        validators=[RegexValidator(regex='^[A-Za-z0-9]+$', message="Can't use special characters")])
    birthday = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker',
        'placeholder': 'dd/mm/yyyy',
        'required': 'required'
    }), input_formats=settings.DATE_INPUT_FORMATS)
    phone = forms.CharField(widget=forms.TextInput(), required=False)
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Entrez l'emplacement"}), required=True)
    country = forms.CharField(widget=forms.HiddenInput(), required=False)
    city = forms.CharField(widget=forms.HiddenInput(), required=False)
    area = forms.CharField(widget=forms.HiddenInput(), required=False)
    lat = forms.CharField(widget=forms.HiddenInput(), required=False)
    lng = forms.CharField(widget=forms.HiddenInput(), required=False)
    email = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'name@address.com', 'autocomplete': 'off'}), required=False)
    registration_type = forms.ChoiceField(label='Sélectionner e-mail ou téléphone',
                                          choices=ACCT_TYPE_CHOICES,
                                          widget=forms.Select(attrs={'id': 'account_type'}),
                                          required=True)

    def clean(self):
        email = self.cleaned_data.get('email')
        phone = self.cleaned_data.get('phone')
        register_type = self.cleaned_data.get('registration_type')
        if register_type == 'email':
            if User.objects.filter(email=email.lower()).exists():
                raise ValidationError("E-mail existe déjà")
        else:
            if Profile.objects.filter(phone=phone).exists():
                raise ValidationError("Le téléphone existe déjà")
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)


class ProfileForm(forms.ModelForm):
    birthday = forms.DateField(widget=forms.TextInput(attrs={
        'class': 'datepicker form-control',
        'placeholder': 'dd/mm/yyyy'
    }), input_formats=settings.DATE_INPUT_FORMATS)
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }), required=False)

    class Meta:
        model = Profile
        fields = ['birthday', 'phone']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            profile = Profile.objects.get(user=user.id)
            if profile:
                if profile.phone:
                    self.fields['phone'].initial = profile.phone
                if profile.birthday:
                    self.fields['birthday'].initial = profile.birthday.strftime('%d/%m/%Y')


class GigForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 8}))
    cover_image = forms.ImageField(widget=forms.ClearableFileInput(), required=False)

    class Meta:
        model = Gig
        fields = ['title', 'category', 'description', 'price', 'cover_image', 'status']


class AddressForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Entrez l'emplacement"}), required=True)
    country = forms.CharField(widget=forms.HiddenInput(), required=False)
    city = forms.CharField(widget=forms.HiddenInput(), required=False)
    area = forms.CharField(widget=forms.HiddenInput(), required=False)
    lat = forms.CharField(widget=forms.HiddenInput(), required=False)
    lng = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Gig
        fields = ['address', 'country', 'city', 'area', 'lat', 'lng',]
