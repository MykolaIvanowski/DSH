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

    def get_total_quantity(self):
        return sum(self.cart.values())

    def cart_total_products(self):
        product_ids = [int(pid) for pid in self.cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {product.id: product for product in products}

        total = 0
        for pid, quantity in self.cart.items():
            pid = int(pid)
            product = product_map.get(pid)
            if product:
                price = product.sale_price if product.is_sale else product.price
                total += price * quantity

        return round(total, 2)

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

