from json import loads

from django.core.cache import cache

from .exceptions import *
from django.conf import settings
from logging import info
import requests

class Postex:
    def __init__(self, api: str):
        self.api = api
        self.url = 'https://api.postex.ir/api/v1/'

        if not self.api:
            raise ValueError('API must be provided')
        self.headers = {'x-api-key': self.api}

        self.client = requests.Session()
        self.client.headers.update(self.headers)
        response = self.get('user/whoami/')
        if response.status_code != 200:
            print(response.text)
            raise UserDoesNotExist('API key is invalid or expired')

        user_data = response.json()
        self.username = user_data['username']
        self.first_name = user_data['first_name']
        self.last_name = user_data['last_name']
        self.email = user_data['email']
        self.phone = user_data['mobile_no']
        self.national_code = user_data['national_code']
        self.is_active = user_data['is_active']
        self.is_verified = user_data['is_verified']

        if not self.is_active or not self.is_verified:
            raise UserNotActive('Your account is disabled!')

        conf = settings.POSTEX_CONFIG

        self.payment_method = conf['payment_method']
        self.courier = {
            'code': conf['courier']['courier_code'],
            'type': conf['courier']['service_type']
        }
        self.telephone = conf['TELEPHONE']
        self.postal_code = conf['postal_code']
        self.city_id = conf['city_id']
        self.city_name = conf['city_name']
        self.address = conf['address']
        self.send_sms = conf['sms_notification']
        self.send_email = conf['email_notification']
        self.pickup = conf['request_pickup']
        self.delivery = conf['request_delivery']
        self.label = conf['request_label']
        self.packaging = conf['request_packaging']
        self.print_logo = conf['print_logo']
        self.auto_accept = conf['ready_to_accept']

        valid_payment_methods = self.get_payment_methods()
        if not any(method['value'] == self.payment_method for method in valid_payment_methods):
            raise ValueError(f'Invalid payment method: {self.payment_method=}\nValid payment methods are {", ".join(valid_payment_methods)}')

        valid_couriers = self.get_receiving_methods()
        if not any(method['courierCode'] == self.courier['code'] and method['courierServiceCode'] == self.courier['type'] for method in valid_couriers):
            raise ValueError(f'Invalid courier data: {self.courier=}\nValid courier data is {", ".join(valid_couriers)}')

        print('Postex API is ready to use!')

    def get(self, url):
        return self.client.get(f'{self.url}{url}')

    def post(self, url, data: dict):
        return self.client.post(f'{self.url}{url}', json=data)

    def delete(self, url, data: dict):
        return self.client.delete(f'{self.url}{url}', json=data)

    def patch(self, url, data: dict):
        return self.client.patch(f'{self.url}{url}', json=data)

    def get_payment_methods(self):
        return loads(self.get(f'common/payment-methods/').text)

    def get_receiving_methods(self):
        return loads(self.get(f'common/shipping-methods/').text)['data']

    def get_city_codes(self):
        return loads(self.get(f'locality/cities/all/').text)

    def find_city_code(self, city_name):
        city_codes = cache.get('city_codes', {})
        if city_name in city_codes:
            return city_codes[city_name]
        for province in self.get_city_codes():
            for city in province.get('cities', []):
                if city.get('name') == city_name:
                    city_codes[city_name] = city.get('id')
                    cache.set('city_codes', city_codes)
                    return city.get('id')
        return -1  # couldn't find the city

    def submit_parcel(self, first_name, last_name, phone, email, national_code,
                      postal_code, country, city_name, address,
                      parcel_items: list, length, width, height, total_weight,
                      is_fragile, is_liquid, total_price, box_type_id,
                      description, order_id, pickup_date_time=None, pickup_on_utc=None, delivery_date_time=None):
        data = {
            'from': {
                'contact': {
                    'first_name': self.first_name,
                    'last_name': self.last_name,
                    'email_address': self.email,
                    'mobile_no': self.phone,
                    'telephone_no': self.telephone,
                    'national_code': self.national_code,
                },
                'location': {
                    'post_code': self.postal_code,
                    'country': country,
                    'city_id': self.city_id,
                    'city_name': self.city_name,
                    'address': self.address,
                    'lat': None,
                    'lon': None,
                }
            },
            'to': {
                'contact': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'mobile_no': phone,
                    'telephone_no': phone,
                    'email_address': email,
                    'national_code': national_code,
                },
                'location': {
                    'post_code': postal_code,
                    'city_id': self.find_city_code(city_name),
                    'city_name': city_name,
                    'country': country,
                    'address': address,
                    'lat': None,
                    'lon': None,
                }
            },
            'parcel_items': parcel_items,
            'additional_data': {},
            'parcel_properties': {
                'length': length,
                'width': width,
                'height': height,
                'total_weight': total_weight,
                'is_fragile': is_fragile,
                'is_liquid': is_liquid,
                'total_value': total_price,
                'pre_paid_amount': total_price,
                'total_value_currency': 'IRR',
                'box_type_id': box_type_id,
            },
            'courier': {
                'name': self.courier['code'],
                'service_type': self.courier['type'],
                'payment_type': self.payment_method
            },
            'added_service': {
                "handling_fee": 0,
                'request_sms_notification': self.send_sms,
                'request_email_notification': self.send_email,
                "request_label": self.label,
                "request_packaging": self.packaging,
                "print_logo": self.print_logo
            },
            'delivery_instructions': None,
            'custom_order_no': str(order_id),
            'custom_reference_no': str(order_id),
            'remarks': description,
            'submit_channel': '',
            'request_pickup': {
                'request': self.pickup,
                'pickup_date_time': pickup_date_time,
                'pickup_on_utc': pickup_on_utc,
            },
            'request_delivery': {
                'request': self.delivery,
                'pickup_date_time': delivery_date_time,
            },
            "from_address_book_id": None,
            "to_address_book_id": None,
            "drop_off_location": None,
            "consolidated_parcels": [
                0
            ],
            'ready_to_accept': self.auto_accept,
        }
        response = self.post('parcels/', data=data)
        print(f'{response.status_code=}\n{response.text=}')

    def __str__(self):
        return f'Postex:{self.username}-{self.first_name}-{self.last_name}'
