from asyncio import run, sleep
from pyeasypay import *
from pyeasypay.core import Provider
from dotenv import load_dotenv


async def main():
    crystalpay = Provider('crystalpay', login='', secret='')
    cryptobot = Provider('cryptobot', api_key='', network='test')
    pay = EasyPay(network='test', providers=[crystalpay, cryptobot])

    invoice = await pay.create_invoice(15, 'RUB', 'crystalpay')
    while invoice.status != 'paid':
        await sleep(5)
        await invoice.check()
        print(invoice)


if __name__ == '__main__':
    run(main())
