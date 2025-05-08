from .models import Cart


def cart(request):
    if not request.path.startswith('/admin'):
        return {'cart': Cart(request)}
    return {}
