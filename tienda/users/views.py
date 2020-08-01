from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView, CreateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from tienda.users.forms import FormularioRegistro 

from django.db.models import Q, Max, Min



from tienda.productos.models import Producto, Comentario, CarritoCompras

User = get_user_model()


class Indice(TemplateView):
    template_name = 'index.html'

class ListadoProducto(ListView):
    template_name = 'listado_productos.html'
    model = Producto
    paginate_by = 10

    def get_queryset(self):
        query = None

        if ('nombre' in self.request.GET) and self.request.GET['nombre'] != "":
            query = Q(nombre=self.request.GET["nombre"])

        if ('maximo' in self.request.GET) and self.request.GET['maximo'] != "":
            try:
                if query == None:
                    query = Q(precio__lte=int(float(self.request.GET['maximo'])))
                else:
                    query = query & Q(precio__lte=int(float(self.request.GET['maximo'])))
            except:
                pass


        if ('minimo' in self.request.GET) and self.request.GET['minimo'] != "":
            try:
                if query == None:
                    query = Q(precio__gte=int(float(self.request.GET['minimo'])))
                else:
                    query = query & Q(precio__gte=int(float(self.request.GET['minimo'])))
            except:
                pass


        if query is not None:
            productos = Producto.objects.filter(query)
        else:
            productos = Producto.objects.all()
        return productos
    
    def get_context_data(self, **kwargs):
        context = super(ListadoProducto, self).get_context_data(**kwargs)
        context['maximo'] = Producto.objects.all().aggregate(Max('precio'))['precio__max']
        context['minimo'] = Producto.objects.all().aggregate(Min('precio'))['precio__min']
        return context


class DetalleProducto(DetailView):
    template_name = 'detalle.html'
    model = Producto

class ComentarioProducto(CreateView):
    template_name = 'detalle.html'
    model = Comentario
    fields = ('comentario','usuario','producto',)

    def get_success_url(self):
        return "/detalle_producto/{}/".format(self.object.producto.pk)

class Salir(LogoutView):
	next_page = reverse_lazy('indice')

class Ingresar(LoginView):
	template_name = 'login.html'

	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			return HttpResponseRedirect(reverse('indice'))
		else:
			context = self.get_context_data(**kwargs)
			return self.render_to_response(context)

	def get_success_url(self):
		return reverse('indice')

class RegistroUsuarios(CreateView):
    model = User
    template_name = 'registrar.html'
    form_class = FormularioRegistro
    success_url = reverse_lazy('ingresar')

class CambiarPerfil(LoginRequiredMixin, UpdateView):
    model = User
    fields = ('telefono','last_name','first_name','email',)
    success_url = '/'
    template_name = 'perfil.html'

    def get_object(self, queryset=None):
        return self.request.user


class AniadirCarrito(LoginRequiredMixin, CreateView):
    model = CarritoCompras
    fields = ('usuario','producto','precio',)
    success_url = reverse_lazy('listar_carrito')
    login_url = 'ingresar'


class EliminarCarrito(LoginRequiredMixin,DeleteView):
    queryset = CarritoCompras.objects.filter(comprado=False)
    model = CarritoCompras
    success_url = reverse_lazy('listar_carrito')
    login_url = 'ingresar'

class ListarCarrito(LoginRequiredMixin,ListView):
    template_name = 'carrito.html'
    model = CarritoCompras
    queryset = CarritoCompras.objects.filter(comprado=False,pendiente=False)
    login_url = 'ingresar'

    def get_context_data(self, **kwargs):
        context = super(ListarCarrito, self).get_context_data(**kwargs)
        context['tab'] = 'sincomprar'
        return context

class ListarCarritoPendientes(LoginRequiredMixin,ListView):
    template_name = 'carrito.html'
    model = CarritoCompras
    queryset = CarritoCompras.objects.filter(comprado=False,pendiente=True)
    login_url = 'ingresar'

    def get_context_data(self, **kwargs):
        context = super(ListarCarritoPendientes, self).get_context_data(**kwargs)
        context['tab'] = 'pendientes'
        return context

class ListarCarritoFinalizadas(LoginRequiredMixin,ListView):
    template_name = 'carrito.html'
    model = CarritoCompras
    queryset = CarritoCompras.objects.filter(comprado=True,pendiente=False)
    login_url = 'ingresar'

    def get_context_data(self, **kwargs):
        context = super(ListarCarritoFinalizadas, self).get_context_data(**kwargs)
        context['tab'] = 'finalizadas'
        return context


########## pasarela de pagos #####################
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import hashlib
import requests
import json

#esta clase contiene los datos de la tienda
class paymentDetail():
    merchantId = 508029 #id de payu
    accountId = 512326
    apiKey = '4Vj8eK4rloUd272L48hsrarnUA' 
    description = "Test PAYU"
    test = 1 #1 si es test o 0 si no 
    url = "https://sandbox.checkout.payulatam.com/ppp-web-gateway-payu" #url a de pago payu

#post de pago para ver la confirmación
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
        #cuando responde payu que fue o no fue exitoso el pago a fin detalle compra
        value_str = str(value)

        value_antes, value_despues = value_str.split(".")
        value_despues= list(value_despues)
        if value_despues[1] == '0':
            value= round(float(value),1)
        signature          = hashlib.md5('{}~{}~{}~{}~{}~{}'.format(paymentDetail().apiKey, merchand_id,reference_sale, value, currency,state_pol).encode('utf-8')).hexdigest()

        if signature == request.POST["sign"]: #los no comprados loc obramos
            carritoModels = CarritoCompras.objects.filter(identificador=reference_sale,comprado=False)
            if state_pol == '4': #aprobado lo ponemos como comprado
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

        return HttpResponse(status=200) #le devolvemos ewl 200 que todo estuvo bien


#vista para pagar, que renderiza el template de pago
class DetailPaymentView(TemplateView):
    template_name = 'detalle_compra.html'
    #datos del pago y toda la info que requiere payu para el pago o cobro
    def get_context_data(self, **kwargs):
        payment = paymentDetail()
        description  = payment.description
        merchantId  = payment.merchantId
        accountId  = payment.accountId
        context = super(DetailPaymentView, self).get_context_data(**kwargs)#el super de la clase
        referenceCode = ""
        amount = 0
        currency = 'COP'#moneda a cobrar

        context["merchant_id"] = merchantId
        context["account_id"] = accountId
        context["description"] = description
        context["reference_code"] = referenceCode
        context["amount"] = amount #cobro
        context["tax"] = 0 #iva
        context["taxReturn_base"] = 0 #iva
        context["currency"] = currency #moneda a cobrar
        context["signature"] = "ba9ffa71559580175585e45ce70b6c37" #firma
        context["test"] = payment.test #si estamos en test
        context["buyer_email"] = self.request.user.email#email user
        context["response_url"] = 'https://5beb0989e52a.ngrok.io/pagar/' #url puede ser ngrok
        context["confirmation_url"] = 'https://5beb0989e52a.ngrok.io/confirmacion/'
        context["url"] = payment.url
        return context

#función que actualiza el carro 
def updateCar(request):
    payment = paymentDetail()
    merchantId  = payment.merchantId
    apiKey = payment.apiKey
    #indentificadores de compra
    maximo_identificador = CarritoCompras.objects.all().order_by('-identificador')[1].identificador
    if maximo_identificador is None:
        maximo_identificador = 0
    maximo_identificador =  maximo_identificador + 1
    currency = 'COP'
    #todo lo que tiene nu comprado ni pendiente
    carritos = request.user.carrito_usuario.all().filter(comprado = False, pendiente = False)
    #vamos sumando cada producto en carrito
    amount = 0
    for carrito in carritos:
        carrito.pendiente = True #le decimos que ahora esta
        carrito.identificador = maximo_identificador
        carrito.direccion = request.POST["direction"]#entregamos la dirreción 
        carrito.save()
        amount = amount + carrito.precio
        #firma propia para que payU nos reconozaca
    signature = hashlib.md5("{}~{}~{}~{}~{}".format(apiKey,merchantId,maximo_identificador,amount,currency).encode('utf-8') ).hexdigest()
    #respondemos a productos pendientes esperando que payu responda
    response = HttpResponse(json.dumps({"precio":amount,"identifier":maximo_identificador,"signature":signature}), content_type="application/json", status=200)
    return response
