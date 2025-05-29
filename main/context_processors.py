from shop.models import Brand, ProductSmell
from .models import Setting

def base(request):
    return {
        'all_brands': Brand.objects.all(),
        'all_smells': ProductSmell.objects.all(),
        'footer_text': Setting.objects.first().footer_text
    }