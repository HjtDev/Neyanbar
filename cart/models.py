from shop.models import Product, Volume


class Cart:
    def __init__(self, request):
        self.session = request.session

        if not self.session.get('cart'):
            self.cart = self.session['cart'] = {}
        else:
            self.cart = self.session['cart']

    def save(self):
        self.session.modified = True

    def clear(self):
        self.cart.clear()
        self.save()

    def add(self, pid: str, volume: int, quantity: int, max_quantity: int):
        try:
            if Product.objects.get(id=int(pid)) and Volume.objects.get(volume=volume):
                if self.cart.get(pid, None):
                    if sum(quantity for quantity in self.cart[pid]['volume'].values()) + quantity > max_quantity:
                        return False
                    if str(volume) in self.cart[pid]['volume']:
                        self.cart[pid]['volume'][str(volume)] += quantity
                    else:
                        self.cart[pid]['volume'].update({volume: quantity})
                else:
                    self.cart[pid] = {'volume': {volume: quantity}}
                return True
        except Product.DoesNotExist as e:
            print('error:', e)
        finally:
            self.save()

    def delete(self, pid: str, volume: str):
        try:
            del self.cart[pid]['volume'][volume]
        except KeyError as k:
            print(k)
        finally:
            self.save()

    def get_total_cost(self):
            total = 0
            for pid, options in self.cart.items():
                try:
                    product = Product.objects.get(id=int(pid))
                    if Volume.objects.filter(volume__in=options['volume'].keys()).exists():
                        for volume, quantity in options['volume'].items():
                            total += product.get_volume_price(int(volume)) * int(quantity)
                except (Product.DoesNotExist, Volume.DoesNotExist):
                    self.delete(pid)
            return total


    def __len__(self):
        return sum(len(options.get('volume')) for options in self.cart.values())

    def __iter__(self):
        for pid, options in self.cart.items():
            try:
                product = Product.objects.get(id=pid)
                for volume, quantity in options['volume'].items():
                    yield {
                        'product': product,
                        'volume': volume,
                        'quantity': quantity,
                        'cost': product.get_volume_price(int(volume)) * int(quantity)
                    }
            except (Product.DoesNotExist, Volume.DoesNotExist):
                self.delete(pid)
