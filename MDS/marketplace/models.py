from django.db import models
from django.contrib.auth.models import AbstractUser

# model pentru useri
class CustomUser(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    birth_date = models.DateField()
    address = models.TextField()
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=12)
    verified = models.BooleanField(default=False)
    confirmed_email = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True) 
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    def __str__(self):
        return self.username

# model pentru categorii
class Category(models.Model): 
    name = models.CharField(max_length=25)
    
    def __str__(self):
        return self.name

# model pentru produse
class Product(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    name = models.CharField(max_length=75)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# model pentru imaginile atribuite produselor
class Image(models.Model): 
    id_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)

# model pentru recenzii
class Review(models.Model):
    id_buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews_given')
    id_seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews_received')
    rating = models.IntegerField(choices=[(1,'1 Star'), (2,'2 Stars'), (3,'3 Stars'), (4,'4 Stars'), (5,'5 Stars')])
    comment = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)