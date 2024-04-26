import asyncio
import random

from web3 import AsyncWeb3

from utils import script_exceptions, abi_read, logger
from config import NEED_DELAY_ACT, DELAY_ACT, TEXT, NUM_THREADS, VALUE_ETH, RPC


with open("data/private_keys.txt") as file:
    evm_keys = [key.strip() for key in file]
    
    
class EtherClient:
    TOKEN_ABI: str = abi_read("abies/evm_token.json")
    
    def __init__(self, index: int, network: str, private: str, proxy: str = None) -> None:
        self.index = index
        self.rpc = network
        self.proxy = proxy
        self.request_kwargs = None

        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self.rpc))
        
        self.private_key = private
        self.account = self.w3.eth.account.from_key(self.private_key)
        self.address = self.account.address

    @staticmethod
    def random_int(lst: list) -> int:
        return random.randint(lst[0], lst[1])
    
    @staticmethod
    def random_float(lst: list) -> int:
        return random.uniform(lst[0], lst[1])
    
    @property
    async def nonce(self) -> int:
        return await self.w3.eth.get_transaction_count(self.address)
    
    @property
    async def wait_for_gas(self) -> int:
        return await self.w3.eth.gas_price
    
    @property
    async def native_balance(self) -> int:
        balance = await self.w3.eth.get_balance(self.address)
        
        return balance
    
    @script_exceptions
    async def bridge_Sep(self, to_address: str) -> str:
        data = f"0x9a2ac6d5000000000000000000000000{self.address[2:]}0000000000000000000000000000000000000000000000000000000000030d4000000000000000000000000000000000000000000000000000000000000000600000000000000000000000000000000000000000000000000000000000000000"
        gwei = await self.wait_for_gas
        
        tx = {
            'from': self.address,
            'to': self.w3.to_checksum_address(to_address),
            'gasPrice': gwei,
            'nonce': await self.nonce,
            'value': self.w3.to_wei(self.random_float(VALUE_ETH), "ether"),
            'chainId': await self.w3.eth.chain_id,
            "data": data,
        }
        gas = int(await self.w3.eth.estimate_gas(tx))
        tx.update({"gas": gas})
        
        return await self.send_transaction(tx)

    @script_exceptions
    async def send_transaction(self, transaction: dict) -> str:
        sign_tx = self.account.sign_transaction(transaction)
        tx_hash = self.w3.to_hex(await self.w3.eth.send_raw_transaction(sign_tx.rawTransaction))
        reciept = await self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if NEED_DELAY_ACT:
            await asyncio.sleep(self.random_int(DELAY_ACT))
        
        logger.success(f"Acc.{self.index} | Transaction Hash: https://sepolia.etherscan.io/tx/{tx_hash}")
            
        return tx_hash


async def run_script(index: int, key: str, proxy: str):
    logger.info(f"Acc.{index} | Preparing for bridge")
    client = EtherClient(index, RPC, key, proxy)
    
    await client.bridge_Sep(to_address="0xcb95f07B1f60868618752CeaBBe4e52a1f564336")
    
    
async def main():
    tasks = []
    for index, evm_private in enumerate(evm_keys, start=1):
        task = run_script(index, evm_private, None)
        tasks.append(task)

        if len(tasks) == NUM_THREADS:
            await asyncio.gather(*tasks)
            tasks.clear()


    if tasks:
        await asyncio.gather(*tasks)
        
        
if __name__ == '__main__':
    print(f'{TEXT}')
    asyncio.run(main())
    
    print('\n\nThank you for using the software. </3\n')
    input('Press "ENTER" To Exit..')