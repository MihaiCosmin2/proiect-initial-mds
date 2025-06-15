from .models import WishlistItem

def wishlist_count_processor(request):
    if request.user.is_authenticated:
        count = WishlistItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'wishlist_count': count}
