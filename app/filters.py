import django_filters
from .models import Gig, Address


def get_location_names(name_type):
    countries = ()
    cities = ()
    areas = ()
    addresses = Address.objects.all()
    for address in addresses:
        cities += (address.city, address.city),
        countries += (address.country, address.country),
        areas += (address.area, address.area),
    if name_type is 0:
        return countries
    elif name_type is 1:
        return cities
    else:
        return areas


class GigFilter(django_filters.FilterSet):
    country = django_filters.ChoiceFilter(choices=get_location_names(0), label='Country')
    city = django_filters.ChoiceFilter(choices=get_location_names(1), label='City')
    area = django_filters.ChoiceFilter(choices=get_location_names(2), label='City')

    class Meta:
        model = Gig
        fields = ['title', 'category', 'country', 'city', 'area']

    @property
    def qs(self):
        parent = super().qs
        if self.request.GET.get('form_id') is not None:
            form_id = self.request.GET.get('form_id')
            category = self.request.GET.get('category')
            country = self.request.GET.get('country')
            city = self.request.GET.get('city')
            area = self.request.GET.get('area')
            if form_id == "gfilter":
                if category != "":
                    parent = parent.filter(category=category)
                if city and city != "":
                    parent = parent.filter(location__city__icontains=city)
                if country is not "":
                    parent = parent.filter(location__country__icontains=country)
                if area is not "":
                    parent = parent.filter(location__area__icontains=area)
            else:
                if city and city != "":
                    parent = parent.filter(location__city__icontains=city)

        title = self.request.GET.get("title")
        title = None if title == "" else title
        if title is not None:
            return parent.filter(title__icontains=title) | parent.filter(description__icontains=title)
        else:
            return parent
