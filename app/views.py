from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CreateUserForm, GigForm
from .models import *


# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Compte créé pour '+ user)
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
    # if request.method == 'POST' and \
    #     not request.user.is_anonymous() and \
    #     Purchase.objects.filter(gig_id=id, buyer=request.user).count() > 0 and \
    #     'content' in request.POST and \
    #     request.POST['content'].strip() != '':
    #     Review.objects.create(content=request.POST['content'], gig_id=id, user=request.user)

    # try:
    #     gig = Gig.objects.get(id=id)
    # except Gig.DoesNotExist:
    #     return redirect('/')

    # if request.user.is_anonymous() or \
    #     Purchase.objects.filter(gig=gig, buyer=request.user).count() == 0 or \
    #     Review.objects.filter(gig=gig, user=request.user).count() > 0:
    #     show_post_review = False
    # else:
    #     show_post_review = Purchase.objects.filter(gig=gig, buyer=request.user).count() > 0

    #reviews = Review.objects.filter(gig=gig)
    #client_token = braintree.ClientToken.generate()
    #return render(request, 'gig_detail.html', {"show_post_review": show_post_review ,"reviews": reviews, "gig": gig, "client_token": client_token})
    return render(request,  'gig-detail.html')

@login_required(login_url="signin")
def create_gig(request):
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
    return render(request, 'create-gig.html', {'error': error, 'form':gig_form})

@login_required(login_url="/")
def edit_gig(request, id):
    try:
        gig = Gig.objects.get(id=id, user=request.user)
        error = ''
        if request.method == 'POST':
            gig_form = GigForm(request.POST, request.FILES, instance=gig)
            if gig_form.is_valid():
                gig.save()
                return redirect('my_gigs')
            else:
                error = "Data is not valid"

        return render(request, 'edit-gig.html', {"gig": gig, "error": error})
    except Gig.DoesNotExist:
        return redirect('/')

@login_required(login_url="/")
def my_gigs(request):
    gigs = Gig.objects.filter(user=request.user)
    return render(request, 'my-gigs.html', {"gigs": gigs})

@login_required(login_url="/")
def profile(request, username):
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        profile.about = request.POST['about']
        profile.slogan = request.POST['slogan']
        profile.save()
    else:
        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return redirect('/')

    gigs = Gig.objects.filter(user=profile.user, status=True)
    return render(request, 'profile.html', {"profile": profile, "gigs": gigs})

@login_required(login_url="/")
def account(request, username):
    # if request.method == 'POST':
    #     profile = Profile.objects.get(user=request.user)
    #     profile.about = request.POST['about']
    #     profile.slogan = request.POST['slogan']
    #     profile.save()
    # else:
    #     try:
    #         profile = Profile.objects.get(user__username=username)
    #     except Profile.DoesNotExist:
    #         return redirect('/')

    # gigs = Gig.objects.filter(user=profile.user, status=True)
    return render(request, 'account.html')

@login_required(login_url="/")
def personal_info(request, username):
    #user = User.objects.get(username=username)
    profile = Profile.objects.get(user__username=username)
    # if request.method == 'POST':
    #     profile = Profile.objects.get(user=request.user)
    #     profile.about = request.POST['about']
    #     profile.slogan = request.POST['slogan']
    #     profile.save()
    # else:
    #     try:
    #         profile = Profile.objects.get(user__username=username)
    #     except Profile.DoesNotExist:
    #         return redirect('/')

    # gigs = Gig.objects.filter(user=profile.user, status=True)
    return render(request, 'personal-info.html', {"profile": profile})

# AJAX
def load_cities(request):
    country_id = request.GET.get('country_id')
    cities = City.objects.filter(country_id=country_id).all()
    return render(request, 'city_dropdown_list_options.html', {'cities': cities})

def load_areas(request):
    city_id = request.GET.get('city_id')
    areas = Area.objects.filter(city_id=city_id).all()
    return render(request, 'area_dropdown_list_options.html', {'areas': areas})