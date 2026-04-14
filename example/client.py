"""
This script is an example client for the secure file transfer server.

It demonstrates how to use the Client class from the pyproto package to
send one file ("README.md") and request another ("main.py").
"""
from e2eeftp import e2eeftpClient


def main() -> None:
    """
    Demonstrate basic E2EEFTP client operations.

    This function shows how to use the e2eeftpClient in a programmatic way
    to perform file transfer operations. It uploads a test image file,
    downloads another file, and lists the server's directory contents.

    The client is used as a context manager to ensure proper connection
    handling and cleanup.
    """
    with e2eeftpClient() as client:
        # Testing send request
        client.send("test_mini-veera.jpg")

        # Testing get request
        client.get('mini-veera.jpg')

        # Testing list request
        print(client.list_files())

        # Testing hlist request
        print(client.hlist())


if __name__ == "__main__":
    main()
