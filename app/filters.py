import django_filters
from .models import Gig, Address
from django.forms.widgets import TextInput

class GigFilter(django_filters.FilterSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        countries = ()
        cities = ()
        addresses_country = Address.objects.distinct('country')
        addresses_city = Address.objects.distinct('city')
        for address in addresses_country:
            if address.country:
                countries += (address.country, address.country),
        for address in addresses_city:
            if address.city:
                cities += (address.city, address.city),
        self.filters['city'].extra['choices'] = cities
        self.filters['country'].extra['choices'] = countries
        self.filters['title'].extra['widget'] = TextInput(attrs={'placeholder': 'MOTS CLÉS'})
        self.filters['category'].extra['empty_label'] = 'CATEGORIES'

    country = django_filters.ChoiceFilter(label='Country', empty_label='PAYS')
    city = django_filters.ChoiceFilter(label='City', empty_label='VILLE')
    lat = django_filters.NumberFilter()
    lng = django_filters.NumberFilter()

    class Meta:
        model = Gig
        fields = ['title', 'category', 'country', 'city', 'lat', 'lng']

    @property
    def qs(self):
        parent = super().qs
        if self.request.GET.get('form_id') is not None:
            form_id = self.request.GET.get('form_id')
            category = self.request.GET.get('category')
            country = self.request.GET.get('country')
            city = self.request.GET.get('city')
            lat = self.request.GET.get('lat')
            lng = self.request.GET.get('lng')
            print("form_id ==", form_id, "category ==", category, "country ==", country, "city ==", city, "lat ==", lat, "lng ==", lng)
            if form_id == "gfilter":
                if category and category != "":
                    print("category is not missing", category)
                    parent = parent.filter(category=category)
                if city and city != "":
                    print("City is not missing", city)
                    parent = parent.filter(location__city__icontains=city)
                if country and country != "":
                    print("Country is not missing", country)
                    parent = parent.filter(location__country__icontains=country)
                if lat != "" and lng != "":
                    print("Latitude is not missing", lat, lng)
                    lat_val = float(lat)
                    lng_val = float(lng)
                    parent = parent.filter(location__lat__range=(lat_val - 0.2, lat_val + 0.2),
                                           location__lng__range=(lng_val - 0.2, lng_val + 0.2))
            else:
                if city and city != "":
                    parent = parent.filter(location__city__icontains=city)

        title = self.request.GET.get("title")
        title = None if title == "" else title
        if title is not None:
            return parent.filter(title__icontains=title) | parent.filter(description__icontains=title)
        else:
            return parent
