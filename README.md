
<div align="center" style="display: flex; flex-flow: column wrap;">
<br><br>
<img src="/assets/img/pyeasypay.svg" alt="easypay" style="width: 300px"/>
<br><br>

[![Get on pypi](https://img.shields.io/pypi/v/pyeasypay.svg)](https://pypi.org/project/pyeasypay/)
[![Last commit](https://img.shields.io/github/last-commit/nichind/pyeasypay.svg)](https://github.com/nichind/pyeasypay)
[![Pip module installs total downloads](https://img.shields.io/pypi/dm/pyeasypay.svg)](https://pypi.org/project/pyeasypay/)
[![GitHub stars](https://img.shields.io/github/stars/nichind/pyeasypay.svg)](https://github.com/nichind/pyeasypay)
<br>
[![Telegram](https://img.shields.io/badge/Telegram-Telegram-0088cc?logo=telegram&logoColor=white)](https://t.me/pyeasypay)
[![Discord](https://img.shields.io/badge/Discord-Discord-5865F2?logo=discord&logoColor=white)](https://discord.gg/nichind)
</div>

# Installation
Install package with pip:
```commandline
pip install pyeasypay
```

# Example usage
```python
from asyncio import run, sleep
from pyeasypay import EasyPay, Provider


async def main():
    cryptobot = Provider(name='cryptobot', api_key='')
    crystalpay = Provider(name='crystalpay', login='', secret='')
    pay = EasyPay(providers=[cryptobot, crystalpay])
    invoice = await pay.create_invoice(15, 'RUB', 'cryptobot')
    
    print(f"Invoice URL: {invoice.pay_info}")
    
    while invoice.status != 'paid':
        await sleep(5)
        await invoice.check()
        
    if invoice.status == 'paid':
        print('Invoice paid! 🎉')
        
if __name__ == '__main__':
    run(main())
```

# Supported providers

| Name       | Tested | Required kwargs   |
|------------|---------|-------------------|
| CryptoBot  | ✅       | `api_key`         |
| CrystalPay | ✅       | `login`, `secret` |
| AAIO       | ❌       | -                 |

# Contributors

<img src="https://contrib.rocks/image?repo=nichind/pyeasypay" alt="Contributors" style="max-width: 100%;"/>
