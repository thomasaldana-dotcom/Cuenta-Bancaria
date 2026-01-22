from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    numero_cuenta = models.CharField(max_length=100)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)

# Create your models here.
