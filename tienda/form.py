from django import forms
from datetime import datetime
from .models import Producto,Compra,Marca,Cliente,Comentario,Direccion,Tarjeta
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm


# Mediante este form traeremos los datos de nuestra base de de datos de modelos
class cambiarProducto(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['vip', 'precio', 'unidades', 'modelo', 'nombre', 'marca']





class formComentarios(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']


class iniciar_sesion(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Usuario",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contraseña",
            }
        )
    )
    next = forms.CharField(widget=forms.HiddenInput, initial="/")


class ValorarProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['puntaje_valoracion']


#MODIFICAR Y AÑADIR VALOR
class comprasForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['unidades']


class fitroForm(forms.Form):
    nombre = forms.CharField(required=False, widget=forms.TextInput({"placeholder": "Buscar. . ."}))
    marca = forms.ModelMultipleChoiceField(queryset=Marca.objects.all(), required=False,
                                           widget=forms.CheckboxSelectMultiple)


class crearUsuario(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class crearUsuarioDatos(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['apellidos', 'saldo']


class crearDireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['envio', 'facturacion']


class crearTarjetaForm(forms.ModelForm):
    class Meta:
        model = Tarjeta
        fields = ['nombre_ID', 'tipo', 'titular', 'Caducidad']

    def clean_Caducidad(self):
        caducidad = self.cleaned_data['Caducidad']
        if len(caducidad) != 5 or caducidad[2] != '/':
            raise forms.ValidationError('El formato de caducidad debe ser 00/00')

        return caducidad