from aiocryptopay import AioCryptoPay, Networks


class Invoice:
    def __init__(self, creds, invoice, amount):
        self.creds = creds
        self.invoice = invoice
        self.amount = amount

        if 'api_key' not in creds.__dict__.keys():
            raise ValueError('api_key is required')

        self.crypto = AioCryptoPay(token=creds.api_key,
                                   network=(Networks.MAIN_NET if creds.network == 'main' else Networks.TEST_NET)
                                   if creds.network else Networks.MAIN_NET)

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
