from django.urls import path
from . import views
from .views import EnviarValoracion,clientenUpdateview,historiaCompraClienteListview,tarjetaDeleteview,tarjetaUpdateview,tarjetaCreateView,direccionDeleteview,direccionUpdateview,direccionCreateView,tarjetasListview,direccionesListview,crearCliente, EliminarComentarioView, editarComentariosUpdateView, CheckoutDetailView,infoClienteDetail,ClientesTopListView,historiaCompraClass,productosTopClass,CheckoutDetailView,editarComentariosUpdateView,EliminarComentarioView,comprarProductCreateView, ProductoXLista, EliminarProductoView, EditarProductoView, ProductListView, ProductoXmarcaView, historiaCompraClass, productosTopClass, AboutView, LogIn,LogoutViewCl, AñadirProducto, EnviarComentario, ClientesTopListView
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', AboutView.as_view(), name='welcome'),
    path('tienda/', ProductoXLista.as_view(), name='tienda'),

    path('tienda/admin/productos', ProductListView.as_view(), name='productos'),
    path('tienda/admin/editar/<int:pk>', EditarProductoView.as_view(), name='editarProducto'),
    path('tienda/admin/eliminar/<int:pk>', EliminarProductoView.as_view(), name='eliminarProducto'),
    path('tienda/admin/nuevo/', AñadirProducto.as_view(), name='añadirProducto'),

    path('tienda/iniciar/', LogIn.as_view(), name='loge_ins'),
    path('tienda/cerrar/', LogoutViewCl.as_view(), name='cerrar_sesion_view'),

    path('tienda/detallesCompra/<int:pk>', comprarProductCreateView.as_view(), name='comprarProducto'),
    path('tienda/info/checkout/<int:pk>', CheckoutDetailView.as_view(), name='checkout'),

    path('tienda/info', ProductoXmarcaView.as_view(), name='info'),
    path('tienda/info/productoTop', productosTopClass.as_view(), name='producto_top'),
    path('tienda/info/historial_compras', historiaCompraClass.as_view(), name='historial_compras'),
    path('tienda/info/clientesTop', ClientesTopListView.as_view(), name='clientesTop'),

    path('tienda/info/newCliente', crearCliente.as_view(), name='crearCliente'),
    path('tienda/info/datosPersonales/', infoClienteDetail.as_view(), name='infoCliente'),
    path('tienda/info/editarDatosPersonales/', clientenUpdateview.as_view(), name='editarPerfil'),

    path('tienda/info/datosPersonales/Direccion', direccionesListview.as_view(), name='datosDireccion'),
    path('tienda/info/datosPersonales/nuevaDireccion', direccionCreateView.as_view(), name='nuevaDireccion'),
    path('tienda/info/datosPersonales/editarDireccion/<int:pk>', direccionUpdateview.as_view(), name='editarDireccion'),
    path('tienda/info/datosPersonales/eliminarDireccion/<int:pk>', direccionDeleteview.as_view(),name='eliminarDireccion'),

    path('tienda/info/datosPersonales/Tarjeta', tarjetasListview.as_view(), name='datosTarjeta'),
    path('tienda/info/datosPersonales/nuevaTarjeta', tarjetaCreateView.as_view(), name='nuevaTarjeta'),
    path('tienda/info/datosPersonales/editarTarjeta/<int:pk>', tarjetaUpdateview.as_view(), name='editarTarjeta'),
    path('tienda/info/datosPersonales/eliminarTarjeta/<int:pk>', tarjetaDeleteview.as_view(), name='eliminarTarjeta'),

    path('tienda/info/datosPersonales/historialMisCompras', historiaCompraClienteListview.as_view(),name='datosCompras'),

    path('tienda/info/enviarComentar/<int:pk>', EnviarComentario.as_view(), name='enviar_comentario'),
    path('tienda/info/editarcomentario/<int:pk>', editarComentariosUpdateView.as_view(), name='editar_comentario'),
    path('tienda/info/eliminarComentario/<int:pk>', EliminarComentarioView.as_view(), name='eliminarComentario'),

    path('tienda/info/enviarValoracion/<int:pk>', EnviarValoracion.as_view(), name='enviar_valoracion'),
]