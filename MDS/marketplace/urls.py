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
]

