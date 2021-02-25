from django.urls import path
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('disconnect/', views.disconnect, name="disconnect"),
    path('create_gig/', views.create_gig, name="create_gig"),
]