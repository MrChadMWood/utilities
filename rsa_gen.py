import argparse
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_keys(private_out, public_out, _dir, password=None):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    encryption_algorithm = serialization.NoEncryption()
    if password:
        encryption_algorithm = serialization.BestAvailableEncryption(password.encode())

    encrypted_pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm
    )

    # Generate public key in OpenSSH format
    pem_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )

    os.makedirs(_dir, exist_ok=True)

    with open(os.path.join(_dir, private_out), "wb") as private_key_file:
        private_key_file.write(encrypted_pem_private_key)

    with open(os.path.join(_dir, public_out), "wb") as public_key_file:
        public_key_file.write(pem_public_key)

def main():
    parser = argparse.ArgumentParser(description="Generate RSA key pairs")
    parser.add_argument(
        "-p", "--password", 
        type=str, 
        help="Password to encrypt the private key (optional)"
    )
    parser.add_argument(
        "--private-out", 
        type=str, 
        default="rsa.pem",
        help="Output filename for the private key (default: rsa.pem)"
    )
    parser.add_argument(
        "--public-out", 
        type=str, 
        default="rsa.pub",
        help="Output filename for the public key (default: rsa.pub)"
    )
    parser.add_argument(
        "-d", "--dir", 
        type=str, 
        default="./",
        help="Output directory for keys (default: ./)"
    )

    args = parser.parse_args()
    generate_keys(args.private_out, args.public_out, args.dir, args.password)

if __name__ == "__main__":
    main()
