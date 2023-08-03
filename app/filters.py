import django_filters
from .models import Gig


class GigFilter(django_filters.FilterSet):

    class Meta:
        model = Gig
        fields = ['title', 'category', 'location']

    @property
    def qs(self):
        parent = super().qs
        if self.request.GET.get('form_id') is not None:
            form_id = self.request.GET.get('form_id')
            category = self.request.GET.get('category')
            location = self.request.GET.get('location')
            if form_id == "filter":
                if category is not "":
                    parent = parent.filter(category=category)
                if location and location is not "":
                    parent = parent.filter(location=location)
            else:
                if location and location is not "":
                    parent = parent.filter(location=location)

        title = self.request.GET.get("title")
        title = None if title == "" else title
        if title is not None:
            return parent.filter(title__icontains=title) | parent.filter(description__icontains=title)
        else:
            return parent
