"""
Example E2EEFTP server instance.

This script demonstrates how to set up and run a basic E2EEFTP server.
It generates the necessary cryptographic keys and starts the server
listening for client connections.
"""

from e2eeftp import e2eeftp
from e2eeftp import generate_keys


def main():
    """
    Generate keys and start the E2EEFTP server.

    This function creates the necessary cryptographic key pairs for
    server and client authentication, then initializes and runs the
    E2EEFTP server to handle incoming secure file transfer requests.
    """
    server = e2eeftp()
    generate_keys()
    server.run()


if __name__ == "__main__":
    main()
