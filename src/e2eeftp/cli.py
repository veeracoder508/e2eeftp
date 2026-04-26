"""
Command-line interface for E2EEFTP.

This module provides the main entry point for running E2EEFTP in either server or client mode.
It handles command-line argument parsing and delegates to the appropriate components.
"""

import argparse
from .server import e2eeftp
from .client.cli import e2eeftpClientCli


__all__ = ["cli"]

def client_cli(host: str, port: int):
    """
    Run the E2EEFTP client CLI connecting to the specified host and port.

    Args:
        host (str): The hostname or IP address of the server to connect to.
        port (int): The port number to connect to on the server.

    This function creates an instance of the E2EEFTP client CLI and starts its interactive
    command loop, allowing users to perform file operations on the remote server.
    """
    server = e2eeftpClientCli(host, port)
    server.run()

def server(host: str, port: int):
    """
    Run the E2EEFTP server on the specified host and port.

    Args:
        host (str): The hostname or IP address to bind the server to.
        port (int): The port number to bind the server to.

    This function creates an instance of the E2EEFTP server and starts it, listening
    for incoming client connections and handling FTP commands with end-to-end encryption.
    """
    server = e2eeftp(host, port)
    server.run()

def cli():
    """
    Main CLI entry point that parses command-line arguments and starts either server or client mode.

    This function sets up an argument parser with subcommands for server and client modes,
    parses the command-line arguments, and invokes the appropriate function based on the
    selected mode. It serves as the primary interface for users to interact with E2EEFTP
    from the command line.

    The function supports the following modes:
    - server: Starts an E2EEFTP server
    - client: Starts an E2EEFTP client CLI

    Both modes accept --host and --port arguments with sensible defaults.
    """
    parser = argparse.ArgumentParser(description="E2EEFTP - End-to-End Encrypted FTP")
    subparsers = parser.add_subparsers(dest="mode", help="Mode of operation")

    # Server mode
    server_parser = subparsers.add_parser("server", help="Run in server mode")
    server_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server (default: localhost)")
    server_parser.add_argument("--port", type=int, default=2121, help="Port to bind the server (default: 2121)")

    # Client mode
    client_parser = subparsers.add_parser("client", help="Run in client mode")
    client_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to connect to (default: localhost)")
    client_parser.add_argument("--port", type=int, default=2121, help="Port to connect to (default: 2121)")

    args = parser.parse_args()

    if args.mode == "server":
        server(args.host, args.port)
    elif args.mode == "client":
        client_cli(args.host, args.port)

if __name__ == "__main__":
    cli()
