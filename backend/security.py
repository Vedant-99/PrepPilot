import hashlib
import hmac
import secrets

def hash_password(password: str) -> str :
    # Random salt-> The same password gives a different result every time
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt = salt, n=2**14, r=8, p=1)

    #  Save salt and hsh together as one text: "salt$hash"
    return salt.hex() + "$" + digest.hex()


def verify_password(password:str, stored:str) -> bool:
    # split the saved text back into salt and hash
    salt_hex, hash_hex = stored.split("$")
    salt = bytes.fromhex(salt_hex)

    # Scramble the typed password with the same salt, then compare

    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(digest.hex(),hash_hex)
