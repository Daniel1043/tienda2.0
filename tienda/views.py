from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django_filters.views import FilterView

from .filters import ProductoXmarcaFilter
from .models import Producto, Cliente, Compra, Comentario, Direccion, Tarjeta
from django.contrib.admin.views.decorators import staff_member_required
from .form import cambiarProducto, iniciar_sesion, fitroForm, comprasForm,crearUsuario,crearUsuarioDatos, \
    ValorarProductoForm, formComentarios,crearDireccionForm,crearTarjetaForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Sum, Avg
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, DetailView


# Esto enlazara con la pagina de inicio
class AboutView(TemplateView):
    template_name = "tienda/index.html"


# Utilizaremos esto para verificar si el usuario es o no un cliente
def cliente_check(user):
    return Cliente.objects.filter(user=user).exists()


# Comprobara que es un moderador
def es_moderador(user):
    return user.groups.filter(name='Moderadores').exists()


# --------------------------------------------------------------------------------------------------


# Iniciaremos sesión
class LogIn(LoginView):
    template_name = 'tienda/iniciarSesion.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        next_url = self.get_success_url()
        if not next_url:
            next_url = 'tienda/'

        return redirect(next_url)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        return response


class LogoutViewCl(LogoutView):
    def dispatch(self, request):
        logout(self.request)
        return redirect(reverse_lazy('welcome'))


#-------------------------------------------------------------------------------------------


class crearCliente(CreateView):
    template_name = 'tienda/crearUsuario.html'
    form_class = crearUsuario
    success_url = reverse_lazy('welcome')

    def form_valid(self, form):
        datos_form = crearUsuarioDatos(self.request.POST)

        if datos_form.is_valid():
            user = form.save(commit=False)
            user.save()

            datos_cliente = datos_form.cleaned_data

            # Crear el cliente con los datos recolectados
            cliente = Cliente(user=user, vip=False, **datos_cliente)
            cliente.save()

            login(self.request, user)
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datos_form'] = crearUsuarioDatos()
        return context


class infoClienteDetail(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    model = Cliente
    template_name = 'tienda/datosCliente.html'
    context_object_name = 'cliente_actual'

    def test_func(self):
        # Verifica si el usuario actual es un cliente
        return cliente_check(self.request.user)

    def get_object(self, queryset=None):
        return get_object_or_404(Cliente, user=self.request.user)


class clientenUpdateview(UpdateView):
    template_name = 'tienda/editarPerfilP.html'
    model = Cliente
    form_class = crearUsuarioDatos
    second_form_class = crearUsuario
    success_url = reverse_lazy('welcome')

    def get_object(self, queryset=None):
        # Obtener el objeto Cliente asociado al usuario actual
        return Cliente.objects.get(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregamos los dos formularios al contexto con nombres diferentes
        context['formE'] = self.form_class(instance=self.object)
        context['formUsuario'] = self.second_form_class(instance=self.object.user)
        return context

    def form_valid(self, form):
        # Guardar el formulario principal (crearUsuarioDatos)
        response = super().form_valid(form)
        # Guardar el segundo formulario (crearUsuario)
        form2 = self.second_form_class(self.request.POST, instance=self.object.user)
        if form2.is_valid():
            form2.save()
        return response


# --------------------------------------------------------------------------

class tarjetasListview(LoginRequiredMixin, UserPassesTestMixin, ListView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    model = Tarjeta
    template_name = 'tienda/direccionCliente.html'
    context_object_name = 'datos_cliente_tarjeta'

    def test_func(self):
        return cliente_check(self.request.user)

    def get_queryset(self):
        cliente_actual = Cliente.objects.get(user=self.request.user)

        return Tarjeta.objects.filter(user=cliente_actual).all()


class tarjetaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    template_name = 'tienda/añadir/añadirDr.html'
    form_class = crearTarjetaForm
    success_url = reverse_lazy('datosTarjeta')

    def test_func(self):
        return cliente_check(self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user.cliente
        return super().form_valid(form)


class tarjetaUpdateview(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    template_name = 'tienda/actualizar/editarDR.html'
    model = Tarjeta
    form_class = crearTarjetaForm
    success_url = reverse_lazy('datosTarjeta')

    def test_func(self):
        return cliente_check(self.request.user)

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Tarjeta, pk=pk)


class tarjetaDeleteview(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    template_name = 'tienda/eliminar/eliminarDR.html'
    model = Tarjeta
    success_url = reverse_lazy('datosTarjeta')

    def test_func(self):
        return cliente_check(self.request.user)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.success_url)


# ---------------------------------------------------------------------------------------


class direccionesListview(LoginRequiredMixin, UserPassesTestMixin, ListView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    model = Direccion
    template_name = 'tienda/direccionCliente.html'
    context_object_name = 'datos_cliente'

    def test_func(self):
        return cliente_check(self.request.user)

    def get_queryset(self):
        cliente_actual = Cliente.objects.get(user=self.request.user)
        return Direccion.objects.filter(user=cliente_actual).all()


class direccionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    template_name = 'tienda/añadir/añadirDr.html'
    form_class = crearDireccionForm
    success_url = reverse_lazy('datosDireccion')

    def test_func(self):
        return cliente_check(self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user.cliente
        return super().form_valid(form)


class direccionUpdateview(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    template_name = 'tienda/actualizar/editarDR.html'
    model = Direccion
    form_class = crearDireccionForm
    success_url = reverse_lazy('datosDireccion')

    def test_func(self):
        return cliente_check(self.request.user)

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Direccion, pk=pk)


class direccionDeleteview(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    template_name = 'tienda/eliminar/eliminarDR.html'
    model = Direccion
    success_url = reverse_lazy('datosDireccion')

    def test_func(self):
        return cliente_check(self.request.user)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.success_url)


# ------------------------------------------------------------

class historiaCompraClienteListview(ListView):
    model = Compra
    template_name = 'tienda/direccionCliente.html'
    context_object_name = 'comprasActualCliente'

    def get_queryset(self):
        cliente_actual = self.request.user.cliente

        return Compra.objects.filter(user=cliente_actual).order_by('-fecha')


# --------------------------------------------------------------------------------------------------

    # Pasara todos los productos que ya existen en producto
class ProductListView(LoginRequiredMixin,UserPassesTestMixin,ListView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    model = Producto
    template_name = 'tienda/producto.html'
    context_object_name = 'Productos'

    def test_func(self):
        # Verifica si el usuario actual es miembro del staff
        return self.request.user.is_staff
    def get_queryset(self):
        return Producto.objects.all()




# Permitira editar los productos ya existentes
class EditarProductoView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    model = Producto
    form_class = cambiarProducto
    template_name = 'tienda/editar.html'
    success_url = reverse_lazy('productos')

    def test_func(self):
        # Verifica si el usuario actual es miembro del staff
        return self.request.user.is_staff
    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Producto, pk=pk)




class EliminarProductoView(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    model = Producto
    template_name = 'tienda/confirmarEliminar.html'
    success_url = reverse_lazy('productos')

    def test_func(self):
        # Verifica si el usuario actual es miembro del staff
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.success_url)




class AñadirProducto(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    template_name = 'tienda/nuevo.html'
    form_class = cambiarProducto
    success_url = reverse_lazy('productos')

    def test_func(self):
        # Verifica si el usuario actual es miembro del staff
        return self.request.user.is_staff
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


# --------------------------------------------------------------------------------------------------
class ProductoXLista( FilterView):
    template_name = 'tienda/tienda.html'
    filterset_class = ProductoXmarcaFilter
    context_object_name = 'Productos'




class comprarProductCreateView(CreateView):
    model = Compra
    template_name = 'tienda/compraProducto.html'
    form_class = comprasForm
    second_form_class = ValorarProductoForm
    third_form_class =formComentarios

    def get_success_url(self):
        return f'/tienda/info/checkout/{self.object.pk}/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        producto = get_object_or_404(Producto, pk=pk)

        context['producto'] = producto
        context['valoracion'] = self.second_form_class()
        context['comentariosMostrar'] = Comentario.objects.all()
        context['comt'] = self.third_form_class(self.request.GET)
        return context

    @transaction.atomic
    def form_valid(self, form):
        pk = self.kwargs['pk']
        producto = get_object_or_404(Producto, pk=pk)
        valoracion = self.second_form_class(self.request.POST)
        unidades = form.cleaned_data['unidades']

        if valoracion.is_valid():
            puntaje = valoracion.cleaned_data['puntaje_valoracion']

        if unidades <= producto.unidades:
            cliente = Cliente.objects.get(user=self.request.user)
            producto.unidades -= unidades

            if producto.puntaje_valoracion is not None and puntaje is not None:
                producto.puntaje_valoracion += puntaje

            producto.save()

            compra = Compra()
            compra.producto = producto
            compra.user = cliente
            compra.unidades = unidades
            compra.importe = unidades * producto.precio
            compra.fecha = timezone.now()
            compra.save()

            cliente.saldo -= compra.importe
            cliente.save()

            return super().form_valid(form)







class CheckoutDetailView(LoginRequiredMixin,UserPassesTestMixin,DetailView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    model = Compra
    template_name = 'tienda/checkout.html'
    context_object_name = 'compra'


    def test_func(self):
        # Verifica si el usuario actual es un cliente
        return cliente_check(self.request.user)

    def get_object(self, queryset=None):
        return Compra.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compra = self.object
        producto = compra.producto
        importe = compra.unidades * producto.precio
        context['producto'] = producto
        context['importe'] = importe
        return context








class EnviarComentario(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    form_class = formComentarios
    template_name = 'tienda/compraProducto.html'

    def test_func(self):
        # Verifica si el usuario actual es un cliente
        return cliente_check(self.request.user)
    def form_valid(self, form):
        pk = self.kwargs['pk']  # Obtiene el 'pk' de los argumentos de la URL
        product = get_object_or_404(Producto, pk=pk)
        comentarioUsuario = form.cleaned_data['texto']
        cliente = Cliente.objects.get(user=self.request.user)

        nuevo_comentario = Comentario(producto=product, user=cliente, texto=comentarioUsuario)
        nuevo_comentario.save()
        return redirect('comprarProducto', pk=pk)

    def get_success_url(self):
        pk = self.kwargs['pk']  # Obtiene el 'pk' de los argumentos de la URL
        return reverse_lazy('comprarProducto', kwargs={'pk': pk})


class editarComentariosUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    model = Comentario
    form_class = formComentarios
    template_name = 'tienda/editar_comentarios.html'
    context_object_name = 'comentario'

    def test_func(self):
        # Verifica si el usuario actual es un cliente
        return cliente_check(self.request.user)

    def get_success_url(self):
        return reverse_lazy('comprarProducto', kwargs={'pk': self.object.producto.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        return response





class EliminarComentarioView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    login_url = "/tienda/tienda/iniciar/"
    redirect_field_name = "tienda/iniciarSesion.html"
    model = Comentario
    template_name = 'tienda/eliminarComentario.html'  # Reemplaza con la plantilla adecuada
    context_object_name = 'comentario'


    def test_func(self):
        # Verifica si el usuario actual es un moderador
        return es_moderador(self.request.user)

    def get_success_url(self):
        # Obtener el ID del producto antes de eliminar el comentario
        producto_id = self.object.producto.id
        return reverse_lazy('comprarProducto', kwargs={'pk': producto_id})

    def delete(self, request, *args, **kwargs):
        # Obtener el ID del producto antes de eliminar el comentario
        producto_id = self.get_object().producto.id
        response = super().delete(request, *args, **kwargs)
        return redirect('comprarProducto', pk=producto_id)


# --------------------------------------------------------------------------------------------------



class ProductoXmarcaView(FilterView):
    template_name = 'tienda/info.html'  # Reemplaza 'tu_template.html' con la ruta correcta a tu template
    filterset_class = ProductoXmarcaFilter
    context_object_name = 'productos'



# Mostrara los productos más vendidos en la tienda
class productosTopClass(ListView):
    model = Producto
    template_name = 'tienda/info.html'
    context_object_name = 'producto_top'

    def get_queryset(self):
        return Producto.objects.annotate(sum_unidades=Sum('compra__unidades'),sum_importes=Sum('compra__importe')).order_by('-sum_unidades')[:10]  # annotate() se utiliza para realizar operaciones de agregación en los objetos



#Muestra el historial de las compras de todos los usuarios
class historiaCompraClass(ListView):
    model = Compra
    template_name = 'tienda/info.html'
    context_object_name = 'compras'

    def get_queryset(self):
        return Compra.objects.all().annotate(Count('fecha', distinct=True)).order_by('-fecha')[:10]


#Muestra los clientes que más han gastado
class ClientesTopListView(ListView):
    model = Cliente
    template_name = 'tienda/info.html'
    context_object_name = 'top_clientes'

    def get_queryset(self):
        return Cliente.objects.annotate(dinero_gastado=Sum('compra__importe')).order_by('-dinero_gastado')[:3]





#-------------------------------------------------------
# class AgregarAlCarritoView(CreateView):
#     template_name = 'agregar_al_carrito.html'
#     form_class = AgregarAlCarritoForm
#     success_url = reverse_lazy('ver_carrito')
#
#     def form_valid(self, form):
#         cantidad = form.cleaned_data['cantidad']
#         producto_id = self.kwargs['producto_id']
#         producto = Producto.objects.get(id=producto_id)
#
#
#             carrito = self.request.carrito
#
#             carrito.productos.add(producto, through_defaults={'cantidad': cantidad})
#
#         return super().form_valid(form)
#
# class VerCarritoView(ListView):
#     template_name = 'ver_carrito.html'
#     model = ItemCarrito
#     context_object_name = 'items'
#
#     def get_queryset(self):
#         if self.request.user.is_authenticated:
#             carrito = self.request.carrito
#             return carrito.productos.all()



# class ComprarCarritoView(CreateView):
#     template_name = 'comprar_carrito.html'
#     form_class = ComprarCarritoForm  # Asegúrate de tener un formulario apropiado
#     success_url = reverse_lazy('pagina_de_exito_compra')  # Cambia esto con la URL deseada después de la compra
#
#     def form_valid(self, form):
#         if self.request.user.is_authenticated:
#             carrito = self.request.carrito
#
#             # Itera sobre los productos en el carrito y realiza la compra para cada uno
#             for producto in carrito.productos.all():
#                 Compra.objects.create(
#                     carrito=carrito,
#                     producto=producto,
#                     unidades=producto.unidades,
#                     importe=producto.precio * producto.unidades,
#                     iva=producto.precio * producto.unidades * 0.21
#                 )
#
#             # Limpia el carrito después de la compra
#             carrito.productos.clear()
#
#         return super().form_valid(form)