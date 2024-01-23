from django.contrib import admin
from .models import Marca,Producto,Compra,Cliente,Comentario,Direccion,Tarjeta

admin.site.register(Cliente)
admin.site.register(Direccion)
admin.site.register(Tarjeta)
admin.site.register(Marca)
admin.site.register(Compra)
admin.site.register(Producto)
admin.site.register(Comentario)


