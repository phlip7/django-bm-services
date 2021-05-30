from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Locality)
admin.site.register(Area)
admin.site.register(SubArea)
admin.site.register(Gig)
admin.site.register(GigCategory)
admin.site.register(GigImage)
admin.site.register(Review)