from AaioAPI import AsyncAaioAPI
from hashlib import sha256
from uuid import uuid4
from asyncio import wait_for


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
