class Cart:

    def __init__(self,request):
        self.request = request
        self.session = request.session

        cart = self.session.get('cart')
        montoTotal = self.session.get('cartMontoTotal')
        cantidadTotal = self.session.get('cartCantidadTotal')
        if not cart:
            cart = self.session['cart'] = {}
            montoTotal = self.session['cartMontoTotal'] = '0'
            cantidadTotal = self.session['cartCantidadTotal'] = '0'

        self.cart = cart
        self.montoTotal = float(montoTotal)
        self.cantidadTotal = int(cantidadTotal)
    
    def add(self,producto,cantidad):
        
        if str(producto.id) not in self.cart.keys():
            self.cart[producto.id] = {
                'producto_id':producto.id,
                'nombre':producto.nombre,
                'cantidad':cantidad,
                'precio':str(producto.precio),
                'imagen':producto.imagen.url,
                'categoria':producto.categoria.nombre,
                'subtotal':str(cantidad*producto.precio),
            }
        else:
            #Actualizacion del producto en Carrito
            for key,value in self.cart.items():
                if key == str(producto.id):
                   value['cantidad'] = str(int(value['cantidad']) + cantidad)
                   res = float(value['cantidad']) * float(value['precio'])
                   value['subtotal'] = "{:.2f}".format(res)
                   break

        self.save()

    def delete(self,producto):
        producto_id = str(producto.id)
        
        if producto_id in self.cart:
            del self.cart[producto_id]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.session['cartMontoTotal'] = '0'
        self.session['cartCantidadTotal'] = '0'

    def save(self):
        ''' GUARDA CAMBIOS EN CARRITO '''
        montoTotal = 0
        cantidadTotal = 0

        for key,value in self.cart.items():
            montoTotal += float(value['subtotal'])
            cantidadTotal += int(value['cantidad'])
        
        self.session['cartMontoTotal'] = "{:.2f}".format(montoTotal)
        self.session['cartCantidadTotal'] = str(cantidadTotal)
        self.session['cart'] = self.cart
        self.session.modified = True
