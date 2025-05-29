from shop.models import Product, Volume


class Cart:
    def __init__(self, request):
        self.session = request.session

        if not self.session.get('cart'):
            self.cart = self.session['cart'] = {}
        else:
            self.cart = self.session['cart']

        mark_to_delete = []
        for pid, volumes in self.cart.items():
            try:
                if sum(quantity for quantity in volumes['volume'].values()) > Product.objects.get(id=pid).inventory:
                    mark_to_delete.append(pid)
            except Product.DoesNotExist:
                mark_to_delete.append(pid)
        if mark_to_delete:
            [self.cart.pop(p) for p in mark_to_delete]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.cart.clear()
        self.save()

    def add(self, pid: str, volume: int, quantity: int, max_quantity: int):
        if not quantity or not max_quantity:
            return False
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
                self.save()
                return True
        except Product.DoesNotExist as e:
            print('error:', e)
        return False

    def update(self, pid: str, volume: int, quantity: int, max_quantity: int):
        if not quantity or not max_quantity:
            self.delete(pid)
            return False
        try:
            if Volume.objects.get(volume=volume):
                self.cart[pid]['volume'][str(volume)] = quantity
                return True
        except (Product.DoesNotExist, Volume.DoesNotExist):
            self.delete(pid)
        return False

    def delete(self, pid: str, volume: str = None):
        try:
            if volume:
                del self.cart[pid]['volume'][volume]
            else:
                del self.cart[pid]
        except KeyError as k:
            print(k)
        finally:
            self.save()

    def get_total_cost(self):
        total = 0
        mark_to_delete = []
        for pid, options in self.cart.items():
            try:
                product = Product.objects.get(id=int(pid))
                if Volume.objects.filter(volume__in=options['volume'].keys()).exists():
                    for volume, quantity in options['volume'].items():
                        total += product.get_volume_price(int(volume)) * int(quantity)
            except (Product.DoesNotExist, Volume.DoesNotExist):
                mark_to_delete.append(pid)
        if mark_to_delete:
            [self.cart.pop(p) for p in mark_to_delete]
            self.save()
        return total

    def __len__(self):
        return sum(len(options.get('volume')) for options in self.cart.values())

    def __iter__(self):
        mark_to_delete = []
        for pid, options in self.cart.items():
            try:
                product = Product.objects.get(id=pid)
                for volume, quantity in options['volume'].items():
                    yield {
                        'product': product,
                        'volume': volume,
                        'volume_name': Volume.objects.get(volume=int(volume)).get_name(),
                        'quantity': quantity,
                        'base_price': product.get_volume_price(int(volume)),
                        'cost': product.get_volume_price(int(volume)) * int(quantity)
                    }
            except (Product.DoesNotExist, Volume.DoesNotExist, RuntimeError):
                mark_to_delete.append(pid)
        [self.cart.pop(pid) for pid in mark_to_delete]
