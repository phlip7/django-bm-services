from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Gig, City, Country
from django import forms
import django.forms.utils
import django.forms.widgets

class CreateUserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'mogo-002', 'autocomplete':'off', 'required':'required'}))
    birthyear = forms.IntegerField(widget=forms.NumberInput(attrs={'minlength':4, 'maxlength':4, 'required':'required'}))
    phone = forms.CharField(widget=forms.TextInput())
    country = forms.ModelChoiceField(queryset=Country.objects.all(), initial=0, required=True)
    city = forms.ModelChoiceField(queryset=City.objects.all(), initial=0, required=True)
    email = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'name@address.com', 'autocomplete':'off', 'required':'required'}))
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class GigForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={ 'rows':5}))
    class Meta:
        model = Gig
        #fields = '__all__'
        fields = ['title', 'category', 'description', 'price', 'photo', 'status', 'country', 'city', 'area', 'address']

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


			#super(GigForm, self).__init__(*args, **kwargs)
            
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
