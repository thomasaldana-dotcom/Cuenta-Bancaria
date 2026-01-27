# CuentaBancaria/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Cliente
import random

@receiver(post_save, sender=User)
def crear_perfil_cliente(sender, instance, created, **kwargs):
    if created:
        if not Cliente.objects.filter(user=instance).exists():
            numero_cuenta = random.randint(1000000000, 9999999999)

            Cliente.objects.create(
                user=instance,
                email=instance.email,
                name=instance.first_name,
                lastname=instance.last_name,
                age=0,
                numero_cuenta=str(numero_cuenta),
                saldo=0
            )