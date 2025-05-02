from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home, name="home"),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path("auth/", views.auth_page, name="auth"),
    path("logout/", views.sign_out, name="logout"),
    path("ad/<int:pk>/", views.ad_details, name="ad_details")
]

