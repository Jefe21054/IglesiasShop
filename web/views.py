from django.shortcuts import render,get_object_or_404,redirect
from .models import Categoria,Producto
from .carrito import Cart

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

    print(request.session.get('cart'))

    return render(request,'carrito.html')

def eliminarProductoCarrito(request,producto_id):
    pass

def limpiarCarrito(request):
    pass

def registrarPedido(request):
    pass

def confirmarPedido(request):
    pass

def gracias(request):
    pass

def crearUsuario(request):
    pass

def cuentaUsuario(request):
    pass

def actualizarCliente(request):
    pass

def loginUsuario(request):
    pass

def logoutUsuario(request):
    pass
