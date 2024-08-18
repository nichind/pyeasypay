from asyncio import run, sleep
from pyeasypay import *


async def main():
    pay = EasyPay(network='test')

    invoice = await pay.create_invoice(0.25, 'TON')
    while invoice.status != 'paid':
        await sleep(5)
        await invoice.check()
        print(invoice)


if __name__ == '__main__':
    run(main())
