from ecdsa import SigningKey, SECP256k1
import sha3
import qrcode
import socket
from threading import Thread

socket = socket.socket()

try:
    serverIP = '127.0.0.1'
    port = 3000
    socket.connect((serverIP, port))
    socket.send("Wallet Generator".encode('ascii'))

    print("Connected to server")
except Exception:
    print("Can't connect to server...")



def checksum_encode(addr_str):
    keccak = sha3.keccak_256()
    out = ''
    addr = addr_str.lower().replace('0x', '')
    keccak.update(addr.encode('ascii'))
    hash_addr = keccak.hexdigest()
    for i, c in enumerate(addr):
        if int(hash_addr[i], 16) >= 8:
            out += c.upper()
        else:
            out += c
    return '0x' + out


def generateWallet():
    keccak = sha3.keccak_256()

    priv = SigningKey.generate(curve=SECP256k1)
    pub = priv.get_verifying_key().to_string()

    keccak.update(pub)

    address = keccak.hexdigest()[24:]

    def test(addrstr):
        assert(addrstr == checksum_encode(addrstr))

    print("Private key:", priv.to_string().hex())
    print("Public key: ", pub.hex())
    print("Address:    ", checksum_encode(address))

    walletAddress = checksum_encode(address)

    # save QR code and other inputs=====================================
    # Address
    addr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    addr.add_data(checksum_encode(address))
    addr.make(fit=True)

    addrImg = addr.make_image(fill_color="black", back_color="white")

    addrImg.save('./templates/img/address.png')

    # Private Key
    priveKey = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=0,
    )
    priveKey.add_data(priv.to_string().hex())
    priveKey.make(fit=True)

    priveKeyImg = priveKey.make_image(fill_color="black", back_color="white")

    priveKeyImg.save('./templates/img/privKey.png')

    return walletAddress


# Save the text keys=========================================================


# Send to blockchain
def sendToChain(addr):
    socket.send(addr.encode('ascii'))


while True:
    cmd = input("\n'G' to generate Wallet ||'B' to get wallet balance || 'S' to send: ")
    if cmd == 'G' or cmd == 'g':
        sendToChain('**wallet'+generateWallet())
    if cmd == 'B' or cmd == 'b':
        _addr = input("Enter or Scan Address: ")
        sendToChain(f'**balance{_addr}')
        print(f"Current balance: {socket.recv(1024).decode('ascii')}")
    if cmd == 'S' or cmd == 's':
        addrFrom = input("Sender's address: ")
        addrTo = input("Receiver's address: ")
        amount = input("Enter amount: ")
        sendToChain(f'**sendCoins{addrFrom},{addrTo},{amount}')
        print("Transaction Successful!")
