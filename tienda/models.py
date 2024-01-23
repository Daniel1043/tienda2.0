from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.hashers import make_password


# Con este proceso crearemos una base de datos o tablas con todos sus clases y atributos
class Marca(models.Model):  # Define una clase marca que hereda de models.Model es decir es un modelo de base de datos
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):  # Define cómo se representará el objeto Marca como una cadena
        return self.nombre  # Devuelve el nombre de la marca

    class Meta:
        verbose_name_plural = "Marcas"  # Definen como se va muestra el nombre del modelo en el panel de administración


class Producto(models.Model):
    vip = models.BooleanField(default=False)
    precio = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(limit_value=0)])
    unidades = models.PositiveIntegerField()  # Solo puede almacenar numeros enteros positivos mayor o igual a cero
    modelo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=30)
    marca = models.ForeignKey(Marca,
                              on_delete=models.CASCADE)  # Establece una relación con otro modelo en este caso Marca
    puntaje_valoracion = models.DecimalField(max_digits=3, decimal_places=1,
                                             validators=[MinValueValidator(limit_value=0),
                                                         MaxValueValidator(limit_value=10)], null=True, blank=True)

    def __str__(self):  # Define cómo se representará el objeto Producto como una cadena
        return f'{self.marca} {self.modelo}'  # Devuelve una cadena que combina el nombre de la marca y el modelo del producto

    class Meta:
        unique_together = ['marca',
                           'modelo']  # Establece una restricción en la base de datos para garantizar que la combinación de marca y modelo sea única en conjunto
        verbose_name_plural = "Productos"  # Establece cómo se mostrará el nombre de este modelo en plural en el panel de administración de Django


class Cliente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)  # Este campo establece una relación uno a uno con el modelo de usuario que se utiliza en el proyecto,  utiliza settings.AUTH_USER_MODEL para referenciar el modelo de usuario configurado en la configuración de Django
    apellidos = models.CharField(max_length=30, unique=False, null=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2)
    vip = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}'  # Devuelve el nombre de usuario del usuario asociado al cliente.

    class Meta:
        verbose_name_plural = "Clientes"




class Direccion(models.Model):
    user = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    envio = models.CharField(max_length=30, unique=False, null=True)
    facturacion = models.CharField(max_length=30, unique=False, null=True)

    def __str__(self):
        return f'{self.user.user.username}{self.envio}'

    class Meta:
        verbose_name_plural = "Direcciones"


class Tarjeta(models.Model):
    user = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nombre_ID = models.CharField(max_length=30, unique=True, null=True)
    tipo = models.CharField(max_length=30, unique=False)
    titular = models.CharField(max_length=30, unique=False, null=True)
    Caducidad = models.CharField(max_length=5, help_text='Formato: 00/00', null=True, unique=False)

    def __str__(self):
        return f'{self.user.user.username}{self.nombre_ID}'

    class Meta:
        verbose_name_plural = "Tarjetas"


class Compra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    user = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)
    unidades = models.IntegerField()
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=0.21)

    def __str__(self):
        return f'{self.user.user.username}{self.fecha}'  # Devuelve una combinación del nombre de usuario del cliente y la fecha de la compra

    class Meta:
        unique_together = ['fecha', 'producto',
                           'user']  # Establece una restricción en la base de datos para garantizar que la combinación de fecha, producto y user sea única en conjunto.
        verbose_name_plural = "Compras"


class Comentario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    user = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    texto = models.TextField(null=True)

    def __str__(self):
        return f'{self.user.user.username}{self.texto}'

    class Meta:
        verbose_name_plural = "Comentarios"