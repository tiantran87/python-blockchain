# Import dependencies
import os
import subprocess
import json
from dotenv import load_dotenv
from web3 import Web3
from constants import *
from bit import *
from web3.middleware import geth_poa_middleware
from eth_account import Account

from web3.middleware import geth_poa_middleware

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)



load_dotenv()
mnemonic=os.getenv("mnemonic")

# Create a function called `derive_wallets`
def derive_wallets(mnemonic, coin, numderive):
    command = f"php ./derive -g --mnemonic=\"{mnemonic}\" --coin=\"{coin}\" --numderive=\"{numderive}\" --cols=index,path,privkey,pubkey,pubkeyhash,xprv,xpub,address --format=json"
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {"btc-test": derive_wallets(mnemonic, BTCTEST, numderive), "eth": derive_wallets(mnemonic, ETH, numderive)}

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)
    

    
#Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH: 
        gasEstimate = w3.eth.estimateGas(
            {"from": account.address, "to": to, "value": amount}
        )
        return {
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
        }
    elif coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# create a account to hold Ethereum 
eth_acc = priv_key_to_account(ETH, derive_wallets(mnemonic, ETH, numderive)[0]['privkey'])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    txn = create_tx(coin, account, to, amount)
    if coin == ETH:
        signed_txn = eth_acc.sign_transaction(txn)
        result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(result.hex())
        return result.hex()
    elif coin == BTCTEST:
        tx_btctest = create_tx(coin, account, to, amount)
        signed_txn = account.sign_transaction(txn)
        print(signed_txn)
        return NetworkAPI.broadcast_tx_testnet(signed_txn)
    
