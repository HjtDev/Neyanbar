from shop.models import Brand, ProductSmell

def navigation(request):
    return {'all_brands': Brand.objects.all(), 'all_smells': ProductSmell.objects.all()}