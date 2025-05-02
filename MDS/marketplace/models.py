from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.urls import reverse
from django.utils.text import slugify


class CustomUserManager(BaseUserManager): # clasa care mosteneste BaseUserManager, cu asta instantiem obiectele de tip CustomUser
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The E-mail field must be set!")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True.')
        return self.create_user(email, password, **extra_fields)


# model pentru useri
class CustomUser(AbstractUser):
    # AbstractUser are deja un date_joined
    username = models.CharField(max_length=25, unique=True)
    birth_date = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(blank=True, null=True, default="")
    confirmed_email = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    blocat = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    objects = CustomUserManager()
    
    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, *kwargs)
    
    def get_absolute_url(self):
        return reverse('category', args=[self.slug])
    

# model pentru produse
class Product(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    title = models.CharField(max_length=75)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    upload_date = models.DateField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title

# model pentru imaginile atribuite produselor
class Gallery(models.Model): 
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)

# model pentru recenzii
class Review(models.Model):
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews_given')
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(1,'1 Star'), (2,'2 Stars'), (3,'3 Stars'), (4,'4 Stars'), (5,'5 Stars')])
    comment = models.TextField(blank=True, null=True)
    upload_date = models.DateField(auto_now_add=True)
    
