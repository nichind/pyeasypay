from asyncio import run, sleep
from pyeasypay import *
from pyeasypay.core import Provider
from dotenv import load_dotenv


async def main():
    crystalpay = Provider('crystalpay', login='', secret='')
    cryptobot = Provider('cryptobot', api_key='', network='test')
    pay = EasyPay(providers=[crystalpay, cryptobot])
    invoice = await pay.create_invoice(0.25, 'TON', 'cryptobot')
    invoice_from_memory = await pay.invoice(amount=0.25, currency='TON', provider='cryptobot', identifier=invoice.identifier,
                                            pay_info=invoice.pay_info)
    while invoice_from_memory.status != 'paid':
        await sleep(5)
        await invoice_from_memory.check()
        print(invoice_from_memory)


if __name__ == '__main__':
    run(main())
