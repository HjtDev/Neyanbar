from json import loads

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
        self.postal_code = conf['postal_code']
        self.city_id = conf['city_id']
        self.city_name = conf['city_name']
        self.address = conf['address']
        self.send_sms = conf['sms_notification']
        self.send_email = conf['email_notification']
        self.pickup = conf['request_pickup']
        self.delivery = conf['request_delivery']
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
        return self.client.post(f'{self.url}{url}', data=data)

    def delete(self, url, data: dict):
        return self.client.delete(f'{self.url}{url}', data=data)

    def patch(self, url, data: dict):
        return self.client.patch(f'{self.url}{url}', data=data)

    def get_payment_methods(self):
        return loads(self.client.get(f'{self.url}common/payment-methods/').text)

    def get_receiving_methods(self):
        return loads(self.client.get(f'{self.url}common/shipping-methods/').text)['data']

    def get_city_codes(self):
        return loads(self.client.get(f'{self.url}locality/cities/all/').text)

    def __str__(self):
        return f'Postex:{self.username}-{self.first_name}-{self.last_name}'
