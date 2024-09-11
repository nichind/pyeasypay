from asyncio import run, sleep
from pyeasypay import EasyPay, Provider


async def main():
    
    # Init providers
    crystalpay = Provider('crystalpay', login='', secret='')
    cryptobot = Provider('cryptobot', api_key='16439:AAWcbxKxgsvblzwgMM5EGYIIOXAsltpInQ5', network='test')
    
    pay = EasyPay(providers=[crystalpay, cryptobot])
    
    # Create invoice
     = await pay.create_invoice(0.25, 'TON', 'cryptobot')
    
    # Save your invoice to memory
    # Code here...
    
    # Init invoice from memory     
    invoice_from_memory = await pay.invoice(
        provider='cryptobot', identifier=invoice.identifier, pay_info=invoice.pay_info)
    
    while await invoice_from_memory.check() is False:
        await sleep(5)
        print(invoice_from_memory)


    if invoice_from_memory.status == 'paid':
        print(f"Inovoice {invoice_from_memory.identifier} paid!")

if __name__ == '__main__':
    run(main())
