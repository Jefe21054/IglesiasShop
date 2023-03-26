from django.shortcuts import render
from .models import Categoria,Producto

# Create your views here.
''' VISTA PARA EL CATALOGO DE PRODUCTOS '''

def index(request):
    listaCategorias = Categoria.objects.all()
    listaProductos = Producto.objects.all()

    context = {
        'categorias':listaCategorias,
        'productos':listaProductos,
    }

    return render(request,'index.html',context)

def productosPorCategoria(request,categoria_id):
    ''' VISTA PARA FILTRAR PRODUCTOS POR CATEGORIA'''
    objCategoria = Categoria.objects.get(pk=categoria_id)
    listaProductos = objCategoria.producto_set.all()
    listaCategorias = Categoria.objects.all()

    context = {
        'categorias':listaCategorias,
        'productos':listaProductos,
    }

    return render(request,'index.html',context)
