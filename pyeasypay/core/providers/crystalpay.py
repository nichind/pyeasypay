from AaioAPI import AsyncAaioAPI
from hashlib import sha256
from uuid import uuid4
from asyncio import wait_for


class Invoice:
    def __init__(self, provider, invoice, amount):
        self.creds = provider
        self.invoice = invoice
        self.amount = amount

        if 'login' not in self.creds.__dict__.keys():
            raise ValueError(f'login is required for {self.creds.name} provider')

        if 'secret' not in self.creds.__dict__.keys():
            raise ValueError(f'secret is required for {self.creds.name} provider')

    async def create(self):
        pass

    async def check(self):
        pass
