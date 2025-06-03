from .post import Postex
from django.conf import settings


postex = Postex(settings.POSTEX_CONFIG['api_key'])
