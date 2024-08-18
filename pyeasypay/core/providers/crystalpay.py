from requests import post


class Invoice:
    def __init__(self, provider, invoice, amount):
        self.creds = provider
        self.invoice = invoice
        self.amount = amount

        if 'login' not in self.creds.__dict__.keys():
            raise ValueError(f'login is required for {self.creds.name} provider')

        if 'secret' not in self.creds.__dict__.keys():
            raise ValueError(f'secret is required for {self.creds.name} provider')

        if self.invoice.currency != 'RUB':
            raise ValueError(f'Only RUB currency is supported for {self.creds.name} provider')

    async def create(self):
        url = "https://api.crystalpay.io/v2/invoice/create/"
        payload = {
            "auth_login": self.creds.login,
            "auth_secret": self.creds.secret,
            "amount": self.amount,
            "type": 'purchase',
            "description": 'CrystalPay payment',
            "redirect_url": self.creds.redirect_url if 'redirect_url' in self.creds.__dict__.keys() else "https://nichind.dev",
            "callback_url": self.creds.callback_url if 'callback_url' in self.creds.__dict__.keys() else "https://nichind.dev",
            "lifetime": 1440
        }
        headers = {'Content-Type': 'application/json'}

        response = post(url, json=payload, headers=headers)
        data = response.json()

        if data.get("error"):
            raise ValueError(data.get("errors"))
        self.invoice.identifier = data.get("id")
        self.invoice.pay_info = data.get("url")
        return self.invoice.pay_info

    async def check(self):
        url = "https://api.crystalpay.io/v2/invoice/info/"
        payload = {
            "auth_login": self.creds.login,
            "auth_secret": self.creds.secret,
            "id": self.invoice.identifier
        }
        headers = {'Content-Type': 'application/json'}

        response = post(url, json=payload, headers=headers)
        data = response.json()

        self.invoice.status = 'paid' if data.get("state") == 'payed' else 'pending'
        return self.invoice.status
