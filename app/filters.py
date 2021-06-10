import django_filters
from .models import Gig


class GigFilter(django_filters.FilterSet):

    class Meta:
        model = Gig
        fields = ['title', 'category', 'country', 'city', 'area']

    @property
    def qs(self):
        parent = super().qs
        if self.request.GET.get('form_id') is not None:
            category = self.request.GET.get('category')
            country = self.request.GET.get('country')
            city = self.request.GET.get('city')
            area = self.request.GET.get('area')
            if category is not "":
                parent = parent.filter(category=category)
            if country is not "":
                parent = parent.filter(country=country)
            if city is not "":
                parent = parent.filter(city=city)
            if area is not "":
                parent = parent.filter(area=area)

        title = self.request.GET.get("title")
        title = None if title == "" else title
        if title is not None:
            return parent.filter(title__icontains=title) | parent.filter(description__icontains=title)
        else:
            return parent
