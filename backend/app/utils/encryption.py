from cryptography.fernet import Fernet

import os

def get_cipher():

    key = os.getenv("ENCRYPTION_KEY")

    if not key:

        raise RuntimeError("ENCRYPTION_KEY missing")

    return Fernet(key)

def encrypt(value: str) -> str:

    return get_cipher().encrypt(value.encode()).decode()

def decrypt(token: str) -> str:

    return get_cipher().decrypt(token.encode()).decode()


