from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category

admin.site.site_header = "Marketplace Dashboard"
admin.site.site_title = "+++"
admin.site.index_title = "Admin"

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "phone_number", "verified", "is_staff", "is_active")
    list_filter = ("verified", "is_staff", "is_active")

    fieldsets = (
        ("Personal Info", {"fields": ("username", "password", "email", "phone_number", "birth_date", "address", "profile_picture")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "verified", "confirmed_email")}),
        ("Important Dates", {"fields": ("last_login","date_joined")}),
    )

    readonly_fields = ("date_joined", "last_login") 

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "phone_number", "is_staff", "is_active"),
        }),
    )

    search_fields = ("email", "username")
    ordering = ("username",)

admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

