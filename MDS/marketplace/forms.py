from django import forms
from .models import CustomUser, Category, Product, Gallery, Review
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login, get_user_model
from django.core.exceptions import ValidationError


# Formular de login
class CustomAuthenticationForm(AuthenticationForm):
    # TODO: nu mai bagam atribut de ramane_logat, trebuie sa ramana mereu logat userul
    def clean(self):
        cleaned_data = super().clean()
        
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            if self.user_cache is None:
                raise forms.ValidationError("Complete all the fields!")
            elif self.user_cache.blocat:
                raise forms.ValidationError("Your account is blocked.")
            else:
                self.user_cache = authenticate(self.request, username=username, password=password)
        
        return cleaned_data
    
    def verified_email(self, user):
        if not user.confirmed_email:
            raise forms.ValidationError("You need to validate your E-mail address before Signing in !")
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = get_user_model()
        fields = ("username", "password")


# Formular de inregistrare
class CustomRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "username", "password1", "password2")
    
    def clean_email(self):
        email = self.cleaned_data.get('email').strip()
        # if email:
            # verify_email(email, debug=True)
        
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if not 3 <= len(username):
                raise forms.ValidationError("The username is too short!")
            elif not len(username) <= 20:
                raise forms.ValidationError("The username is too long!")
            
            if not username.isdigit():
                users = CustomUser.objects.exclude(pk=self.instance.pk).filter(username__iexact=username).exists()
                if users: 
                    raise forms.ValidationError("Username is already taken!")
            else:
                raise forms.ValidationError("Username can't contain only numbers!")
        return username
            
    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.phone_number = "000000000"
    #     user.confirmed_email = True
    #     if commit:
    #         user.save()
    #     return user
    