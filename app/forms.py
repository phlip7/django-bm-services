from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from baramogo import settings
from .models import *
from django import forms
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
    country = forms.ModelChoiceField(queryset=Country.objects.all(), initial=0, required=True)
    city = forms.ModelChoiceField(queryset=City.objects.all(), initial=0, required=True)
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


class GigForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 8}))
    locality = forms.ModelChoiceField(queryset=Locality.objects.all(), required=False)
    area = forms.ModelChoiceField(queryset=Area.objects.all(), required=False)
    subarea = forms.ModelChoiceField(queryset=SubArea.objects.all(), required=False)
    address = forms.CharField(required=False)
    cover_image = forms.ImageField(widget=forms.ClearableFileInput(), required=False)

    class Meta:
        model = Gig
        # fields = '__all__'
        fields = ['title', 'category', 'description', 'price', 'cover_image', 'status',
                  'country', 'city', 'locality', 'area', 'subarea', 'address']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['city'].queryset = City.objects.none()
            self.fields['area'].queryset = Area.objects.none()

            if 'country' in self.data:
                try:
                    country_id = int(self.data.get('country'))
                    self.fields['city'].queryset = City.objects.filter(country_id=country_id).order_by('name')
                except (ValueError, TypeError):
                    pass  # invalid input from the client; ignore and fallback to empty City queryset
            elif self.instance.pk:
                self.fields['city'].queryset = self.instance.country.city_set.order_by('name')

            if 'city' in self.data:
                try:
                    city_id = int(self.data.get('city'))
                    self.fields['area'].queryset = Area.objects.filter(city_id=city_id).order_by('name')
                except (ValueError, TypeError):
                    pass  # invalid input from the client; ignore and fallback to empty City queryset
            elif self.instance.pk:
                self.fields['area'].queryset = self.instance.city.area_set.order_by('name')

            # super(GigForm, self).__init__(*args, **kwargs)

            # for field in  self.fields:
            #     self.fields[field].widget.attrs['class'] = 'form-control'
            #     self.fields[field].widget.attrs['name'] = field
            #     self.fields[field].widget.attrs['id'] = field

            # self.fields['title'].widget.attrs['id'] = 'title'
            # self.fields['title'].widget.attrs['name'] = 'title'
            # self.fields['title'].widget.attrs['id'] = 'title'
            # self.fields['category'].widget.attrs['name'] = 'category'
            # self.fields['category'].widget.attrs['id'] = 'category'
            # self.fields['description'].widget.attrs['name'] = 'description'
            # self.fields['description'].widget.attrs['id'] = 'description'
            # self.fields['price'].widget.attrs['name'] = 'price'
            # self.fields['price'].widget.attrs['id'] = 'price'
            # self.fields['photo'].widget.attrs['name'] = 'photo'
            # self.fields['photo'].widget.attrs['id'] = 'photo'
            # self.fields['status'].widget.attrs['name'] = 'status'
            # self.fields['status'].widget.attrs['id'] = 'status'
