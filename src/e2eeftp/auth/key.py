"""
Key generation utilities for E2EEFTP authentication.

This module provides functions for generating Ed25519 key pairs used in the
end-to-end encryption authentication system. It handles the creation of server
and client keys, saving them to appropriate files, and managing the authorized
clients list.
"""

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64
from rich import print

def generate_keys():
    """
    Generates and saves Ed25519 key pairs for server and client authentication.

    This function creates cryptographic key pairs for both the server and client
    components of E2EEFTP. It generates:

    - Server private key (server_id.key) - kept secret on the server
    - Server public key (known_server.pub) - shared with clients
    - Client private key (client_id.key) - kept secret on the client
    - Client public key - added to authorized_clients.pub for server authorization

    The keys are saved in PEM format for private keys and appropriate formats
    for public keys. The function provides user feedback about where to place
    the generated files.

    Note:
        This function appends to authorized_clients.pub if it exists, allowing
        multiple client keys to be authorized.
    """
    # --- Generate Server Keys ---
    print("--- Generating Server Keys ---")
    server_priv_key = ed25519.Ed25519PrivateKey.generate()
    server_pub_key = server_priv_key.public_key()

    # Save server private key in PEM format
    with open("server_id.key", "wb") as f:
        f.write(server_priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print("Saved 'server_id.key' [blue](private)[/blue]. Place this in your server's root directory.")

    # Save server public key in PEM format (for client's known_server.pub)
    with open("known_server.pub", "wb") as f:
        f.write(server_pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print("Saved 'known_server.pub' [blue](public)[/blue]. Copy this to your client's directory.")

    # --- Generate Client Keys ---
    print("\n--- Generating Client Keys ---")
    client_priv_key = ed25519.Ed25519PrivateKey.generate()
    client_pub_key = client_priv_key.public_key()

    # Save client private key in PEM format
    with open("client_id.key", "wb") as f:
        f.write(client_priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print("Saved 'client_id.key' [blue](private)[/blue]. Place this in your client's directory.")

    # Get client public key in raw format, then base64 encode it for authorized_clients.pub
    client_pub_key_raw_b64 = base64.b64encode(client_pub_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ))

    # Create or append to the authorized_clients.pub file
    with open("authorized_clients.pub", "a") as f:
        f.write(client_pub_key_raw_b64.decode() + '\n')
    
    print("\n--- Authorization ---")
    print("The client's public key has been added to 'authorized_clients.pub'.")
    print("Place this file in your server's root directory.")
    print(f"Key added: [yellow]{client_pub_key_raw_b64.decode()}[/yellow]")
    print("------------------------")
