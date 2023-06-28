from web3 import Web3, EthereumTesterProvider
import bitcoinlib
from hashlib import sha256

# function that hashes the latest block hash of both bitcoin and ethereum
def getTimestamp() -> bytes:
    ethBlockHash = getEthereumBlockHash()
    btcBlockHash = getBitcoinBlockHash()
    h1 = sha256()
    h1.update(ethBlockHash)
    h1.update(btcBlockHash)
    return h1.digest()

# def getTimestamp() -> bytes:
#     ethBlockHash = getEthereumBlockHash()
#     btcBlockHash = getBitcoinBlockHash()
#     h1 = sha256()
# h1.update(rawhex4)
#     block = web3.eth.get_block('latest')
#     # get block hash
#     blockhash = block['hash']
#     return bytes(str(blockhash))

    
def getBitcoinBlockHash() -> bytes:
    # block = bitcoinlib.blocks.get_block('latest')
    # # get block hash
    # blockhash = block.hash
    # blockhash = 1
    # return bytes(str(blockhash))
    return b'hallo'

def getEthereumBlockHash() -> bytes:
    myprovider = Web3.HTTPProvider('https://mainnet.infura.io/v3/5718340b942f4fc1a524b21ca5acbc92')
    w3 = Web3(myprovider)
    block = w3.eth.get_block('latest')
    # get block hash
    blockhash = block['hash']
    return bytes(blockhash)