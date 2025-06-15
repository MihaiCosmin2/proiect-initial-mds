from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Gallery
from .forms import CustomAuthenticationForm, CustomRegistrationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.db.models import Q


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
    products = Product.objects.filter(category=category)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    return render(request, 'category_detail.html', {
        'category': category,
        'products': products,
        'min_price': min_price,
        'max_price': max_price,
    })



def auth_page(request):
    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "sign_in":
            signIn_form = CustomAuthenticationForm(request=request, data=request.POST or None)
            signUp_form = CustomRegistrationForm()
            if signIn_form.is_valid():
                user = authenticate(request,
                                    username=signIn_form.cleaned_data["username"],
                                    password=signIn_form.cleaned_data["password"])
                if user:
                    if user.blocat:
                        messages.error(request, "Account blocked. Contact the Administrator.")
                    elif not user.confirmed_email:
                        messages.error(request, "You need to validate your e-mail!")
                    else:
                        login(request, user)
                        return redirect("home")

        elif form_type == "sign_up":
            signIn_form = CustomAuthenticationForm()
            signUp_form = CustomRegistrationForm(request.POST or None)

            if signUp_form.is_valid():
                user = signUp_form.save(commit=False)
                user.confirmed_email = True
                user.save()
                login(request, user)
                return redirect("home")
    else:
        signIn_form = CustomAuthenticationForm()
        signUp_form = CustomRegistrationForm()


    return render(request, "SignUp_OR_SignIn.html", {
        "signIn_form": signIn_form,
        "signUp_form": signUp_form,
        "errors": signUp_form.errors
    })


def sign_out(request):
    logout(request)
    return redirect("home")

def ad_details(request, pk):
    ad = get_object_or_404(Product, pk=pk)
    photos = ad.gallery_set.all()
    return render(request, "adDetails.html", {"ad": ad, "seller": ad.user, "photos": photos})

@login_required
def add_product(request):
    categories = Category.objects.all()

    if request.method == "POST":
        title = request.POST['title']
        price = request.POST['price']
        description = request.POST['description']
        category_id = request.POST['category']
        images = request.FILES.getlist('images')

        product = Product.objects.create(
            user=request.user,
            title=title,
            price=price,
            description=description,
            category=Category.objects.get(id=category_id)
        )

        for img in images:
            Gallery.objects.create(product=product, image=img)

        messages.success(request, 'Product added successfully!')
        return redirect('add_product')

    return render(request, 'add_product.html', {'categories': categories})

@login_required
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        # Update basic info
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, 'Profile updated successfully!')

        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if current_password or new_password or confirm_password:
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'New password must be at least 8 characters long.')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Stay logged in
                messages.success(request, 'Password changed successfully.')

        return redirect('profile')

    return render(request, 'profile.html', {'user': user})

@login_required
def my_ads_view(request):
    products = Product.objects.filter(user=request.user).order_by('-upload_date')
    return render(request, 'my_ads.html', {'products': products})


@login_required
def edit_ad_view(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    categories = Category.objects.all()

    if request.method == 'POST':
        product.title = request.POST.get('title')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        category_id = request.POST.get('category')
        product.category = Category.objects.get(id=category_id)
        product.save()

        # Procesare imagini noi
        images = request.FILES.getlist('images')
        for image in images:
            Gallery.objects.create(product=product, image=image)

        messages.success(request, 'Ad updated successfully.')
        return redirect('my_ads')

    return render(request, 'edit_ad.html', {'product': product, 'categories': categories})

@login_required
def delete_image_view(request, image_id):
    image = get_object_or_404(Gallery, id=image_id, product__user=request.user)
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted.')
    return redirect('edit_ad', pk=image.product.id)


@login_required
def delete_ad_view(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Ad deleted successfully.')
    return redirect('my_ads')

def search_results(request):
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category_id = request.GET.get('category')

    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    if category_id:
        products = products.filter(category_id=category_id)

    # Pentru afișare dropdown
    categories = Category.objects.all()

    return render(request, 'search_results.html', {
        'products': products,
        'query': query,
        'categories': categories
    })