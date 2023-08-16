from django.db import models
from django.contrib.auth.models import User
from django.db.models.manager import ManagerDescriptor
from django.utils import timezone


# Create your models here.
class Address(models.Model):
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    area = models.CharField(max_length=255, null=True, blank=True)
    lat = models.DecimalField(max_digits=25, decimal_places=20)
    lng = models.DecimalField(max_digits=25, decimal_places=20)

    def __str__(self):
        return self.address


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.FileField(upload_to='avatars')
    about = models.CharField(max_length=1000, null=True)
    slogan = models.CharField(max_length=500, null=True)
    birthday = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, null=True)
    location = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
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
    cover_image = models.FileField(upload_to='gigs')
    status = models.BooleanField(default=True, choices=STATUS_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    create_time = models.DateTimeField(default=timezone.now)
    location = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    website_link = models.CharField(max_length=50, null=True)
    facebook_link = models.CharField(max_length=500, null=True)
    twitter_link = models.CharField(max_length=500, null=True)
    instagram_link = models.CharField(max_length=500, null=True)

    def __str__(self):
        return self.title

    @property
    def city(self):
        return self.location.city


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
