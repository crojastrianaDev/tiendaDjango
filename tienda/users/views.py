from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, RedirectView, UpdateView, TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from tienda.users.forms import FormularioRegistro 
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
# se importan los modulos de consulta django
from django.db.models import Q, Max, Min
from tienda.productos.models import Producto, Comentario, Carrito

User = get_user_model()


#creamos el view PRINCIPAL

class Indice(TemplateView):
    template_name = 'index.html'

#CLASE PARA LISTAR LOS PRODUCTOS
class ListadoProductos(ListView):
    #template render
    print("Pase a listado productos")
    template_name = 'listado_productos.html'
    #el modelo
    model = Producto
    #cada cuanto se pagina los productos
    paginate_by = 4
    #obtiene todos los objetos en esa base de datos que pertenezcan a ese modelo.
    def get_queryset(self):
        query = None #si viene algun nombre filtrando con el nombre
        #atravez del reques traemos cada dato con get
        if('nombre' in self.request.GET) and self.request.GET['nombre'] != "":
            #query ahora es igual a q. y respondemos el objeto de ese nombre
            query = Q(nombre=self.request.GET["nombre"])
        #ahora consultamos con los precios
        if ('maximo' in self.request.GET) and self.request.GET['maximo'] !="":
            try:
                if query == None: #si viene sin nombre lo hacemos con el maximo
                    #lo que hacemos es sacar el número y buscar lo que sea menor o igual a ese número
                    query = Q(precio__lte=int(float(self.request.GET['maximo'])))
                else:
                    query = query & Q(precio__lte=int(float(self.request.GET['maximo'])))
            except:  #si insertan letras no ocurre nada  
              pass
        if ('minimo' in self.request.GET) and self.request.GET['minimo'] !="":
            try:
                if query == None: #si viene sin nombre lo hacemos con el maximo
                    #lo que hacemos es sacar el número y buscar lo que sea mayor o igual a ese número
                    query = Q(precio__gte=int(float(self.request.GET['minimo'])))
                else:
                    query = query & Q(precio__gte=int(float(self.request.GET['minimo'])))
            except:  #si insertan letras no ocurre nada  
              pass
        # finalmente preguntamos que si query es no none  -- traemos los productos
        if query is not None:
            productos = Producto.objects.filter(query)
        else: #agarra todos los productos si no los filtra los entrega todos
            productos = Producto.objects.all()
        return productos

    #con este enviamos info que se requiera.
    def get_context_data(self, **kwargs):
        #enviamos a listado producto traeme lo que tiene listview
        context = super(ListadoProductos, self).get_context_data(**kwargs)
        #agreamos los campos de minimo y maximo y entregara esto el producto con menor o maximo
        context['maximo'] = Producto.objects.all().aggregate(Max('precio'))['precio__max']
        context['minimo'] = Producto.objects.all().aggregate(Min('precio'))['precio__min']
        print(context)
        return context

class DetalleProducto(DetailView):
    template_name = 'detalle.html'
    model = Producto    

class ComentarioProducto(CreateView):
    template_name = 'detalle.html'
    model = Comentario
    #los datos del comentario sin el fecha que es automatica
    fields = ('comentario','usuario','productofk',)
# nos redirecciona el mensaje a el producto con su llave 
    def get_success_url(self):  
        #devolvemos a detalle producto con la pk del producto para recargar con mensajes
        return "/detalleProducto/{}/".format(self.object.productofk.pk)

class Salir(LogoutView):
    #me envia redireccionado a la inicial
   
    next_page = reverse_lazy('indice')

class Ingresar(LoginView):
    #llamaos login
    template_name = 'login.html'

    def get(self, reques, *args, **kwargs):
        #este metodo si ya nos autenticamos y quiero entrar de nuevo me manda a indice
        #si no, me loguea
        if reques.user.is_authenticated:
            return HttpResponseRedirect(reverse('indice'))
        else:
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)

    def get_success_url(self):
        #si me logueo bien me manda a donde?
        return reverse('indice') 

class RegistroUsuarios(CreateView):
    model = User
    template_name = 'registrar.html'
    form_class = FormularioRegistro
    success_url = reverse_lazy('ingresar')


# cambio de perfil, solo si es logueado
class ModificarPerfil(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('telefono','last_name','first_name','email')
    success_url = '/'
    template_name = 'perfil.html'

    #usamos getobject para obtener el ibjeto a modificar
    def get_object(self, queryser=None):
        #esta función nis toma el obhjeto logeado.
        return self.request.user

class AgregarCarrito(LoginRequiredMixin, CreateView):
    #con esto añadimos al carrito
    #llamamos el modelo carrito, los datos a llenar 
    model = Carrito
    fields = ('usuario','producto','precio',)
    #si todo va bien vamos a 
    success_url = reverse_lazy('listadoProductos')
    #si no estamos logueados logear
    login_url = 'ingresar'

class EliminarCarrito(LoginRequiredMixin, DeleteView):
    #con el podemos borrar el carrito cuando comprado es falso
    queryset = Carrito.objects.filter(comprado=False)
    model = Carrito
    #si lo borra vamos a prodcutos
    success_url = reverse_lazy('listadoProductos')
    #si no estamos logueados que se loguie
    login_url = 'ingresar'

class ListarCarrito(LoginRequiredMixin, ListView):
    template_name = 'carrito.html'
    model = Carrito
    #si es no esta comprado y no esta pendiente
    queryset = Carrito.objects.filter(comprado=False, pendiente=False)
    login_url = 'ingresar'

    def get_context_data(self, **kwargs):
        #sobre cargamos carro de pendientes
        context = super(ListarCarrito, self).get_context_data(**kwargs)
        # con el tab sin compra para que el template lo entienda
        context["tab"] = 'sincomprar'
        return context

class ListarCarritoPendiente(LoginRequiredMixin, ListView):
    template_name = 'carrito.html'
    model = Carrito
    #si es pendiente y falsa de comprar lo mostramos en pendiente
    queryset = Carrito.objects.filter(comprado=False, pendiente=True)
    login_url = 'ingresar'

    def get_context_data(self, **kwargs):
        #sobre cargamos carro de pendientes
        context = super(ListarCarritoPendiente, self).get_context_data(**kwargs)
        # con el tab pendiente que el template lo entienda
        context["tab"] = 'pendientes'
        return context

class ListarCarritoFinalizado(LoginRequiredMixin, ListView):
    template_name = 'carrito.html'
    model = Carrito
    #cuando ya esta pago
    queryset = Carrito.objects.filter(comprado=True, pendiente=False)
    login_url = 'ingresar'

    def get_context_data(self, **kwargs):
        #sobre cargamos carro de pendientes
        context = super(ListarCarritoFinalizado, self).get_context_data(**kwargs)
        # con el tab finalizado para que el template lo entienda
        context["tab"] = 'finalizadas'
        return context
    

########## pasarela de pagos #####################
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import hashlib
import requests
import json


class paymentDetail():
    merchantId = 508029
    accountId = 512321
    apiKey = '4Vj8eK4rloUd272L48hsrarnUA'
    description = "compra realizada desde mi sitio"
    test = 1
    url = "https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu"

@method_decorator(csrf_exempt, name='dispatch')
class SummaryView(TemplateView):
    template_name = 'fin_detalle_compra.html'

    def post(self, request, *args, **kwargs):
        merchand_id          = request.POST['merchant_id']
        reference_sale       = request.POST['reference_sale']
        state_pol            = request.POST['state_pol']
        value                = request.POST['value']
        currency             = request.POST['currency']
        sign                 = request.POST['sign']

        value_str = str(value)

        value_antes, value_despues = value_str.split(".")
        value_despues= list(value_despues)
        if value_despues[1] == '0':
            value= round(float(value),1)
        signature          = hashlib.md5('{}~{}~{}~{}~{}~{}'.format(paymentDetail().apiKey, merchand_id,reference_sale, value, currency,state_pol).encode('utf-8')).hexdigest()

        if signature == request.POST["sign"]:
            carritoModels = CarritoCompras.objects.filter(identificador=reference_sale,comprado=False)
            if state_pol == '4':
                for carrito in carritoModels:
                    carrito.comprado = True
                    carrito.pendiente = False
                    carrito.datos_payu = "{}".format(request.POST)
                    carrito.save()

                if len(carritoModels) != 0:
                    print("compra realizada exitosamente")

            # 104 error 
            # 5 expirada
            # 6 declinada
            elif state_pol == '104' or state_pol == '5' or state_pol == '6':
                carritoModels.delete()
        else:
            print("el signature no coincide")

        return HttpResponse(status=200)



class DetailPaymentView(TemplateView):
    template_name = 'detalle_compra.html'

    def get_context_data(self, **kwargs):
        payment = paymentDetail()
        description  = payment.description
        merchantId  = payment.merchantId
        accountId  = payment.accountId
        context = super(DetailPaymentView, self).get_context_data(**kwargs)
        referenceCode = ""
        amount = 0
        currency = 'COP'

        context["merchant_id"] = merchantId
        context["account_id"] = accountId
        context["description"] = description
        context["reference_code"] = referenceCode
        context["amount"] = amount
        context["tax"] = 0
        context["taxReturn_base"] = 0
        context["currency"] = currency
        context["signature"] = ""
        context["test"] = payment.test
        context["buyer_email"] = self.request.user.email
        context["response_url"] = 'https://c79ed2a8.ngrok.io/pagar/'
        context["confirmation_url"] = 'https://c79ed2a8.ngrok.io/confirmacion/'
        context["url"] = payment.url
        return context


def updateCar(request):
    payment = paymentDetail()
    merchantId  = payment.merchantId
    apiKey = payment.apiKey

    maximo_identificador = CarritoCompras.objects.all().order_by('-identificador')[0].identificador
    if maximo_identificador is None:
        maximo_identificador = 0
    maximo_identificador =  maximo_identificador + 1
    currency = 'COP'
    
    carritos = request.user.carrito_usuario.all().filter(comprado = False, pendiente = False)

    amount = 0
    for carrito in carritos:
        carrito.pendiente = True
        carrito.identificador = maximo_identificador
        carrito.direccion = request.POST["direction"]
        carrito.save()
        amount = amount + carrito.precio
    signature = hashlib.md5("{}~{}~{}~{}~{}".format(apiKey,merchantId,maximo_identificador,amount,currency).encode('utf-8') ).hexdigest()

    response = HttpResponse(json.dumps({"precio":amount,"identifier":maximo_identificador,"signature":signature}), content_type="application/json", status=200)
    return response
