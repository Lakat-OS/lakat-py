from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, 
    load_pem_public_key)
from cryptography.exceptions import InvalidSignature
import os

def _sign_with_private_key(private_key, message):
    """
    Sign a message with the provided private key.
    """
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def sign_message(message, private_key=None, private_key_file=None):
    """
    Sign a message using a private key directly or from a PEM file.
    """
    if private_key_file and os.path.exists(private_key_file):
        with open(private_key_file, "rb") as key_file:
            private_key = load_pem_private_key(key_file.read(), password=None)

    if not private_key:
        raise ValueError("A valid private key must be provided.")

    message_bytes = message.encode('utf-8')
    signature = _sign_with_private_key(private_key, message_bytes)
    return signature

def check_signature(message, signature, public_key_pem):
    """
    Check if the signature is valid for the given message and public key.
    """
    public_key = load_pem_public_key(public_key_pem)
    message_bytes = message.encode('utf-8')

    try:
        public_key.verify(
            signature,
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

def get_public_key_from_file(key_file_prefix: str):
    save_dir = os.path.join(os.getcwd(), ".ssh")
    public_key_path = os.path.join(save_dir, key_file_prefix + "_public_key.pem")
    with open(public_key_path, "rb") as key_file:
        public_key = load_pem_public_key(key_file.read())
    # Serialize the public key to bytes
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return public_key_bytes


# # Example Usage
# key_file_prefix = "lakat"
# save_dir = os.path.join(os.getcwd(), ".ssh")
# private_key_path = os.path.join(save_dir, key_file_prefix + "_private_key.pem")
# public_key_path = os.path.join(save_dir, key_file_prefix + "_public_key.pem")

# with open(public_key_path, "rb") as public_key_file:
#     public_key_pem = public_key_file.read()

# message = "This is a message."
# signature = sign_message(message, private_key_file=private_key_path)
# is_valid = check_signature(message, signature, public_key_pem)

# print("Signature valid:", is_valid)
