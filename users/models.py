# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    ACCOUNT_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('superadmin', 'Superadmin'),
        ('user', 'User'),
        ('editor', 'Editor'),
        ('moderator', 'Moderator')
    ]

    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=False,
        null=False
    )
   
    birth_date = models.DateField(null=True, blank=True)  
    contact_number = models.CharField(max_length=11, default='', blank=True)
    email = models.EmailField(unique=True)
    last_activity = models.DateTimeField(auto_now=True)
    account_type = models.CharField(
        max_length=10,
        choices=ACCOUNT_TYPE_CHOICES,
        default='admin',
        blank=False,
        null=False
    )

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def is_online(self):
        now = timezone.now()
        return self.last_activity >= now - timezone.timedelta(minutes=5)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile_picture')
    photo = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default.png')
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.email}"
