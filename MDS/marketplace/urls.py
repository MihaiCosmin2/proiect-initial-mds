from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path("auth/", views.auth_page, name="auth"),
    path("logout/", views.sign_out, name="logout"),
    path("ad/<int:pk>/", views.ad_details, name="ad_details"),
    path('add-product/', views.add_product, name='add_product'),
    path('profile/', views.profile_view, name='profile'),
    path('delete-image/<int:image_id>/', views.delete_image_view, name='delete_image'),
    path('my-ads/', views.my_ads_view, name='my_ads'),
    path('edit-ad/<int:pk>/', views.edit_ad_view, name='edit_ad'),
    path('delete-ad/<int:pk>/', views.delete_ad_view, name='delete_ad'),
    path('search/', views.search_results, name='search_results'),
    path("buy/<int:product_id>/", views.buy_product, name="buy_product"),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('review/<int:seller_id>/', views.leave_review, name='leave_review'),
    path('review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/delete_review/<int:review_id>/', views.delete_review_admin, name='delete_review_admin'),
    path('staff/delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
]

