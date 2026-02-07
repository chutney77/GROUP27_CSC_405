from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Accounts(models.Model):
    fullname = models.CharField()
    email = models.CharField()
    phone = models.CharField(max_length=20)
    matric_number = models.CharField(max_length=20, unique=True)
    



    
