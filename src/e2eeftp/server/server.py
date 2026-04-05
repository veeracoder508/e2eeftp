""" 
e2eeftp server using `socketserver` module.
"""
import socketserver
import logging
import os
import base64
from ..auth import E2EE, AESCipher
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from .commands import *
from rich.logging import RichHandler


rh = RichHandler()
# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s", # Rich handles the timestamp and level formatting
    datefmt="[%X]",
    handlers=[rh] # Shows cool traceback visuals on errors
)

log = logging.getLogger("rich")

class E2EEFTPRequestHandler(socketserver.BaseRequestHandler):
    """
    Request handler for each client connection, instantiated by the socketserver.

    This class manages the entire lifecycle of a client connection. It is
    responsible for performing the secure handshake, parsing client commands,
    and dispatching to the appropriate handler methods (e.g., for sending or
    receiving files).

    The command dispatch approach is intentionally flexible: subclasses can
    override `command_handlers` to add or modify supported commands without
    changing _handle_request logic.
    """

    command_handlers: dict[str, str] = {
        "SEND": "_receive_file",
        "GET": "_send_file",
        "LIST": "_send_list",
        "DELETE": "_delete_file",
        "HLIST": "_hlist"
    }

    req: dict[str, HList] = {}

    def handle(self):
        """
        The main entry point for handling a new client connection.

        This method orchestrates the session:
        1.  Performs the E2EE handshake to establish a secure channel.
        2.  Waits for and parses a command from the client.
        3.  Calls the internal method corresponding to the command.
        4.  Handles any exceptions during the session.
        5.  Ensures the connection is logged and closed cleanly.
        """
        address = self.client_address
        log.info(f"Accepted connection from {address}")
        try:
            server_key_path = "server_id.key"
            auth_keys_path = "authorized_clients.pub"

            log.info("Loading server identity and authorized keys...")
            
            if not os.path.exists(server_key_path):
                log.error(f"Server identity key '{server_key_path}' not found. Cannot secure connection.")
                return

            with open(server_key_path, "rb") as f:
                server_id_priv_key = serialization.load_pem_private_key(f.read(), password=None)
            
            authorized_client_keys = []
            if os.path.exists(auth_keys_path):
                with open(auth_keys_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                key_bytes = base64.b64decode(line)
                                authorized_client_keys.append(ed25519.Ed25519PublicKey.from_public_bytes(key_bytes))
                            except Exception as e:
                                log.warning(f"Skipping invalid key in {auth_keys_path}: {e}")
            else:
                log.warning(f"'{auth_keys_path}' not found. No clients will be authorized.")
                log.warning("Run 'generate_keys.py' to create client keys and the authorization file.")

            e2ee = E2EE()
            log.info(f"Performing secure handshake with {address}...")
            cipher = e2ee.server_handshake(self.request, server_id_priv_key, authorized_client_keys)
            log.info(f"Secure handshake with {address} complete.")
            self._handle_request(cipher)
        except FileNotFoundError as e:
            log.error(f"Identity key file not found: {e}. Please generate keys and authorize clients.")
        except ConnectionError as e:
            log.error(f"Handshake failed with {address}: {e}")
        except Exception as e:
            log.error(f"Error during session with {address}: {e}")
        finally:
            log.info(f"Connection with {address} closed.")

    def _recv_until(self, delimiter: bytes) -> bytes: 
        """ 
        Receives data from the socket until a specific delimiter is found. 

        This is a helper method to read data from the stream-based TCP socket 
        in a message-oriented way. It reads one byte at a time until the 
        `delimiter` is encountered.

        Args:
            delimiter (bytes): The byte sequence that marks the end of a message.

        Returns:
            bytes: The data received from the socket, including the delimiter.
                   Returns an empty bytestring if the client disconnects before
                   sending any data.
        """
        data = b''
        while not data.endswith(delimiter):
            chunk = self.request.recv(1)
            if not chunk: break
            data += chunk
        return data

    def _handle_request(self, cipher: AESCipher) -> None:
        """
        Parses the client's command and dispatches to the correct handler.

        Uses a dispatch map so subclasses can modify/add commands by overriding
        `command_handlers`.
        """
        header_data = self._recv_until(b'\n')
        if not header_data:
            return

        try:
            parts = header_data.decode().strip().split("|")
            command = parts[0].upper()

            handler_name = self.command_handlers.get(command)
            if handler_name is None:
                self.request.sendall(b"400|Invalid Command\n")
                log.warning(f"Invalid command from {self.client_address}: {command}")
                return

            handler = getattr(self, handler_name, None)
            if not callable(handler):
                self.request.sendall(b"500|Server Misconfigured\n")
                log.error(f"Handler {handler_name} for command {command} not implemented")
                return

            handler(*self._arg_paser(parts, cipher)) 

        except (IndexError, ValueError) as e:
            log.error(f"Malformed request from {self.client_address}: {header_data.strip()!r} - {e}")
            self.request.sendall(b"400|Malformed request\n")

    def _arg_paser(self, request_parts: list[str], cipher: AESCipher) -> tuple:
        """_summary_

        Args:
            request_parts (list[str]): The list of parts from the client's command header in the form of a list.

        Returns:
            tuple: The arguments to be passed to the command handler method, based on the command type. The mapping is as follows:
        """
        cmd_args: tuple = ()
        command = request_parts[0].upper()
        if command == "SEND":
            cmd_args = [request_parts[1], int(request_parts[2]), cipher]
        elif command == "GET":
            cmd_args = [request_parts[1], cipher]
        elif command == "LIST" or command == "HLIST":
            cmd_args = []
        elif command == "DELETE":
            cmd_args = [request_parts[1]]
        return tuple(cmd_args) 

    def _hlist(self) -> None:
        """
        Sends a text file of all available commands that the server supports to the client.
        
        The server responds with a header `200|<content_length>` followed by a newline-separated string of commands.
        **Protocol**:
        1.  Sends header: `b"200|<size>"`
        2.  Sends body: A string of commands.
        """
        self.req["HLIST"] = Hlist(commands=list(self.command_handlers.keys()), request=self.request, log=log, )
        self.req["HLIST"].__hlist__ = self._hlist.__name__
        self.req["HLIST"].run()

    def _send_list(self) -> None:
        """
        Sends a list of available files in the 'received' directory to the client.

        The server responds with a header `200|<content_length>` followed by a
        newline-separated string of filenames.

        **Protocol**:
        1.  Sends header: `b"200|<size>"`
        2.  Sends body: A string of filenames.
        """
        self.req["LIST"] = List(request=self.request, log=log)
        self.req["LIST"].set_hlist(self._send_list.__name__)
        self.req["LIST"].run()

    def _delete_file(self, filename: str) -> None:
        """
        Deletes a specified file from the server's 'received' directory.

        Args:
            filename (str): The name of the file to delete.

        **Responses**:
        - On success: `b"200|File deleted\\n"`
        - If file not found: `b"404|File not found\\n"`
        """
        self.req["DELETE"] = Delete(filename=filename, request=self.request, log=log)
        self.req["DELETE"].set_hlist(self._delete_file.__name__)
        self.req["DELETE"].run()

    def _receive_file(self, filename: str, filesize: int, cipher: AESCipher) -> None:
        """
        Receives, decrypts, and saves a file sent by the client.

        This method reads a specified number of bytes (`filesize`) from the socket,
        which contains the encrypted file data. It then attempts to decrypt this
        data using the session's cipher and saves it to the `received` directory.

        Args:
            filename (str): The name to save the file as.
            filesize (int): The exact size of the incoming encrypted data buffer.
            cipher (AESCipher): The cipher instance for this session.

        **Responses**:
        - On success: `b"226|Transfer Complete\\n"`
        - On decryption failure: `b"500|Decryption Failed\\n"`
        """
        self.req["SEND"] = Send(filename=filename, filesize=filesize, cipher=cipher, request=self.request, log=log)
        self.req["SEND"].set_hlist(self._receive_file.__name__)
        self.req["SEND"].run()

    def _send_file(self, filename: str, cipher: AESCipher) -> None:
        """
        Encrypts and sends a requested file to the client.

        If the file exists in the 'received' directory, it is read, encrypted
        with the session cipher, and sent over the socket.

        Args:
            filename (str): The name of the file to send.
            cipher (AESCipher): The cipher instance for this session.

        **Protocol & Responses**:
        - If file found:
            1. Sends header: `b"200|<encrypted_size>\\n"`
            2. Sends body: The encrypted file data.
        - If file not found: `b"404|File not found: {filename}\\n"`
        - On server-side error: `b"500|Server Read Error\\n"`
        """
        self.req["GET"] = Get(filename=filename, cipher=cipher, request=self.request, log=log)
        self.req["GET"].set_hlist(self._send_file.__name__)
        self.req["GET"].run()


class e2eeftp(socketserver.ThreadingTCPServer):
    """
    A multi-threaded TCP server for secure file transfers.

    This server uses `socketserver.ThreadingTCPServer` to handle each incoming
    client connection in a separate thread. This allows for concurrent file
    transfer operations.

    Security is established on a per-connection basis using an Elliptic Curve
    Diffie-Hellman (ECDH) key exchange. This generates a unique, ephemeral
    session key for each client, providing forward secrecy. All file data
    transferred after the handshake is encrypted with this key.

    The server listens for commands like SEND, GET, LIST, and DELETE.

    Attributes:
        allow_reuse_address (bool): Allows the server to restart and bind to the
                                    same address quickly.
        host (str): The IP address the server is bound to.
        port (int): The port the server is listening on.

    Supported Status Codes:
        - 200: Success
        - 226: Transfer Complete
        - 400: Bad Request / Invalid Command
        - 404: File Not Found
        - 500: Internal Server Error (e.g., Decryption Failed)

    The header format is:
        - SEND: SEND|filename|encrypted_data
        - GET: GET|filename
        - LIST: LIST
        - DELETE: DELETE|filename
    """
    allow_reuse_address = True

    def __init__(self, host: str='127.0.0.1', port: int=5001, logging: bool=True) -> None:
        """
        Initializes the server and binds it to a host and port.

        Args:
            host (str): The network interface IP to bind to. Defaults to '127.0.0.1'
                        (localhost). Use '0.0.0.0' to listen on all interfaces.
            port (int): The port number to listen on. Defaults to 5001.
            enable_logging (bool): If False, disables server logging output.
        """
        super().__init__((host, port), E2EEFTPRequestHandler)
        self.host, self.port = host, port
        self.enable_logging = logging
        log.disabled = not self.enable_logging

    def _generate_server_keys_if_missing(self) -> None:
        """
        Generates and saves server key pair if it doesn't exist.
        """
        server_key_path = "server_id.key"
        if not os.path.exists(server_key_path):
            log.warning(f"Server identity key '{server_key_path}' not found. Generating a new one.")

            server_priv_key = ed25519.Ed25519PrivateKey.generate()
            server_pub_key = server_priv_key.public_key()

            # Save server private key in PEM format
            with open(server_key_path, "wb") as f:
                f.write(server_priv_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            log.info(f"Saved '{server_key_path}' (private). This is your server's permanent identity.")

            # Save server public key in PEM format (for client's known_server.pub)
            with open("known_server.pub", "wb") as f:
                f.write(server_pub_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            log.info("Saved 'known_server.pub' (public). Copy this file to your client's directory.")
            log.warning("You must still generate client keys and add their public keys to 'authorized_clients.pub' for them to connect.")

    def run(self) -> None:
        """
        Starts the server's main loop to listen for and handle connections.

        This method calls `serve_forever()`, which blocks and waits for incoming
        connections. Each connection is then passed to an instance of
        `E2EEFTPRequestHandler` for processing in a new thread.
        """
        self._generate_server_keys_if_missing()
        log.info(f"host: {self.host}, port: {self.port}")
        log.info("press ctrl+c to exit")
        log.info(f"Server listening on {self.host}:{self.port}")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            log.warning("Shutting down...")
        finally:
            self.server_close()
