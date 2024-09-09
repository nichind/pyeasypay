from collections.abc import Iterable
from typing import Any, List, Self
from requests import get
from importlib.metadata import version
from os.path import dirname, basename, isfile, join
import glob


try:
    current_version = version("pyeasypay")
    last_version = get('https://pypi.org/pypi/pyeasypay/json').json()['info']['version']
    print(f"pyesaypay {current_version} is still in beta, there can be some bugs, if you find one - report it at https://github.com/nichind/pyeasypay/issues")
    if last_version != current_version:
        print(f"pyeasypay {last_version} is avaliable (current: {current_version}) - python3 -m pip install pyeasypay -U")
except:
    pass


class Provider:
    def __init__(self, name: str, **kwargs) -> None:
        """
        Provider initialization

        Args:
            name: Provider name, should be the same as the module name
            **kwargs: Additional keyword arguments to set attributes for the 
            
            
        kwargs you may use (not limited to):
            api_key: API key for the provider
            secret: Secret key for the provider
            login: Login for the provider
            password: Password for the provider
            redirect_url: Redirect URL for the provider
            callback_url: Callback URL for the provider
            network: Network for the provider
        """
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.name: str = name

    def __repr__(self) -> str:
        return f'Provider({self.__dict__})'


class Providers:
    def __init__(self) -> None:
        """
        Providers initialization

        Finds all provider modules in the providers directory and
        adds them as attributes to the instance
        """
        modules = glob.glob(join(dirname(__file__) + '/providers', "*.py"))
        __all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
        for _ in __all__:
            setattr(self, _, Provider(_))

    def list(self) -> List[Provider]:
        """
        List all providers available in the EasyPay instance
        """
        return list(self.__dict__.values())

    def __repr__(self) -> str:
        return f'Providers({self.__dict__})'



class Invoice:
    def __init__(self, providers: Providers, **kwargs) -> None:
        """
        Invoice initialization

        Args:
            providers: Providers instance
            **kwargs: Additional keyword arguments to set attributes for the instance
        """
        self.providers = providers
        self.status = 'creating'
        self.identifier = None
        self.pay_info = None
        self.invoice = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    async def init_invoice(self, provider: str | Provider) -> Self:
        """
        Initialize invoice object

        Args:
            provider: Provider name or Provider instance

        Returns:
            Invoice object

        Raises:
            ValueError: If provider is not supported or was not added
        """
        modules = glob.glob(join(dirname(__file__) + '/providers', "*.py"))
        __all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
        provider_name = provider.name if isinstance(provider, Provider) else provider
        if self.currency is None or self.currency == '':
            self.currency = 'USD'
            print("Currency was not provided for create_invoice, defaulting to USD")
        if provider_name == 'None' or provider_name is None or provider_name == '':
            for provider, args in self.providers.__dict__.items():
                if len(args.__dict__) > 1:
                    provider_name = provider
                    print(f"Provider was not provided for create_invoice, defaulting to {provider_name}"
                          " since it was added to the EasyPay instance") 
                    break
            if provider_name == '' or provider_name is None or provider_name == 'None':
                raise ValueError('Provider is not provided for create_invoice')
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

    async def create(self, provider: str | Provider, run_check: bool = False) -> Self:
        """
        Creates an invoice object

        Args:
            provider: Provider name or Provider instance
            run_check: Whether to run invoice status check after creation

        Returns:
            Self: self (Invoice object)

        Raises:
            ValueError: If provider is not supported or was not added
        """
        await self.init_invoice(provider)
        await self.invoice.create()

        if run_check:
            print(NotImplementedError('run_check is not implemented yet, check invoice status manually'))

        return self

    async def check(self) -> str:
        """
        Checks the status of the invoice.

        Returns:
            str: Invoice status (paid or else)

        Raises:
            ValueError: If provider or identifier were not provided.
        """
        if 'identifier' not in self.__dict__ or self.identifier is None:
            raise ValueError('Identifier is not provided, create invoice first or set identifier manually')
        if self.invoice is None:
            if 'provider' not in self.__dict__.keys():
                raise ValueError('Provider is not provided, create invoice first or set provider manually')
            await self.init_invoice(self.provider)
        return await self.invoice.check()

    def __repr__(self) -> str:
        return f'Invoice({self.__dict__})'



class EasyPay:
    """
    EasyPay instance
    """
    def __init__(self, **kwargs) -> None:
        """
        EasyPay initialization

        Args:
            **kwargs: Additional keyword arguments to set attributes for the instance
        """
        self.provider = Providers()
        for k, v in kwargs.items():
            setattr(self, k, v)
        if 'provider' not in self.__dict__ and 'providers' not in self.__dict__:
            raise ValueError('At least one provider is required for EasyPay to work')
        if 'providers' in self.__dict__:
            if isinstance(self.__dict__['providers'], Provider):
                return self.configure_provider(self.__dict__['providers'])
            for provider in self.__dict__['providers']:
                self.configure_provider(provider)

    def configure_provider(self, provider: str | Provider, **kwargs) -> None:
        """
        Configure provider for EasyPay instance

        Args:
            provider: Provider instance or name of provider as string
            **kwargs: Additional keyword arguments to pass to Provider constructor
        """
        setattr(
            self.provider,
            provider.name if isinstance(provider, Provider) else provider,
            Provider(provider, **kwargs) if isinstance(provider, str) else provider
        )

    async def create_invoice(self, amount: int | float, currency: str = 'USD', provider: str | Provider = None,
                             identifier=None, **kwargs) -> Invoice:
        """_summary_

        Args:
            amount (int | float): _description_
            currency (str, optional): _description_. Defaults to 'USD'.
            provider (str | Provider, optional): _description_. Defaults to None.
            identifier (_type_, optional): _description_. Defaults to None.

        Returns:
            Invoice: invoice object
        """
        invoice = Invoice(self.provider, amount=amount, currency=currency)
        if identifier:
            return await self.invoice(identifier=identifier, amount=amount, currency=currency, provider=provider,
                                      **kwargs)
        return await invoice.create(provider)

    async def invoice(self, **kwargs) -> Invoice | None:
        """
        Creates an invoice object

        Args:
            **kwargs: Arguments to pass to Invoice constructor

        Returns:
            Invoice | None: Invoice object or None if failed
        """
        invoice = Invoice(self.provider, **kwargs)
        return invoice

    def __repr__(self) -> str:
        return f'EasyPay({self.__dict__})'
