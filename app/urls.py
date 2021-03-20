from django.urls import path, re_path
from app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('disconnect/', views.disconnect, name="disconnect"),
    path('contact/', views.contact, name='contact'),
    re_path(r'^gig_detail/(?P<id>[0-9]+)/$', views.gig_detail, name='gig_detail'),
    path('my_gigs/', views.my_gigs, name='my_gigs'),
    path('gig_create/', views.gig_create, name="gig_create"),
    re_path(r'^gig_edit/(?P<id>[0-9]+)/$', views.gig_edit, name='gig_edit'),
    re_path(r'^profile/(?P<username>\w+)/$', views.profile, name='profile'),
    path('account/', views.account, name='account'),
    #re_path(r'^account/(?P<username>\w+)/$', views.account, name='account'),
    re_path(r'^personal_info/(?P<username>\w+)/$', views.personal_info, name='personal_info'),

    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'), # AJAX
    path('ajax/load-areas/', views.load_areas, name='ajax_load_areas'), # AJAX
]