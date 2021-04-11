from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes


class Secret:
    RSA_BIT_SIZE = 2048
    AES_BYTE_SIZE = 16
    AES_MAC_BYTE_SIZE = 16
    AES_NONCE_SIZE = 8

    def __init__(self):
        self.ready = False
        self.rsa_key_pair = None
        self.rsa_cipher = None
        self.aes_key = None
        self.aes_nonce = None
        self.aes_cipher = None

    def init_rsa(self, public_key: bytes = None) -> None:
        """
        Initialize RSA key & cipher
        """
        if public_key is None:
            self.rsa_key_pair = RSA.generate(self.RSA_BIT_SIZE)
        else:
            self.rsa_key_pair = RSA.import_key(public_key)
        self.rsa_cipher = PKCS1_OAEP.new(self.rsa_key_pair)

    def export_public_key(self) -> bytes:
        """
        Return public key as bytes
        """
        return self.rsa_key_pair.public_key().export_key()

    def encrypt_rsa(self, plaintext: bytes) -> bytes:
        """
        Encrypt given plaintext and return ciphertext using RSA
        """
        return self.rsa_cipher.encrypt(plaintext)

    def decrypt_rsa(self, ciphertext: bytes) -> bytes:
        """
        Decrypt given ciphertext and return plaintext using RSA
        """
        return self.rsa_cipher.decrypt(ciphertext)

    def init_aes(self, aes_key: bytes = None, aes_nonce: bytes = None) -> None:
        """
        Initialize AES key, nonce & cipher
        """
        if aes_key is None:
            self.aes_key = get_random_bytes(self.AES_BYTE_SIZE)
        else:
            self.aes_key = aes_key
        if aes_nonce is None:
            self.aes_nonce = get_random_bytes(self.AES_NONCE_SIZE)
        else:
            self.aes_nonce = aes_nonce

    def encrypt_aes(self, plaintext: bytes) -> bytes:
        """
        Encrypt given plaintext using AES and return ciphertext and mac tag
        """
        self.aes_cipher = AES.new(self.aes_key, AES.MODE_GCM, nonce=self.aes_nonce)
        ciphertext, mac_tag = self.aes_cipher.encrypt_and_digest(plaintext)
        return mac_tag + ciphertext

    def decrypt_aes(self, payload: bytes) -> bytes:
        """
        Parse payload, decrypt given ciphertext using AES, validate mac and return plaintext
        :return:
        """
        mac_tag = payload[:self.AES_MAC_BYTE_SIZE]
        ciphertext = payload[self.AES_MAC_BYTE_SIZE:]
        self.aes_cipher = AES.new(self.aes_key, AES.MODE_GCM, nonce=self.aes_nonce)
        return self.aes_cipher.decrypt_and_verify(ciphertext, mac_tag)

    def export_aes_key(self) -> bytes:
        """
        Return AES data as bytes
        """
        return self.aes_key + self.aes_nonce

    def parse_aes_key(self, payload: bytes) -> None:
        """
        Parse AES data from payload and populate AES key & nonce
        """
        self.init_aes(aes_key=payload[:self.AES_BYTE_SIZE], aes_nonce=payload[-self.AES_NONCE_SIZE:])
