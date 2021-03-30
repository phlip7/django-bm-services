from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm, GigForm
from django.db.models import Q
from .models import *


# Create your views here.
def home(request):
    gigs = Gig.objects.filter(status=True)
    cities =  City.objects.all()
    categories =  GigCategory.objects.all()
    return render(request, 'home.html', {"gigs": gigs, 'cities': cities, 'categories': categories})

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            #print(form)
            if form.is_valid():
                user = User()
                user.username = form.cleaned_data.get('username')
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.email = form.cleaned_data.get('email')
                user.set_password( form.cleaned_data.get('password1'))
                user.save()

                usernam = form.cleaned_data.get('username')
                country = form.cleaned_data.get('country')
                city = form.cleaned_data.get('city')
                
                profile = Profile()
                profile.user = User.objects.get(username=usernam)
                profile.birthyear = form.cleaned_data.get('birthyear')
                profile.phone = form.cleaned_data.get('phone')
                profile.country = Country.objects.get(name=country)
                profile.city = City.objects.get(name=city)
                profile.save()
                #form.save()                
                messages.success(request, 'Compte créé pour '+ usernam)
                return redirect('signin')
    
        context = {'form': form}
        return render(request, 'signup.html', context)

def signin(request):
	if request.user.is_authenticated:
		return redirect('home')
	else:
		if request.method == 'POST':
			email = request.POST.get('email')
			password = request.POST.get('password')
			username = User.objects.get(email=email.lower()).username
			user = authenticate(request, username=username, password=password)

			if user is not None:
				login(request, user)
				return redirect('home')
			else:
				messages.info(request, 'Username OR password is incorrect')

		context = {}
		return render(request, 'signin.html', context)

def disconnect(request):
	logout(request)
	return redirect('signin')

def contact(request):
    return render(request, 'contact.html')

def gig_detail(request, id):
    try:
        gig = Gig.objects.get(id=id)
    except Gig.DoesNotExist:
        return redirect('/')
    
    if request.method == 'POST' and \
        not request.user.is_anonymous and \
        ('rating' in request.POST or 'review' in request.POST) and \
        request.POST['rating'].strip() != '':
        Review.objects.create(
            rating=request.POST['rating'], 
            rating_nb_bad= 5 - int(request.POST['rating']), 
            comment=request.POST['comment'], 
            gig_id=id, 
            user=request.user)
        return redirect('gig_detail', id=gig.id)

    reviews = Review.objects.filter(gig=gig)
    return render(request,  'gig-detail.html', {"gig": gig, "reviews": reviews})

@login_required(login_url="signin")
def gig_create(request):
    error = ''
    if request.method == 'POST':
        gig_form = GigForm(request.POST, request.FILES)
        if gig_form.is_valid():
            gig = gig_form.save(commit=False)
            gig.user = request.user
            gig.save()
            return redirect('my_gigs')
        else:
            error = "Données non valides"

    gig_form = GigForm()
    return render(request, 'gig-create.html', {'error': error, 'form':gig_form})

@login_required(login_url="/")
def gig_edit(request, id):
    try:
        gig = Gig.objects.get(id=id, user=request.user)
        countries =  Country.objects.all()
        cities =  City.objects.all()
        areas =  Area.objects.all()
        categories =  GigCategory.objects.all()
        error = ''
        if request.method == 'POST':
            gig_form = GigForm(request.POST, request.FILES, instance=gig)
            print(gig_form)
            if gig_form.is_valid():
                gig.save()
                return redirect('my_gigs')
            else:
                print(messages.error)
                error = "Data is not valid"
        gig_form = GigForm()
        return render(request, 'gig-edit.html', {"gig": gig, "error": error, 'countries': countries, 'cities': cities, 'areas': areas, 'categories': categories})
    except Gig.DoesNotExist:
        return redirect('/')

@login_required(login_url="/")
def gig_mygigs(request):
    gigs = Gig.objects.filter(user=request.user)
    return render(request, 'gig-mygigs.html', {"gigs": gigs})

def gig_search(request):
    countries =  Country.objects.all()
    cities =  City.objects.all()
    areas =  Area.objects.all()
    categories =  GigCategory.objects.all()
    location = request.GET.get('location')
    title = request.GET.get('title')

    print(title)
    print(location)

    if location and title :
        gigs = Gig.objects.filter(title__contains=title, city=location)
    elif location or title :
        gigs = Gig.objects.filter(Q(title__contains=title) | Q(city=location))
    
    print(gigs)
    return render(request, 'gig-search.html', {"gigs": gigs})
    #return render(request, 'home.html')

def profile(request, username):
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return redirect('/')

    gigs = Gig.objects.filter(user=profile.user, status=True)
    return render(request, 'profile.html', {"profile": profile, "gigs": gigs})

@login_required(login_url="/")
def account(request):
    return render(request, 'account.html')

@login_required(login_url="/")
def personal_info(request, username):
    countries =  Country.objects.all()
    cities =  City.objects.all()
    
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        user = User.objects.get(username=username)
        form_id = request.POST.get('form_id')

        if form_id == 'perso':
            user.username = request.POST['username']
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            user.save()
            profile = Profile.objects.get(user=user.id)
            profile.birthyear = request.POST['birthyear']
            profile.phone = request.POST['phone']
            profile.save()
            return redirect('personal_info', username)
        elif form_id == 'addr':
            profile.address = request.POST['address']
            profile.country = Country.objects.get(name = request.POST['country'])
            profile.city = City.objects.get(name = request.POST['city'])
            profile.save()
            return redirect('personal_info', username)
        elif form_id == 'profl':
            profile.about = request.POST['about']
            profile.slogan = request.POST['slogan']
            profile.save()
            return redirect('personal_info', username)
    else:
        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return redirect('/')

    return render(request, 'personal-info.html', {"profile": profile, "countries": countries, "cities": cities})

# AJAX
def load_cities(request):
    country_id = request.GET.get('country_id')
    cities = City.objects.filter(country_id=country_id).all()
    return render(request, 'dropdown_city_list_options.html', {'cities': cities})

def load_areas(request):
    city_id = request.GET.get('city_id')
    areas = Area.objects.filter(city_id=city_id).all()
    return render(request, 'dropdown_area_list_options.html', {'areas': areas})