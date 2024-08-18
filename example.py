from asyncio import run, sleep
from pyeasypay import *
from pyeasypay.core import Provider
from dotenv import load_dotenv


async def main():
    crystalpay = Provider('crystalpay', login='', secret='')
    cryptobot = Provider('cryptobot', api_key='16439:AAUlIiiHO7M0xhCjXriuNTz5BHPvjgzLLPy', network='test')
    pay = EasyPay(providers=[crystalpay, cryptobot])
    invoice = await pay.create_invoice(0, 'TON', 'cryptobot')
    while invoice.status != 'paid':
        await sleep(5)
        await invoice.check()
        print(invoice)


if __name__ == '__main__':
    run(main())
