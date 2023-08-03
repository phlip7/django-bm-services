from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Address)
admin.site.register(Gig)
admin.site.register(GigCategory)
admin.site.register(GigImage)
admin.site.register(Review)
