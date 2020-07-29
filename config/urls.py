from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views

from tienda.users.views import (
        Indice, ListadoProducto, DetalleProducto, ComentarioProducto,
        Ingresar, Salir, CambiarPerfil, AniadirCarrito, 
        ListarCarrito, ListarCarritoPendientes, ListarCarritoFinalizadas,
        DetailPaymentView, EliminarCarrito, SummaryView, updateCar
    )

urlpatterns = [
     path('',Indice.as_view(),name='indice'),

    #usuarios 
    path('ingresar/',Ingresar.as_view(),name='ingresar'),

    path('salir/',Salir.as_view(),name='salir'),

    path('cambiar_perfil/',CambiarPerfil.as_view(),name='cambiar_perfil'),

    #productos
    path('listado_productos/',ListadoProducto.as_view(),name='listado_productos'),

    path('detalle_producto/<int:pk>/',DetalleProducto.as_view(),name='detalle_productos'),

    path('crear_comentario/',ComentarioProducto.as_view(),name='crear_comentario'),

    path('aniadir_carrito/',AniadirCarrito.as_view(),name='aniadir_carrito'),

    path('listar_carrito/',ListarCarrito.as_view(),name='listar_carrito'),

    path('listar_pendientes/',ListarCarritoPendientes.as_view(),name='listar_pendientes'),

    path('listar_finalizado/',ListarCarritoFinalizadas.as_view(),name='listar_finalizado'),

    path('eliminar_carrito/<int:pk>/',EliminarCarrito.as_view(),name='eliminar_carrito'),

    #pasarela de compras
    path('confirmacion/', SummaryView.as_view(), name='confirmation'),
    path('pagar/',DetailPaymentView.as_view(),name="pagar"),
    path('cambiar-carrito/', updateCar, name="actualizar_carrito"),

    
    path(settings.ADMIN_URL, admin.site.urls),  # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
