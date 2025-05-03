from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Product, Gallery
from django.utils.html import format_html


admin.site.site_header = "Marketplace Dashboard"
admin.site.site_title = "+++"
admin.site.index_title = "Admin"

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("username", "email", "phone_number", "is_active") # am sters 'is_staff' de aici ca daca intra vre un hacker si da disable la toate checkboxurile de is staff de la admini ce facem, primim maine dimineata pe birou o felicitare cum ar zice cineva
    list_filter = ("is_active",)

    fieldsets = (
        ("Personal Info", {"fields": ("username", "password", "email", "phone_number", "birth_date", "address", "profile_picture")}),
        ("Permissions", {"fields": ("is_active", "confirmed_email", "blocat")}),
        ("Important Dates", {"fields": ("last_login","date_joined")}),
    )

    readonly_fields = ("date_joined", "last_login") 

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "phone_number", "is_active"),
        }),
    )

    search_fields = ("email", "username")
    ordering = ("username",)
    
    # suprascriem get_readonly_fields ca 'blocat' sa fie modificabil doar pentru userii normali, iar pentru superuseri si admin sa nu fie modificabil
    def get_readonly_fields(self, request, obj=None):
        ro_fields = list(self.readonly_fields)
        if obj is not None:
            if obj.is_staff or obj.is_superuser:
                ro_fields.append("blocat")
        return ro_fields
    
    

admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class GalleryInline(admin.TabularInline):
    model = Gallery
    fk_name = "product"
    extra = 1
    readonly_fields = ("preview",)
    
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:80px; object-fit:cover;" />', obj.image.url)
        return ""
    preview.short_description = "Thumb"
    
@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "category", "upload_date", "views")
    search_fields = ("title",)
    inlines = [GalleryInline]