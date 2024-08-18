from aiocryptopay import AioCryptoPay, Networks


class Invoice:
    def __init__(self, provider, invoice, amount):
        self.creds = provider
        self.invoice = invoice
        self.amount = amount

        if 'api_key' not in self.creds.__dict__.keys():
            raise ValueError(f'api_key is required for {self.creds.name} provider')

        self.crypto = AioCryptoPay(token=self.creds.api_key,
                                   network=(Networks.MAIN_NET if self.creds.network == 'main' else Networks.TEST_NET)
                                   if self.creds.network else Networks.MAIN_NET)

    async def create(self):
        invoice = await self.crypto.create_invoice(asset=self.invoice.currency, amount=self.amount)
        self.invoice.pay_info = invoice.bot_invoice_url
        self.invoice.identifier = invoice.invoice_id
        self.invoice.status = invoice.status
        return invoice.bot_invoice_url

    async def check(self):
        invoice = await self.crypto.get_invoices(invoice_ids=self.invoice.identifier)
        if invoice.status != self.invoice.status:
            self.invoice.status = invoice.status
        if invoice.status == 'paid':
            await self.crypto.close()
        return self.invoice.status