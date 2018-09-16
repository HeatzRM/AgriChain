import socket
from threading import Thread
import json
import time


# Blockchain ledgers
addresses = {}
pendingTransactions = []
miningJob = []
blockChain = []


class Transaction():
    """docstring for Transac"""

    def __init__(self, sender, receiver, amount):

        super(Transaction, self).__init__()
        self.sender = sender
        self.receiver = receiver
        self.amount = amount


# Defing the Blockchain======
class Block():
    """docstring for Block"""

    def __init__(self, index, current_hash, transactions, previous_hash):
        super(Block, self).__init__()
        self.index = index
        self.current_hash = current_hash
        self.transactions = transactions
        self.previous_hash = previous_hash


def genesisBlock():
    _block = Block(0, '56360BFB8218A44DD9943B4F7EA8A4EF80109E067C9D9DA3DC7605BE50126ABB', [], '0000')
    blockChain.append(_block)


def createNewBlock(_nextIndex, _newHash):
    _block = Block(_nextIndex, _newHash, miningJob, blockChain[-1].previous_hash)
    blockChain.append(_block)
    updateBalance(miningJob)


def updateBalance(_miningJob):
    for tx in _miningJob:
        adresses[tx.sender] -= tx.amount
        adresses[tx.receiver] += tx.amount
        broadCastToAllNodes(f'**updateBalances{tx.sender},{tx.receiver},{tx.amount}')


genesisBlock()
# Server================================================================
# Dict of clients
arrayClients = {}


# Start Server
coopName = input("Enter Coop Name: ")
port = int(input("Enter port: "))
ipAddress = '127.0.0.1'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', port))
server.listen()


# Accept Clients
def recvClients():
    print("Waiting for connections...")
    while True:
        try:
            _client, add = server.accept()
            data = _client.recv(1024).decode('ascii')

            if '**reciprocateConnection ' in data:
                data = data.replace('**reciprocateConnection ', '')
                processedData = data.split(',')

                print(f"{processedData[0]} Connected Succesfully!")
                arrayClients[processedData[0]] = _client
                Thread(target=handleClient, args=(_client, processedData[0])).start()

                reciprocalConnection(processedData[0], processedData[1], processedData[2])
            else:
                arrayClients[data] = _client
                print(f"{data} Connected Succesfully!")
                Thread(target=handleClient, args=(_client, data)).start()
        except Exception:
            break


# Recv Messages
def handleClient(client, coopName):
    clientConnected = True

    while clientConnected:
        try:
            msg = client.recv(1024).decode('ascii')
            # if msg != "":
            #     print(msg)
            if '**wallet' in msg:
                msg = msg.replace('**wallet', '')
                addresses[msg] = 10
                print("New Address accepted!")
                broadCastToAllNodes('**updateAdresses' + msg)
            if '**balance' in msg:
                msg = msg.replace('**balance', '')
                client.send(str(addresses[msg]).encode('ascii'))
            if '**sendCoins' in msg:
                msg = msg.replace('**sendCoins', '')
                _sender, _rcver, _amount = msg.split(',')
                if addresses[_sender] >= int(_amount):
                    addresses[_sender] -= int(_amount)
                    addresses[_rcver] += int(_amount)
                    broadCastToAllNodes(f'**updateBalances{_sender},{_rcver},{_amount}')
            if '**updateAdresses' in msg:
                msg = msg.replace('**updateAdresses', '')
                addresses[msg] = 10
                print("Address Updated!")
            if '**updatePendingTransaction' in msg:
                msg = msg.replace('**updatePendingTransaction', '')
                _sender, _rcver, _amount = msg.split(',')
                tx = Transaction(_sender, _rcver, _amount)
                pendingTransactions.append(tx)
                print('Pending Transactions Updated!')
            if '**blockDetails' in msg:
                if len(miningJob) != 0:
                    client.send(f"**toMiner{len(blockChain)},{blockChain[-1].current_hash}")
                else:
                    client.send("empty".encode('ascii'))
            if '**newHash' in msg:
                msg = msg.replace('**newHash', '')
                nextIndex, newHash = msg.split(',')
                createNewBlock(nextIndex, newHash)
            if '**updateBalances' in msg:
                msg = msg.replace('**updateBalances', '')
                _sender, _rcver, _amount = msg.split(',')
                addresses[_sender] -= int(_amount)
                addresses[_rcver] += int(_amount)
                print("Balances Updated!")
        except Exception:
            arrayClients.pop(coopName)
            print(coopName + ' has been logged out')
            clientConnected = False
# ============================================================================

# Client =====================================================================


# Dict of server
arrayServers = {}


def broadCastToAllNodes(data):
    for key, value in arrayServers.items():
        value.send(data.encode('ascii'))


def connectToInitialPeers():
    file = open('initial_peers.json', 'r')
    contents = file.read()

    obj = json.loads(contents)

    for node in obj:
        if node['port'] != port:
            try:
                _socket = socket.socket()
                _socket.connect((node['ipAddress'], node['port']))
                _socket.send(f"**reciprocateConnection {coopName},{ipAddress},{port}".encode('ascii'))
                # _socket.send(coopName.encode('ascii'))
                arrayServers[node['coopName']] = _socket
                print(f"Succesfully Connected to {node['coopName']}")
            except Exception:
                print(f"Can't connect to {node['coopName']}")


def reciprocalConnection(_coopName, ipAddress, port):
    try:
        _socket = socket.socket()
        _socket.connect((ipAddress, int(port)))
        arrayServers[_coopName] = _socket
        _socket.send(coopName.encode('ascii'))
        print(f"Reciprocal Connection to {_coopName} is Succesful!")
    except Exception:
        print(f"Can't reciprocate connection to {_coopName}")


def handleServers():
    while True:
        msg = input()
        for key, value in arrayServers.items():
            value.send(msg.encode('ascii'))


def createMiningJob():
    while True:
        if len(miningJob) == 0 and len(pendingTransactions) != 0:
            for tx in pendingTransactions:
                miningJob.append(tx)
                pendingTransactions.pop()
                print("Created a new Mining Job!")

        time.sleep(20)


#  Main========================================================================
Thread(target=recvClients).start()
connectToInitialPeers()
Thread(target=handleServers).start()
Thread(target=createMiningJob).start()
