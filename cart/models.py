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

    def add(self, pid: str, volume: int, quantity: int):
        try:
            if Product.objects.get(id=int(pid)) and Volume.objects.get(volume=volume):
                if pid in self.cart:
                    if volume in self.cart[pid]['volume']:
                        self.cart[pid]['quantity'] += quantity
                    else:
                        self.cart[pid]['quantity'] = quantity
                        self.cart[pid]['volume'].append(volume)
                else:
                    self.cart[pid] = {'volume': [volume], 'quantity': quantity}
        except Exception as e:
            print(e)
        finally:
            self.save()

    def delete(self, pid: str):
        try:
            del self.cart[pid]
        except KeyError:
            pass
        finally:
            self.save()

    def get_total_cost(self):
            total = 0
            for pid, options in self.cart.items():
                try:
                    product = Product.objects.get(id=int(pid))
                    if Volume.objects.get(volume__in=options['volume']):
                        for volume in options['volume']:
                            total += product.get_volume_price(int(volume))
                except (Product.DoesNotExist, Volume.DoesNotExist):
                    self.delete(pid)
            return total


    def __len__(self):
        return len(self.cart.keys())

    def __iter__(self):
        for pid, options in self.cart.items():
            try:
                product = Product.objects.get(id=pid)
                volume = Volume.objects.filter(volume__in=options['volume'])
                yield {
                    'product': product,
                    'volumes': ', '.join(str(v.volume) for v in volume),
                    'quantity': options['quantity'],
                    'cost': sum(product.get_volume_price(v.volume) for v in volume)
                }
            except (Product.DoesNotExist, Volume.DoesNotExist):
                self.delete(pid)
