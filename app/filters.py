import django_filters
from .models import Gig


class GigFilter(django_filters.FilterSet):

    class Meta:
        model = Gig
        fields = ['title', 'category', 'country', 'city', 'area']

    @property
    def qs(self):
        parent = super().qs
        title = self.request.GET.get("title")
        title = None if title == "" else title
        if title is not None:
            return parent.filter(title__icontains=title) | parent.filter(description__icontains=title)
        else:
            return parent
