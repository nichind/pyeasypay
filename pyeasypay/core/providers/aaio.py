from hashlib import sha256
from uuid import uuid4
import aiohttp
import hashlib
from urllib.parse import urlencode
from asyncio import wait_for
from requests.exceptions import ConnectTimeout, ReadTimeout


class AsyncAaioAPI:
    """Originally written by https://github.com/wkillus/"""
    def __init__(self, API_KEY, SECRET_KEY, MERCHANT_ID):
        """
        Creates instance of one AAIO merchant API client

        Args:
            merchant_id: Merchant ID from https://aaio.so/cabinet
            secret: 1st secret key from https://aaio.so/cabinet
            api_key: API key from https://aaio.so/cabinet/api
        """
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.MERCHANT_ID = MERCHANT_ID

    async def get_balance(self):
        """
        Creates a request for get balances of user
        See https://wiki.aaio.so/api/poluchenie-balansa

        Returns: Model from response JSON
        """

        URL = 'https://aaio.so/api/balance'

        headers = {
            'Accept': 'application/json',
            'X-Api-Key': self.API_KEY
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:

                async with session.post(URL) as response:

                    if (response.status in [200, 400, 401]):
                        try:
                            response_json = await response.json()  # Парсинг результата
                        except:
                            return 'Не удалось пропарсить ответ'

                        if (response_json['type'] == 'success'):
                            return response_json
                        else:
                            return 'Ошибка: ' + response_json['message']  # Вывод ошибки
                    else:
                        return 'Response code: ' + str(response.status)  # Вывод неизвестного кода ответа

        except ConnectTimeout:
            return 'ConnectTimeout'  # Не хватило времени на подключение к сайту

        except ReadTimeout:
            return 'ReadTimeout'  # Не хватило времени на выполнение запроса

    async def create_payment(self, order_id,
                             amount, lang='ru',
                             currency='RUB', description=None):
        """
        Creates payment URL
        See https://wiki.aaio.so/priem-platezhei/sozdanie-zakaza for more detailed information

        Args:
            amount: Payment amount
            order_id: Your order id
            description: Payment description (Optional)
            currency: Payment currency
            language: Page language (Optional)

        Returns: Payment URL

        """

        merchant_id = self.MERCHANT_ID  # merchant id
        secret = self.SECRET_KEY  # secret key №1 from shop settings

        sign = f':'.join([
            str(merchant_id),
            str(amount),
            str(currency),
            str(secret),
            str(order_id)
        ])

        params = {
            'merchant_id': merchant_id,
            'amount': amount,
            'currency': currency,
            'order_id': order_id,
            'sign': hashlib.sha256(sign.encode('utf-8')).hexdigest(),
            'desc': description,
            'lang': lang
        }

        url_aaio = "https://aaio.so/merchant/pay?" + urlencode(params)

        return url_aaio

    async def get_payment_info(self, order_id):
        """
        Creates a request for get payment information
        See https://wiki.aaio.so/api/informaciya-o-zakaze

        Args:
            order_id: Your order ID

        Returns: Model from response JSON

        """

        URL = 'https://aaio.so/api/info-pay'

        params = {
            'merchant_id': self.MERCHANT_ID,
            'order_id': order_id
        }

        headers = {
            'Accept': 'application/json',
            'X-Api-Key': self.API_KEY

        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(URL, data=params) as response:
                response_json = await response.json()

                return response_json

    async def is_expired(self, order_id):
        """Check status payment (expired)"""

        response_json = await self.get_payment_info(order_id)

        return response_json['type'] == 'success' and response_json['status'] == 'expired'

    async def is_success(self, order_id):
        """Check status payment (success)"""

        response_json = await self.get_payment_info(order_id)

        return (response_json['type'] == 'success' and response_json['status'] == 'success') or \
            (response_json['type'] == 'success' and response_json['status'] == 'hold')


class Invoice:
    def __init__(self, provider, invoice, amount):
        self.creds = provider
        self.invoice = invoice
        self.amount = amount

        if 'api_key' not in self.creds.__dict__.keys():
            raise ValueError(f'api_key is required for {self.creds.provider} provider')

        if 'secret' not in self.creds.__dict__.keys():
            raise ValueError(f'secret is required for {self.creds.provider} provider')

    def create_signature(self):
        signature_string = f"{self.creds.api_key}:{self.amount}:{self.invoice.currency}:{self.creds.secret}:{self.invoice.identifier}"
        signature = sha256(signature_string.encode('utf-8')).hexdigest()
        return signature

    async def create(self):
        client = AsyncAaioAPI(self.creds.api_key, self.creds.secret, self.creds.api_key)

        self.invoice.identifier = str(uuid4())
        lang = self.creds.language if 'language' in self.creds.__dict__.keys() else 'en'

        signature = self.create_signature()
        self.invoice.pay_info = await client.create_payment(self.invoice.identifier, self.amount, lang, self.invoice.currency, 'AAIO Payment')
        return self.invoice.pay_info

    async def check(self):
        client = AsyncAaioAPI(self.creds.api_key, self.creds.secret, self.creds.api_key)

        expired = await wait_for(client.is_expired(self.invoice.identifier), timeout=10)
        success = await wait_for(client.is_success(self.invoice.identifier), timeout=10)

        if expired:
            self.invoice.status = 'expired'
            return 'expired'
        elif success:
            self.invoice.status = 'paid'
            return 'paid'
        else:
            self.invoice.status = 'pending'
            return 'pending'
