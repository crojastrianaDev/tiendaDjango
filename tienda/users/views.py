from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView, CreateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse


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
    success_url = reverse_lazy('indice')
    login_url = 'ingresar'


class EliminarCarrito(LoginRequiredMixin,DeleteView):
    queryset = CarritoCompras.objects.filter(comprado=False)
    model = CarritoCompras
    success_url = reverse_lazy('indice')
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
