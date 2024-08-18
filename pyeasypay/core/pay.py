from dotenv import load_dotenv
from os import environ
from os.path import dirname, basename, isfile, join
import glob


class Provider:
    """
    Provider instance
    """
    def __init__(self, name: str, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.name: str = name

    def __repr__(self):
        return f'Provider({self.__dict__})'


class Providers:
    def __init__(self):
        pass


class EasyPay:
    """
    Create an instance of EasyPay
    """
    def __init__(self, **kwargs):
        load_dotenv()
        self.provider = Providers()
        for k, v in kwargs.items():
            setattr(self, k, v)
        if 'provider' not in self.__dict__ and 'providers' not in self.__dict__:
            raise ValueError('At least one provider is required')
        if 'providers' in self.__dict__:
            for provider in self.__dict__['providers']:
                self.configure_provider(provider)

    def configure_provider(self, provider: str | Provider, **kwargs):
        setattr(
            self.provider,
            provider.name if isinstance(provider, Provider) else provider,
            Provider(provider, **kwargs) if isinstance(provider, str) else provider
        )

    async def create_invoice(self, amount: int | float, currency: str = 'USD', provider: str | Provider = None):
        invoice = Invoice(self.provider, amount, currency)
        return await invoice.create(provider)

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
    def __init__(self, providers: Providers, amount: int | float, currency: str = 'USDT'):
        self.providers = providers
        self.currency = currency
        self.amount = amount
        self.status = 'creating'
        self.identifier = None
        self.pay_info = None
        self.invoice = None

    async def create(self, provider: str | Provider, run_check: bool = False):
        modules = glob.glob(join(dirname(__file__) + '\\providers', "*.py"))
        __all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

        if ((isinstance(provider, str) and provider not in __all__) or
                (isinstance(provider, Provider) and provider.name not in __all__)):
            raise ValueError(
                f'Provider {provider.name if isinstance(provider, Provider) else provider} is not supported'
            )

        module = __import__(f'pyeasypay.core.providers.{provider.name if isinstance(provider, Provider) else provider}',
                            globals(), locals(), ['Invoice'], 0)
        try:
            self.invoice = module.Invoice(
                self.providers.__dict__[provider.name if isinstance(provider, Provider) else provider],
                self, self.amount
            )
        except KeyError:
            raise ValueError(
                f'Provider {provider.name if isinstance(provider, Provider) else provider} '
                f'was not added, please add it first'
            )
        await self.invoice.create()

        if run_check:
            print(NotImplementedError('run_check is not implemented yet, check invoice status manually'))

        return self

    async def check(self):
        if self.invoice is None:
            return ValueError('Invoice needs to be created first')
        return await self.invoice.check()

    def __repr__(self):
        return f'Invoice({self.__dict__})'
