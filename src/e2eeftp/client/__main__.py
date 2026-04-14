"""
Main entry point for the E2EEFTP client command-line interface.

This module provides the script entry point for running the E2EEFTP client
as a standalone application. It parses command-line arguments for server
connection details and launches the interactive CLI.
"""

import argparse
from .cli import e2eeftpClientCli


def main():
    """
    Parse command-line arguments and start the E2EEFTP client CLI.

    This function sets up argument parsing for host and port options,
    creates a client CLI instance with the specified connection details,
    and starts the interactive session.

    Command-line options:
    --host: Server hostname or IP address (default: 127.0.0.1)
    --port: Server port number (default: 5001)
    """
    parse = argparse.ArgumentParser()
    parse.add_argument("--host", help="The gost for the server", default="127.0.0.1", type=str)
    parse.add_argument("--port", help="The port for the server", default=5001, type=int)
    args = parse.parse_args()

    server = e2eeftpClientCli(args.host, args.port)
    server.run()
    

if __name__ == "__main__":
    main()