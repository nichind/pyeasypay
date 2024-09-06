from requests import get
from importlib.metadata import version
from os.path import dirname, basename, isfile, join
import glob


try:
    current_version = version("pyeasypay")
    last_version = get('https://pypi.org/pypi/pyeasypay/json').json()['info']['version']
    if last_version != current_version:
        print(f"pyeasypay {last_version} is avaliable (current: {current_version}) - pip install pyeasypay -U")
except:
    pass


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

    async def create_invoice(self, amount: int | float, currency: str = 'USD', provider: str | Provider = None,
                             identifier=None, **kwargs):
        invoice = Invoice(self.provider, amount=amount, currency=currency)
        if identifier:
            return await self.invoice(identifier=identifier, amount=amount, currency=currency, provider=provider,
                                      **kwargs)
        return await invoice.create(provider)

    async def invoice(self, **kwargs):
        invoice = Invoice(self.provider, **kwargs)
        return invoice

    def __repr__(self):
        return f'EasyPay({self.__dict__})'


class Invoice:
    def __init__(self, providers: Providers, **kwargs):
        """
        Invoice class, use it to create an invoice
        Args:
            amount: int
        Attributes:
            amount: int
            status: str
            identifier: str
        """

        self.providers = providers
        self.status = 'creating'
        self.identifier = None
        self.pay_info = None
        self.invoice = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    async def init_invoice(self, provider: str | Provider):
        modules = glob.glob(join(dirname(__file__) + '/providers', "*.py"))
        __all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
        provider_name = provider.name if isinstance(provider, Provider) else provider
        if provider_name not in __all__:
            raise ValueError(
                f'Provider {provider_name} is not supported'
            )

        module = __import__(f'pyeasypay.core.providers.{provider_name}',
                            globals(), locals(), ['Invoice'], 0)
        try:
            self.invoice = module.Invoice(
                self.providers.__dict__[provider_name],
                self, self.amount if 'amount' in self.__dict__ else None
            )
        except KeyError:
            raise ValueError(
                f'Provider {provider_name} '
                f'was not added, please add it first'
            )
        return self.invoice

    async def create(self, provider: str | Provider, run_check: bool = False):
        await self.init_invoice(provider)
        await self.invoice.create()

        if run_check:
            print(NotImplementedError('run_check is not implemented yet, check invoice status manually'))

        return self

    async def check(self):
        if 'identifier' not in self.__dict__ or self.identifier is None:
            raise ValueError('Identifier is not provided, create invoice first or set identifier manually')
        if self.invoice is None:
            if 'provider' not in self.__dict__.keys():
                raise ValueError('Provider is not provided, create invoice first or set provider manually')
            await self.init_invoice(self.provider)
        return await self.invoice.check()

    def __repr__(self):
        return f'Invoice({self.__dict__})'
