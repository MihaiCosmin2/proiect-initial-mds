from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from MDS.settings import EMAIL_HOST_USER
from .models import CustomUser, Product, Category, Gallery, Review, Transaction, WishlistItem
from .forms import CustomAuthenticationForm, CustomRegistrationForm, ReviewForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import user_passes_test

# categories= [
    #     {'name': 'Cars', 'image': 'cars.png'},
    #     {'name': 'Houses', 'image': 'Houses.png'},
    #     {'name': 'Electronics', 'image': 'electronics.png'},
    # ]

def home(request):
    wishlist_count = 0
    if request.user.is_authenticated:
        wishlist_count = WishlistItem.objects.filter(user=request.user).count()
    categories = Category.objects.all()
    return render(request, "home.html", {'categories' : categories, 'wishlist_count': wishlist_count})

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
    signIn_form = CustomAuthenticationForm(request=request, data=request.POST or None)
    signUp_form = CustomRegistrationForm(request.POST or None)

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "sign_in" and signIn_form.is_valid():
            user = authenticate(request,
                                username=signIn_form.cleaned_data["username"],
                                password=signIn_form.cleaned_data["password"])
            if user:
                if user.blocat:
                    messages.error(request, "Account blocked. Contact the Administrator.")
                # elif not user.confirmed_email:
                #     messages.error(request, "You need to validate your e-mail!")
                else:
                    login(request, user)
                    return redirect("home")

        elif form_type == "sign_up" and signUp_form.is_valid():
            user = signUp_form.save(commit=False)
            user.confirmed_email = True
            user.save()
            login(request, user)
            return redirect("home")

    return render(request, "SignUp_OR_SignIn.html", {
        "signIn_form": signIn_form,
        "signUp_form": signUp_form,
        "errors": signUp_form.errors,
        "old": request.POST
    })


def sign_out(request):
    logout(request)
    return redirect("home")

def ad_details(request, pk):
    ad = get_object_or_404(Product, pk=pk)
    photos = ad.gallery_set.all()
    
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = WishlistItem.objects.filter(user=request.user, product=ad).exists()
        
    return render(request, "adDetails.html", {"ad": ad, "seller": ad.user, "photos": photos, 'in_wishlist': in_wishlist,})

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
        
        wishlist_items = WishlistItem.objects.filter().select_related('product')
        wishlist_users = [item.user for item in wishlist_items]
        wishlist_users = set(wishlist_users)

        for user in wishlist_users:
            subject = f"Produsul „{product.title}” a fost actualizat!"
            link = request.build_absolute_uri(reverse('ad_details', args=[product.id]))
            html_message = render_to_string('product_update_email.html', {
                'user': user,
                'product': product,
                'seller': request.user,
                'link' : link
            })
            plain_message = strip_tags(html_message)
            send_mail(
                subject,
                plain_message,
                EMAIL_HOST_USER,
                [user.email],
                html_message=html_message
            )

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

@login_required
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.user == request.user:
        messages.error(request, "You cannot buy your own product.")
        return redirect("ad_details", pk=product.id)

    try:
        transaction = Transaction.objects.create(
            seller=product.user,
            buyer=request.user,
            product=product,
            price=product.price
        )
        print(f"Transaction created: {transaction}")
        print(f"Transaction saved with id: {transaction.id}")
    except Exception as e:
        print(f"Error creating transaction: {e}")
        messages.error(request, "Failed to create transaction.")
        return redirect("ad_details", pk=product.id)

    product.sold = True
    product.save()

    subject = 'Confirmare cumpărare produs'
    html_message = render_to_string('purchase_confirmation.html', {
        'buyer': request.user,
        'seller': product.user,
        'product': product,
        'transaction': transaction,
        'review_link': request.build_absolute_uri(
        reverse('leave_review', args=[product.user.id])
    )
    })
    plain_message = strip_tags(html_message)
    from_email = EMAIL_HOST_USER
    to = [request.user.email]

    send_mail(subject, plain_message, from_email, to, html_message=html_message)

    messages.success(request, "Product bought successfully!")
    return redirect("home")


def user_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    reviews = Review.objects.filter(seller=user).select_related('buyer').order_by('-upload_date')
    return render(request, 'user_profile.html', {
        'user_profile': user,
        'reviews': reviews
    })

@login_required
def leave_review(request, seller_id):
    seller = get_object_or_404(CustomUser, id=seller_id)

    # Verificăm dacă a existat vreo tranzacție în care userul curent a cumpărat de la seller
    has_bought = Transaction.objects.filter(buyer=request.user, seller=seller).exists()
    
    # Verificăm dacă userul a lăsat deja un review pentru acel seller
    already_reviewed = Review.objects.filter(buyer=request.user, seller=seller).exists()

    if not has_bought:
        return render(request, 'not_allowed.html', {"message": "Nu poți lăsa un review fără să fi cumpărat de la acest vânzător."})

    if already_reviewed:
        return render(request, 'not_allowed.html', {"message": "Ai lăsat deja un review pentru acest vânzător."})

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.buyer = request.user
            review.seller = seller
            review.save()
            return redirect('user_profile', username=seller.username)
    else:
        form = ReviewForm()

    return render(request, 'leave_review.html', {'form': form, 'seller': seller})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, buyer=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review-ul a fost actualizat cu succes.')
            return redirect('user_profile', username=review.seller.username)
    else:
        form = ReviewForm(instance=review)
    
    return render(request, 'edit_review.html', {'form': form})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, buyer=request.user)

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review-ul a fost șters.')
        return redirect('user_profile', username=review.seller.username)

    return render(request, 'delete_review.html', {'review': review})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    WishlistItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'initial_price': product.price}
    )
    return redirect('ad_details', pk=product.id)

@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    item.delete()
    return redirect('wishlist')

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
def staff_dashboard(request):
    reviews = Review.objects.all()
    products = Product.objects.all()
    if not request.user.is_staff:
        return render(request, 'access_denied.html')  # Redirecționare către pagina personalizată
    # Logica dashboard-ului staff
    return render(request, 'dashboard.html', {'reviews': reviews, 'products': products})


@user_passes_test(is_admin)
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, "Review-ul a fost șters.")
    return redirect('staff_dashboard')

@user_passes_test(is_admin)
def delete_post(request, post_id):
    product = get_object_or_404(Product, id=post_id)
    product.delete()
    messages.success(request, "Postarea a fost ștearsă.")
    return redirect('staff_dashboard')