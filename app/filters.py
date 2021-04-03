import django_filters
from django.forms.widgets import TextInput
from django_filters import CharFilter

from .models import Gig

class GigFilter(django_filters.FilterSet):
	title = CharFilter(field_name='title', lookup_expr='icontains', widget=TextInput(attrs={'placeholder': 'Métier'}))

	class Meta:
		model = Gig
		fields = ['title', 'category', 'country', 'city', 'area']
		#exclude = ['customer', 'date_created']

#https://github.com/divanov11/crash-course-CRM/blob/Part-12-Filter-Form/crm1_v12_filter_form/accounts/filters.py