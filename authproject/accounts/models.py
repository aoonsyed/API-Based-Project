from django.db import models

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = (
        ('user','User'),
        ('contributor','Contributor')
    )

    username = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    isadmin = models.BooleanField(default=False)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices = ROLE_CHOICES, default='user')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username