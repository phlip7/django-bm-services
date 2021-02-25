from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Gig
from django import forms

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class GigForm(forms.ModelForm):
    class Meta:
        model = Gig
        fields = ['title', 'category', 'description', 'price', 'photo', 'status']

        # def __init__(self, *args, **kwargs):
        #     super(GigForm, self).__init__(*args, **kwargs)
            
        #     for field in  self.fields:
        #         self.fields[field].widget.attrs['class'] = 'form-control'
        #         self.fields[field].widget.attrs['name'] = field
        #         self.fields[field].widget.attrs['id'] = field
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
