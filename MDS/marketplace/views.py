from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product
from .forms import CustomAuthenticationForm, CustomRegistrationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

# categories= [
    #     {'name': 'Cars', 'image': 'cars.png'},
    #     {'name': 'Houses', 'image': 'Houses.png'},
    #     {'name': 'Electronics', 'image': 'electronics.png'},
    # ]

def home(request):
    categories = Category.objects.all()
    return render(request, "home.html", {'categories' : categories,})

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return render(request, 'category_detail.html', {'category': category})


def auth_page(request):
    signIn_form = CustomAuthenticationForm(request=request, data=request.POST or None)
    signUp_form = CustomRegistrationForm(request.POST or None)
    
    if request.method == "POST" and "email" in request.POST and "password" in request.POST:
        if signIn_form.is_valid():
            user = authenticate(request, username=signIn_form.cleaned_data["username"],
                            password=signIn_form.cleaned_data["password"],)
            if user:
                if user.blocat:
                    messages.error(request, "Account blocked. Contact the Administrator.")
                elif not user.confirmed_email:
                    messages.error(request, "You need to validate your e-mail!")
                else:
                    login(request, user)
                    return redirect("home")
    elif request.method == "POST" and "password1" in request.POST:
        if signUp_form.is_valid():
            user = signUp_form.save(commit=False)
            user.confirmed_email = True # TODO: De trimis email de verificat la user
            user.save()
            login(request, user)
            return redirect("home")

    return render(request, "SignUp_OR_SignIn.html", {"signIn_form": signIn_form, "signUp_form": signUp_form,
                                                     "errors": signUp_form.errors,
                                                     "old": request.POST})

def sign_out(request):
    logout(request)
    return redirect("home")

def ad_details(request, pk):
    ad = get_object_or_404(Product, pk=pk)
    photos = ad.gallery_set.all()
    return render(request, "adDetails.html", {"ad": ad, "seller": ad.user, "photos": photos})

