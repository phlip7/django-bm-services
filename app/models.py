from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Country(models.Model):
    name = models.CharField(max_length=30)
    ggeoloc_url = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.name

class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    ggeoloc_url = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.name

class Locality(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    ggeoloc_url = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.name

class Area(models.Model):
    locality = models.ForeignKey(Locality, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    ggeoloc_url = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.name

class SubArea(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    name = models.CharField(max_length=70)
    ggeoloc_url = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.FileField(upload_to='avatars', default='avatars/avatar-default-1.jpeg')
    about = models.CharField(max_length=1000, null=True)
    slogan = models.CharField(max_length=500, null=True)
    birthyear = models.IntegerField(null=True) 
    phone = models.CharField(max_length=20, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.user.username

class GigCategory(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self):
        return self.name

class Gig(models.Model):
    STATUS_CHOICES = (
        (True, 'Activé'),
        (False, 'Désactivé')
    )

    title = models.CharField(max_length=500)
    category = models.ForeignKey(GigCategory, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=1000)
    price = models.CharField(max_length=500, default=0)
    cover_image = models.FileField(upload_to='gigs', default='gigs/baramogo-default-gig-1.jpeg')
    status = models.BooleanField(default=True, choices=STATUS_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    locality = models.ForeignKey(Locality, on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    subarea = models.ForeignKey(SubArea, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=True)
    website_link = models.CharField(max_length=50, null=True)
    facebook_link = models.CharField(max_length=500, null=True)
    twitter_link = models.CharField(max_length=500, null=True)
    instagram_link = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.title

class GigImage(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    image = models.FileField(upload_to='gigs', null=True, blank=True)

    def __str__(self):
        return self.gig.title

class Review(models.Model):
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    rating_nb_bad = models.IntegerField()
    comment = models.CharField(max_length=1000, null=True)

    def __str__(self):
        return self.comment