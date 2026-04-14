"""
Simple E2EEFTP server example.

This script provides a minimal example of starting an E2EEFTP server
without generating keys. It assumes that cryptographic keys have already
been set up and are available in the expected locations.
"""

from src.e2eeftp import e2eeftp


def main() -> None:
    """
    Start the E2EEFTP server.

    This function creates an instance of the E2EEFTP server and starts
    it, beginning the listening loop for incoming client connections.
    The server will run until interrupted.
    """
    server = e2eeftp()
    server.run()


if __name__ == "__main__":
    main()
