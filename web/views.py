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

def cuentaUsuario(request):
    
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
    mensaje=''

    if request.method == 'POST':
        frmCliente = ClienteForm(request.POST)
        if frmCliente.is_valid():
            dataCliente = frmCliente.cleaned_data

            #Actualizacion del Usuario
            actUsuario = User.objects.get(pk=request.user.id)
            actUsuario.first_name = dataCliente['nombre']
            actUsuario.last_name = dataCliente['apellidos']
            actUsuario.email = dataCliente['email']
            actUsuario.save()

            #Registro de Cliente
            nuevoCliente = Cliente()
            nuevoCliente.usuario = actUsuario
            nuevoCliente.cedula = dataCliente['cedula']
            nuevoCliente.direccion = dataCliente['direccion']
            nuevoCliente.telefono = dataCliente['telefono']
            nuevoCliente.sexo = dataCliente['sexo']
            nuevoCliente.fecha_nacimiento = dataCliente['fecha_nacimiento']
            nuevoCliente.save()

            mensaje = 'DATOS ACTUALIZADOS'

    context ={
        'mensaje':mensaje,
        'frmCliente':frmCliente,
    }
    
    return render(request,'cuenta.html',context)

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

            return redirect('/cuenta')

        else:
            context = {
                'mensajeError':'DATOS INCORRECTOS'
            }

    return render(request,'login.html',context)

def logoutUsuario(request):
    logout(request)
    return render(request,'login.html')

''' VISTAS PARA EL PROCESO DE COMPRA '''

@login_required(login_url='/login')
def registrarPedido(request):
    frmCliente = ClienteForm()

    context = {
        'frmCliente':frmCliente,
    }

    return render(request,'pedido.html',context)

@login_required(login_url='/login')
def confirmarPedido(request):
    pass

@login_required(login_url='/login')
def gracias(request):
    pass
