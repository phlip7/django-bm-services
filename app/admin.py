from django.contrib import admin
from .models import Profile, Country, City, Area, Gig, GigCategory

# Register your models here.
admin.site.register(Profile)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Area)
admin.site.register(Gig)
admin.site.register(GigCategory)