import socket
import hashlib
import time

_socket = socket.socket()

try:
    serverIP = '127.0.0.1'
    port = 3000
    _socket.connect((serverIP, port))
    _socket.send('Miner'.encode('ascii'))
    print("Connected to server...")
except Exception:
    print("Can't connect to server...")

index = ""
current_hash = ""
difficulty = "000"

def getBlockDetails():
    _socket.send('**blockDetails'.encode('ascii'))
    data = _socket.recv(1024).decode('ascii')
    if '**toMiner' in data:
        index, current_hash = data.split(',')
        mine(index, current_hash)


def mine(_index, _current_hash):
    mining = True
    nonce = 0
    newhash = ""
    nextIndex = int(_index) + 1
    while newhash[0:3] != difficulty:
        print(calculateNextHash(nextIndex, _current_hash, nonce))
        nonce += 1
        newhash = calculateNextHash(nextIndex, _current_hash, nonce)

    _socket.send(f"**newHash{nextIndex},{newhash}".encode('ascii'))


def calculateNextHash(nextIndex, _current_hash, nonce):
    data = str(nextIndex) + _current_hash + str(nonce) + str(time.time())
    return hashlib.sha256(data.encode('utf8')).hexdigest()


while True:
    getBlockDetails()
    time.sleep(3)
