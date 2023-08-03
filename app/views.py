from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
# from PIL import Image
from .filters import GigFilter
from .forms import CreateUserForm, GigForm, ProfileForm, PasswordResetForm, SetPasswordForm, AddressForm
from django.db.models import Q
from .models import *
from .tokens import account_activation_token
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from .send_sms import send_sms


# Create your views here.
def home(request):
    gigs = Gig.objects.filter(status=True)
    locations = Address.objects.all()
    categories = GigCategory.objects.all()
    gig_filter = GigFilter(request.GET, queryset=gigs)
    return render(request, 'home.html',
                  {"gigs": gigs, 'location': locations, 'categories': categories, 'gig_filter': gig_filter})


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                register_type = form.cleaned_data.get('registration_type')
                user = User()
                user.username = form.cleaned_data.get('username')
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.email = form.cleaned_data.get('email').lower() if register_type == 'email' else ''
                user.set_password(form.cleaned_data.get('password1'))
                user.is_active = False
                user.save()

                username = form.cleaned_data.get('username')
                # Saving Address
                address = Address()
                address.address = form.cleaned_data.get('address')
                address.lat = form.cleaned_data.get('lat')
                address.lng = form.cleaned_data.get('lng')
                address.save()

                # Saving Profile
                profile = Profile()
                profile.user = User.objects.get(username=username)
                profile.birthday = form.cleaned_data.get('birthday')
                profile.phone = form.cleaned_data.get('phone') if register_type == 'phone' else ''
                profile.location_id = address.id
                profile.save()
                result = activate_via_email_or_sms(request, user, profile, form.cleaned_data.get('email'),
                                                   register_type)
                if result:
                    return redirect('signin')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        context = {'form': form}
        return render(request, 'signup.html', context)


def activate_via_email_or_sms(request, user, profile, to_email, register_type):
    domain = get_current_site(request).domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)
    protocol = 'https' if request.is_secure() else 'http'
    sms_url = f'{protocol}://{domain}/activate/{uid}/{token}'
    if register_type == 'email':
        mail_subject = "Activez votre compte utilisateur."
        message = render_to_string("email_templates/activate_account.html", {
            'user': user.username,
            'domain': domain,
            'uid': uid,
            'token': token,
            "protocol": protocol
        })
        email = EmailMessage(mail_subject, message, to=[to_email])
        if email.send():
            messages.success(request,
                             f'Cher <b>{user}</b>, Veuillez vous rendre dans votre boîte de réception e-mail <b>{to_email}</b> et cliquer sur le lien d\'activation reçu pour confirmer et terminer l\'inscription.')
            return True
        else:
            messages.error(request,
                           f'Problème d\'envoi d\'e-mail à {to_email}, vérifiez si vous l\'avez saisi correctement.')
            return False
    else:
        sms_body = f'Veuillez cliquer sur le lien ci-dessous pour confirmer votre inscription:\n' \
                   f'{sms_url}'
        res_is_ok = send_sms(sms_body, profile.phone)
        if not res_is_ok:
            messages.error(request, "Échec de l'envoi du lien de vérification sur votre téléphone.")
            return False
        else:
            messages.success(request, "Nous avons envoyé le lien de vérification sur votre téléphone avec succès.")
            return True


def activate(request, uidb64, token):
    user_info = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = user_info.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('signin')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('home')


def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            email_or_phone = request.POST.get('email')
            password = request.POST.get('password')
            user_by_email = User.objects.filter(email=email_or_phone.lower())
            profile_by_phone = Profile.objects.filter(phone=email_or_phone)
            if len(user_by_email) > 0:
                user_instance = user_by_email[0]
                return auth(request, user_instance.username, password)
            elif len(profile_by_phone) > 0:
                user_instance = profile_by_phone[0].user
                return auth(request, user_instance.username, password)
            else:
                messages.info(request, 'email OU mot de passe incorrect')
                return redirect('signin')

        return render(request, 'signin.html')


def auth(request, username, password):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('home')
    else:
        messages.info(request, 'email OU mot de passe incorrect')
        return redirect('signin')


def password_reset_request(request):
    if request.method == 'POST':
        email_or_phone = request.POST.get('email')
        user_by_email = User.objects.filter(email=email_or_phone.lower())
        profile_by_phone = Profile.objects.filter(phone=email_or_phone)
        # 0->Email, 1->Phone
        verify_type = 0
        if len(user_by_email) > 0:
            associated_user = user_by_email[0]
        elif len(profile_by_phone) > 0:
            verify_type = 1
            associated_user = profile_by_phone[0].user
        else:
            print("=======Can't find data======")
            messages.error(request, "L'e-mail ou le numéro de téléphone est incorrect.")
            return redirect('password_reset')
        # SMS or Email Content Info
        domain = get_current_site(request).domain
        uid = urlsafe_base64_encode(force_bytes(associated_user.pk))
        token = account_activation_token.make_token(associated_user)
        protocol = 'https' if request.is_secure() else 'http'
        sms_url = f'{protocol}://{domain}/reset/{uid}/{token}'
        has_sent = False
        if verify_type == 0:
            subject = "Demande de réinitialisation du mot de passe"
            message = render_to_string("email_templates/reset_password.html", {
                'user': associated_user,
                'domain': domain,
                'uid': uid,
                'token': token,
                "protocol": protocol
            })
            email = EmailMessage(subject, message, to=[associated_user.email])
            if email.send():
                has_sent = True
                messages.success(request,
                                 """<h2>Réinitialisation du mot de passe envoyée</h2><hr> <p> Nous vous avons 
                                 envoyé par e-mail des instructions pour définir votre mot de passe, si un compte 
                                 existe avec l'e-mail que vous avez saisi. Vous devriez les recevoir sous 
                                 peu.<br>Si vous ne recevez pas d'e-mail, assurez-vous d'avoir entré l'adresse 
                                 avec laquelle vous vous êtes inscrit et vérifiez votre dossier spam. </p> """
                                 )
            else:
                messages.error(request,
                               "Problème d'envoi de l'e-mail de réinitialisation du mot de passe, <b>SERVER PROBLEM</b>")
        else:
            sms_body = f'Veuillez suivre ce lien pour réinitialiser votre mot de passe:\n' \
                       f'{sms_url}'
            has_sent = send_sms(sms_body, profile_by_phone[0].phone)
            if has_sent:
                messages.success(request, "Envoyé un lien de réinitialisation du mot de passe sur votre téléphone.")
            else:
                messages.error(request, "Échec de l'envoi du lien de réinitialisation du mot de passe par SMS.")

        # Redirect to Home when sending SMS or Email is success
        if has_sent:
            return redirect('home')

    form = PasswordResetForm()
    return render(
        request=request,
        template_name="password_reset.html",
        context={"form": form}
    )


def passwordResetConfirm(request, uidb64, token):
    user_info = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = user_info.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('home')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Something went wrong, redirecting back to Homepage')
    return redirect("home")


# def resize_image(imagename, ref_size):
#     # ''' resize if image is greater than the reference size '''
#     print('fefdfs')
#     print(imagename)
#     print(ref_size)
#     img = Image.open(imagename)
#     (width, height) = img.size
#     img = img.resize(ref_size)
#     img.save(imagename)
#     #if width > ref_size[0] or height > ref_size[1]:
#     #    img = img.resize(ref_size)
#     #    img.save(imagename)
#     #print('size : {}'.format(img.size))
#     #print('L : {} '.format(img.size[0]))
#     print(imagename)
#     return imagename


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
            rating_nb_bad=5 - int(request.POST['rating']),
            comment=request.POST['comment'],
            gig_id=id,
            user=request.user)
        return redirect('gig_detail', id=gig.id)

    reviews = Review.objects.filter(gig=gig)
    gig_images = GigImage.objects.filter(gig=gig)
    gig_similars = Gig.objects.filter(category=gig.category)
    return render(request, 'gig-detail.html',
                  {"gig": gig, "reviews": reviews, "gig_images": gig_images,
                   "gig_similars": gig_similars})


@login_required(login_url="signin")
def gig_create(request):
    error = ''
    if request.method == 'POST':
        try:
            gig_form = GigForm(request.POST, request.FILES)
            address_form = AddressForm(request.POST)
            images = request.FILES.getlist('images')
            if images is not None and len(images) > 6:
                error = "Nombre maximum de photos atteint!!" \
                        " Supprimes quelques photos existantes" \
                        " avant d’importer des photos nouvelles."
            else:
                if gig_form.is_valid() and address_form.is_valid():
                    # Saving Address
                    address = Address()
                    address.address = address_form.cleaned_data.get('address')
                    address.lat = address_form.cleaned_data.get('lat')
                    address.lng = address_form.cleaned_data.get('lng')
                    address.save()

                    gig = gig_form.save(commit=False)
                    gig.user = request.user
                    gig.location = address
                    gig.save()
                    if images is not None:
                        for image in images:
                            img = GigImage.objects.create(gig=gig, image=image)

                    return redirect('gig_mygigs')
                else:
                    messages.error(request, "Données non valides")
        except Exception as err:
            print("========Error====", err)
            messages.error(request, "Quelque chose s'est mal passé.")
            redirect('gig_create')

    gig_form = GigForm()
    address_form = AddressForm()
    return render(request, 'gig-create.html', {'gig_form': gig_form, 'address_form': address_form})


@login_required(login_url="/")
def gig_edit(request, id):
    try:
        gig = Gig.objects.get(id=id, user=request.user)
        address = gig.location
        categories = GigCategory.objects.all()
        error = ''
        gig_images = GigImage.objects.filter(gig=gig)
        if request.method == 'POST':
            images = request.FILES.getlist('images')
            gig_form = GigForm(request.POST, request.FILES, instance=gig)
            address_form = AddressForm(request.POST, instance=address)
            if len(gig_images) + len(images) > 6:
                error = "Nombre maximum de photos atteint!!" \
                        " Supprimes quelques photos existantes" \
                        " avant d’importer des photos nouvelles."
            else:
                if gig_form.is_valid() and address_form.is_valid():
                    gig.save()
                    address_form.save()
                    if images is not None:
                        for image in images:
                            GigImage.objects.create(gig=gig, image=image)
                    return redirect('gig_mygigs')
                else:
                    print(messages.error)
                    error = "Data is not valid"
        gig_form = GigForm()
        return render(request, 'gig-edit.html',
                      {"gig": gig, "address": address, "error": error, 'categories': categories, "gig_images": gig_images})
    except Exception as error:
        return redirect('/')


@login_required(login_url="/")
def gig_mygigs(request):
    gigs = Gig.objects.filter(user=request.user)
    return render(request, 'gig-mygigs.html', {"gigs": gigs})


def gig_search(request):
    categories = GigCategory.objects.all()
    gigs = Gig.objects.all()

    gig_filter = GigFilter(request=request)
    gigs = gig_filter.qs

    context = {"gigs": gigs, 'categories': categories, 'gig_filter': gig_filter}
    return render(request, 'gig-search.html', context)
    # return render(request, 'home.html')


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
    form = ProfileForm(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        profile = Profile.objects.get(user=request.user)
        user = User.objects.get(username=username)
        form_id = request.POST.get('form_id')

        if request.user != user:
            messages.warning(request, "Vous n'êtes pas autorisé à modifier ces informations.")
            return redirect('personal_info', username)

        if form_id == 'perso':
            user.username = request.POST['username']
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            user.save()
            profile = Profile.objects.get(user=user.id)
            if form.is_valid():
                profile.birthday = form.cleaned_data.get('birthday')
                profile.phone = form.cleaned_data.get('phone')
            profile.save()
            return redirect('personal_info', username)
        elif form_id == 'addr':
            address = Address()
            address.address = request.POST['address']
            address.lat = request.POST['lat']
            address.lng = request.POST['lng']
            address.save()
            profile.location = address
            profile.save()
            return redirect('personal_info', username)
        elif form_id == 'profl':
            profile.about = request.POST['about']
            profile.slogan = request.POST['slogan']
            if 'avatar' in request.FILES:
                avatar = request.FILES['avatar']
                print(avatar)
                profile.avatar = avatar
                # fs = FileSystemStorage(location='avatars/')
                # filename = fs.save(avatar.name, avatar)
                # print(fs.url(filename))
            profile.save()
            return redirect('personal_info', username)
    else:
        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return redirect('/')

    return render(request, 'personal-info.html', {"profile": profile, "form": form})


@login_required(login_url="/")
def delete_confirm(request, id, father_id):
    # ''' id : id the item to delete. father_id : id of the entity (gig, ...) calling the deletion '''
    if request.method == 'POST':
        form_id = request.POST.get('form_id')
        if form_id == 'gig_img':
            GigImage.objects.filter(id=request.POST['item_id']).delete()
            return redirect('gig_edit', father_id)

    context = {"item_id": id, 'father_id': father_id}
    return render(request, 'delete-confirm.html', context)


# AJAX
def load_cities(request):
    country_id = request.GET.get('country_id')
    # cities = City.objects.filter(country_id=country_id).all()
    return render(request, 'dropdown_city_list_options.html')


def load_localities(request):
    city_id = request.GET.get('city_id')
    # localities = Locality.objects.filter(city_id=city_id).all()
    return render(request, 'dropdown_locality_list_options.html')


def load_areas(request):
    locality_id = request.GET.get('locality_id')
    # areas = Area.objects.filter(locality_id=locality_id).all()
    return render(request, 'dropdown_area_list_options.html')


def load_subareas(request):
    area_id = request.GET.get('area_id')
    # subareas = SubArea.objects.filter(area_id=area_id).all()
    return render(request, 'dropdown_subarea_list_options.html')
