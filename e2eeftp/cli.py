import argparse
from .server import e2eeftp
from .client.cli import e2eeftpClientCli


def client_cli(host: str, port: int):
    server = e2eeftpClientCli(host, port)
    server.run()

def server(host: str, port: int):
    server = e2eeftp(host, port)
    server.run()

def cli():
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