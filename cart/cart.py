from app_dsh.models import Product

class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get('session_key')

        if'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        self.cart = cart


    def db_add(self, product, quantity):
        product_id = str(product)
        product_quantity = str(quantity)

        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = int[product_quantity]

        self.session.modified = True

    def cart_total_products(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        total = 0

        for key, value in quantities.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total = total +(product.sale_price * value)
                    else:
                        total = total  + (product.price * value)


        return total

    def __len__(self):
        return len(self.cart)

    def add_product(self, product,quantity):
        product_id = str(product.id)
        product_quantity = str(quantity)
        if product_id in self.cart:
            pass
        else:
            self.cart[product_id] = int(product_quantity)

        self.session.modified = True

    def get_products(self):
        product_ids =self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        return products

    def get_quantities(self):
        product_quantities = self.cart
        return product_quantities

    def update_cart(self, product, quantities):
        product_id = str(product)
        product_quantities = int(quantities)

        current_cart = self.cart
        current_cart[product_id] = product_quantities
        self.session.modified = True

        cart = self.cart
        return cart

    def delete_from_cart(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

