from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import os

## os.path.join(os.getcwd(), ".ssh")
## os.path.expanduser("~/.ssh")
def create_key_pair(key_size=2048, key_file_prefix="lakat", save_dir=os.path.join(os.getcwd(), ".ssh")):
    """
    Create an RSA key pair and save them as PEM files in the specified directory.
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )

    # Generate public key
    public_key = private_key.public_key()

    # Ensure save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Save private key
    private_key_file = os.path.join(save_dir, key_file_prefix + "_private_key.pem")
    with open(private_key_file, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    # Save public key
    public_key_file = os.path.join(save_dir, key_file_prefix + "_public_key.pem")
    with open(public_key_file, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    return private_key_file, public_key_file

# # Example Usage
# private_key_path, public_key_path = create_key_pair(key_file_prefix="lakat")
# print("Private key saved to:", private_key_path)
# print("Public key saved to:", public_key_path)
