from dotenv import load_dotenv
from os import environ
from os.path import dirname, basename, isfile, join
import glob
from threading import Thread
from asyncio import run, sleep
import asyncio
from .methods import *


class EasyPay:
    """
    Create an instance of EasyPay
    """
    def __init__(self, **kwargs):
        load_dotenv()
        for name, value in environ.items():
            if name.upper() in ['API_KEY', 'PROVIDER', 'NETWORK', 'LOGIN', 'PASSWORD', 'SECRET_KEY']:
                setattr(self, name.lower(), value)
        for k, v in kwargs.items():
            setattr(self, k, v)
        if 'provider' not in self.__dict__:
            raise ValueError('Provider is required')

    async def create_invoice(self, amount: int, currency: str = 'USD'):
        invoice = Invoice(self, amount, currency)
        await invoice.create()
        return invoice

    def __repr__(self):
        return f'EasyPay({self.__dict__})'


class Invoice:
    """
    Invoice class, use it to create an invoice
    Args:
        amount: int
    Attributes:
        amount: int
        status: str
        identifier: str
    """
    def __init__(self, creds: EasyPay, amount: int | float, currency: str = 'USDT'):
        self.creds = creds
        self.currency = currency
        self.amount = amount
        self.status = 'creating'
        self.identifier = None
        self.pay_info = None
        self.invoice = None

    async def create(self, run_check: bool = False):
        print(f'Creating invoice for {self.amount} {self.currency} using {self.creds.provider} provider...')
        modules = glob.glob(join(dirname(__file__) + '\\methods', "*.py"))
        __all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

        if self.creds.provider not in __all__:
            raise ValueError('Provider is not supported')

        provider = __import__(f'pyeasypay.core.methods.{self.creds.provider}', globals(), locals(), ['Invoice'], 0)
        self.invoice = provider.Invoice(self.creds, self, self.amount)
        await self.invoice.create()

        if run_check:
            print('[run_check] Not implemented yet')

    async def check(self):
        if self.invoice is None:
            return ValueError('Invoice needs to be created first')
        return await self.invoice.check()

    def __repr__(self):
        return f'Invoice({self.__dict__})'
