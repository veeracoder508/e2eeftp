"""
Example E2EEFTP client CLI instance.

This script demonstrates how to start the E2EEFTP client command-line
interface for interactive file transfers with a server. It connects
to the default server location and provides a user-friendly terminal
interface for performing secure file operations.
"""

from src.e2eeftp import e2eeftpClientCli


def main():
    """
    Start the E2EEFTP client CLI.

    This function creates a client CLI instance with default connection
    settings and starts the interactive command loop, allowing users
    to send commands like SEND, GET, LIST, etc. to the E2EEFTP server.
    """
    cli = e2eeftpClientCli()
    cli.run()


if __name__ == "__main__":
    main()
