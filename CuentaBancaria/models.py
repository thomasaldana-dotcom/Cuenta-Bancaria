from django.db import models
from django.contrib.auth.models import User
import zoneinfo

zonas_disponibles = sorted(zoneinfo.available_timezones())
opciones_zona = tuple((zona, zona) for zona in zonas_disponibles)

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    numero_cuenta = models.CharField(max_length=100)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)

    zona_horaria = models.CharField(max_length=64, choices=opciones_zona, default='America/Bogota')

    def __str__(self):
        return f"{self.name} {self.lastname} ({self.numero_cuenta})"


class Transaccion(models.Model):
    TIPOS = (
        ('Deposito', 'Depósito'),
        ('Retiro', 'Retiro'),
        ('Transferencia', 'Transferencia'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='transacciones')
    tipo = models.CharField(max_length=25, choices=TIPOS)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True) 
    destinatario = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='transferencias_recibidas')

    def __str__(self):
        return f"{self.tipo} {self.monto}"