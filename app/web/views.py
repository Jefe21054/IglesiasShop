from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from .models import Categoria,Producto,Cliente,Pedido,PedidoDetalle
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from .carrito import Cart
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from .forms import ClienteForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

# Create your views here.

def index(request):
    ''' VISTA PARA EL CATALOGO DE PRODUCTOS '''

    listaCategorias = Categoria.objects.all()
    listaProductos = Producto.objects.all()

    context = {
        'categorias':listaCategorias,
        'productos':listaProductos,
    }

    return render(request,'index.html',context)

def productosPorCategoria(request,categoria_id):
    ''' VISTA PARA FILTRAR PRODUCTOS POR CATEGORIA'''
    #objCategoria = Categoria.objects.get(pk=categoria_id)
    objCategoria = get_object_or_404(Categoria,pk=categoria_id)
    listaProductos = objCategoria.producto_set.all()
    listaCategorias = Categoria.objects.all()

    context = {
        'categorias':listaCategorias,
        'productos':listaProductos,
    }

    return render(request,'index.html',context)

def productosPorNombre(request):
    ''' VISTA PARA FILTRAR PRODUCTOS POR NOMBRE '''
    llega = request.POST['nombre']
    nombre = llega.upper()
    
    listaProductos = Producto.objects.filter(nombre__contains=nombre)
    listaCategorias = Categoria.objects.all()

    context = {
        'categorias':listaCategorias,
        'productos':listaProductos,
    }

    return render(request,'index.html',context)

def productoDetalle(request,producto_id):
    ''' VISTA PARA EL DETALLE DE PRODUCTO '''

    objProducto = get_object_or_404(Producto,pk=producto_id)
    categ = objProducto.categoria
    objCategoria = get_object_or_404(Categoria,nombre=categ)

    context = {
        'producto':objProducto,
        'categ':objCategoria,
    }

    return render(request,'producto.html',context)

def categ(request,categoria_id):
    ''' VISTA PARA REDIRECCION CATEGORIAS '''

    objCategoria = get_object_or_404(Categoria,pk=categoria_id)
    
    return redirect('/productosPorCategoria/'+str(categoria_id))

''' VISTAS PARA EL CARRITO DE COMPRAS '''

def carrito(request):
    return render(request,'carrito.html')

def agregarCarrito(request,producto_id):
    if request.method == 'POST':
        cantidad = int(request.POST['cantidad'])
    else:
        cantidad = 1

    objProducto = get_object_or_404(Producto,pk=producto_id)
    carritoProducto = Cart(request)
    carritoProducto.add(objProducto, cantidad)

    #print(request.session.get('cart'))

    if request.method == 'GET':
        return redirect('/')
    
    return render(request,'carrito.html')

def eliminarProductoCarrito(request,producto_id):
    objProducto = get_object_or_404(Producto,pk=producto_id)
    carritoProducto = Cart(request)
    carritoProducto.delete(objProducto)

    return render(request,'carrito.html')

def limpiarCarrito(request):
    carritoProducto = Cart(request)
    carritoProducto.clear()

    return render(request,'carrito.html')

''' VISTAS PARA CLIENTES Y USUARIOS '''

def crearUsuario(request):
    
    if request.method == 'POST':
        dataUsuario = request.POST['nuevoUsuario']
        dataPassword = request.POST['nuevoPassword']

        nuevoUsuario = User.objects.create_user(username=dataUsuario,password=dataPassword)
        if nuevoUsuario is not None:
            login(request,nuevoUsuario)
            return redirect('/cuenta')
    
    return render(request,'login.html')

def loginUsuario(request):
    paginaDestino = request.GET.get('next',None)
    context = {
        'destino':paginaDestino,
    }

    if request.method == 'POST':
        dataUsuario = request.POST['usuario']
        dataPassword = request.POST['password']
        dataDestino = request.POST['destino']

        usuarioAuth = authenticate(request,username=dataUsuario,password=dataPassword)
        if usuarioAuth is not None:
            login(request,usuarioAuth)

            if dataDestino != 'None':
                return redirect(dataDestino)

            return redirect('/')
        else:
            context = {
                'mensajeError':'DATOS INCORRECTOS',
            }

    return render(request,'login.html',context)

def logoutUsuario(request):
    logout(request)
    return render(request,'login.html')

def cuentaUsuario(request):

    try:
        clienteEditar = Cliente.objects.get(usuario=request.user)

        dataCliente = {
            'nombre':request.user.first_name,
            'apellidos':request.user.last_name,
            'email':request.user.email,
            'direccion':clienteEditar.direccion,
            'telefono':clienteEditar.telefono,
            'cedula':clienteEditar.cedula,
            'sexo':clienteEditar.sexo,
            'fecha_nacimiento':clienteEditar.fecha_nacimiento,
        }
    except:
        dataCliente = {
            'nombre':request.user.first_name,
            'apellidos':request.user.last_name,
            'email':request.user.email,
        }
    
    frmCliente = ClienteForm(dataCliente)
    context = {
        'frmCliente':frmCliente,
    }

    return render(request,'cuenta.html',context)

def actualizarCliente(request):
    mensaje = ''

    if request.method == 'POST':
        frmCliente = ClienteForm(request.POST)
        if frmCliente.is_valid():
            dataCliente = frmCliente.cleaned_data

            #Actualizar Usuario
            actUsuario = User.objects.get(pk=request.user.id)
            actUsuario.first_name = dataCliente['nombre']
            actUsuario.last_name = dataCliente['apellidos']
            actUsuario.email = dataCliente['email']
            actUsuario.save()

            #Registrar Cliente
            nuevoCliente = Cliente()
            nuevoCliente.usuario = actUsuario
            nuevoCliente.cedula = dataCliente['cedula']
            nuevoCliente.direccion = dataCliente['direccion']
            nuevoCliente.telefono = dataCliente['telefono']
            nuevoCliente.sexo = dataCliente['sexo']
            nuevoCliente.fecha_nacimiento = dataCliente['fecha_nacimiento']
            nuevoCliente.save()

            mensaje = 'DATOS ACTUALIZADOS'

    context = {
        'mensaje':mensaje,
        'frmCliente':frmCliente,
    }

    return render(request,'cuenta.html',context)

''' VISTAS PARA EL PROCESO DE COMPRA '''

@login_required(login_url='/login')
def registrarPedido(request):
    try:
        clienteEditar = Cliente.objects.get(usuario = request.user)
        
        dataCliente = {
            'nombre':request.user.first_name,
            'apellidos':request.user.last_name,
            'email':request.user.email,
            'direccion':clienteEditar.direccion,
            'telefono':clienteEditar.telefono,
            'cedula':clienteEditar.cedula,
            'sexo':clienteEditar.sexo,
            'fecha_nacimiento':clienteEditar.fecha_nacimiento
        }
    except:
         dataCliente = {
            'nombre':request.user.first_name,
            'apellidos':request.user.last_name,
            'email':request.user.email
         }
    
    frmCliente = ClienteForm(dataCliente)
    context = {
        'frmCliente':frmCliente
    }
    
    return render(request,'pedido.html',context)

@login_required(login_url='/login')
def confirmarPedido(request):
    context = {}
    if request.method == 'POST':
        #Actualizar datos de usuario
        actUsuario = User.objects.get(pk=request.user.id)
        actUsuario.first_name = request.POST['nombre']
        actUsuario.last_name = request.POST['apellidos']
        actUsuario.save()
        #Registro o actualizacion cliente
        try:
            clientePedido = Cliente.objects.get(usuario=request.user)
            clientePedido.telefono = request.POST['telefono']
            clientePedido.direccion = request.POST['direccion']
            clientePedido.save()
        except:
            clientePedido = Cliente()
            clientePedido.usuario = actUsuario
            clientePedido.direccion = request.POST['direccion']
            clientePedido.telefono = request.POST['telefono']
            clientePedido.save()
        #Registro de nuevo pedido
        nroPedido = ''
        auxi = float(request.session.get('cartMontoTotal'))
        montoTotal = "{:.2f}".format(auxi)
        nuevoPedido = Pedido()
        nuevoPedido.cliente = clientePedido
        nuevoPedido.save()

        #Registro detalle del pedido
        carritoPedido = request.session.get('cart')
        for key,value in carritoPedido.items():
            productoPedido = get_object_or_404(Producto,pk=value['producto_id'])
            detalle = PedidoDetalle()
            detalle.pedido = nuevoPedido
            detalle.producto = productoPedido
            detalle.cantidad = int(value['cantidad'])
            auxi2 = float(value['subtotal'])
            detalle.subtotal = "{:.2f}".format(auxi2)
            detalle.save()

        #Actualizar pedido
        nroPedido = 'PED' + nuevoPedido.fecha_registro.strftime('%Y') + str(nuevoPedido.id)
        nuevoPedido.nro_pedido = nroPedido
        nuevoPedido.monto_total = montoTotal
        nuevoPedido.save()

        #Registrar variable de sesion para el pedido
        request.session['pedidoId'] = nuevoPedido.id

        #Creacion Boton Paypal
        paypal_dict = {
            "business": settings.PAYPAL_USER_EMAIL,
            "amount": montoTotal,
            "item_name": "PEDIDO CODIGO: " + nroPedido,
            "invoice": nroPedido,
            "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
            "return": request.build_absolute_uri('/gracias'),
            "cancel_return": request.build_absolute_uri('/'),
        }

        # Create the instance.
        formPaypal = PayPalPaymentsForm(initial=paypal_dict)

        context = {
            'pedido':nuevoPedido,
            'formPaypal':formPaypal,
        }

        #Limpiar carrito de compras
        carrito = Cart(request)
        carrito.clear()

    return render(request,'compra.html',context)

@login_required(login_url='/login')
def gracias(request):
    paypalId = request.GET.get('PayerID',None)
    context = {}
    if paypalId is not None:
        pedidoId = request.session.get('pedidoId')
        pedido = get_object_or_404(Pedido,pk=pedidoId)
        pedido.estado = '1'
        pedido.save()

        send_mail(
            'GRACIAS POR TU COMPRA',
            'Tu número de pedido es: ' + pedido.nro_pedido,
            settings.ADMIN_USER_EMAIL,
            [request.user.email],
            fail_silently=False,
        )

        context = {
            'pedido':pedido,
        }
    else:
        return redirect('/')
    return render(request,'gracias.html',context)
