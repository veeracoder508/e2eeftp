"""
Command handlers for E2EEFTP server operations.

This module defines the command classes that handle various FTP operations
in the E2EEFTP server. Each command inherits from the base Comm class and
implements the __script__ method to perform specific operations like sending
files, receiving files, listing directories, deleting files, and providing
help information.

All commands work with encrypted data using the AESCipher for secure
communication between client and server.
"""

from logging import Logger
import os
from ..auth import AESCipher


__all__ = ["Comm", "Send", "Get", "List", "Delete", "Hlist"]


class Comm:
    """
    The base class for all commands, used to identify the command type in a structured way.

    Args:
        __hlist__ (str): A string identifier for the command type, used for dispatching.
    """
    __comm__: str

    def __init__(self, request, log: Logger, comm: str) -> None: 
        """
        Args:
            request: The socket request object for the current client connection.
            log (Logger): A logger instance for logging command execution details.  
        """
        self.request = request
        self.log: Logger = log
        self.set_comm(comm)
        self.run()

    def __script__(self) -> None: 
        """ 
        A placeholder method that can be implemented by subclasses to define the command's behavior. 

        This method is intended to be overridden by subclasses to provide specific functionality for each command type.
        """

    def run(self) -> None:
        """
        Executes the command by calling its `__script__` method. 

        This method serves as the entry point for executing the command's logic, allowing for any necessary setup or teardown to be handled in a consistent manner.
        """
        self.__script__()

    def set_comm(self, comm_value: str) -> None:
        """
        Sets the `__hlist__` value for this command instance.
        """
        self.__comm__ = comm_value

    def get_comm(self) -> str: 
        """Returns the `__hlist__` value for the given command.

        Returns:
            str: the method name of the function in the request handeler.
        """
        return self.__comm__


class StartSession(Comm): ...

class EndSession(Comm): ...

class Send(Comm):
    """
    This method is a placeholder and should be implemented with the actual logic to receive a file from the client, 
    save it to the server, and send an appropriate response back to the client. 

    Receives, decrypts, and saves a file sent by the client.

    This method reads a specified number of bytes (`filesize`) from the socket,
    which contains the encrypted file data. It then attempts to decrypt this
    data using the session's cipher and saves it to the `received` directory.

    Args:
        filename (str): The name to save the file as.
        filesize (int): The exact size of the incoming encrypted data buffer.
        cipher (AESCipher): The cipher instance for this session.

    **Command**:
    - Client sends: `SEND|<filename>|<filesize>`

    **Responses**:
    - On success: `b"226|Transfer Complete\\n"`
    - On decryption failure: `b"500|Decryption Failed\\n"`
    """
    def __init__(self, filename: str, filesize: int, cipher: AESCipher, **kwargs) -> None:
        """The initializer for the `SEND` method.

        Args:
            filename (str): The name to save the file as on the server.
            filesize (int): The exact size of the incoming encrypted data buffer, used to determine how many bytes to read from the socket.
            cipher (AESCipher): The cipher instance for this session, used to decrypt the received file data.
        """
        self.filename = filename
        self.filesize = filesize
        self.cipher = cipher
        super().__init__(**kwargs)

    def __script__(self):
        """
        Execute the SEND command to receive and decrypt a file from the client.

        This method reads the encrypted file data from the socket based on the
        specified filesize, decrypts it using the session cipher, and saves the
        decrypted file to the 'received' directory. It sends appropriate response
        codes back to the client indicating success or failure.

        The method handles partial reads by accumulating data until the full
        encrypted buffer is received. If decryption fails, an error response
        is sent and the operation is logged.
        """
        self.log.info(f"Receiving encrypted file: {self.filename} ({self.filesize} bytes)")
        received_dir = "received"
        os.makedirs(received_dir, exist_ok=True)
        write_path = os.path.join(received_dir, self.filename)
        encrypted_buffer = b""
        while len(encrypted_buffer) < self.filesize:
            chunk = self.request.recv(min(self.filesize - len(encrypted_buffer), 4096))
            if not chunk: break
            encrypted_buffer += chunk
        
        if len(encrypted_buffer) < self.filesize:
            self.log.error(f"File transfer incomplete for {self.filename}. Expected {self.filesize}, got {len(encrypted_buffer)}")
            return

        try:
            decrypted_data = self.cipher.decrypt(encrypted_buffer)
            with open(write_path, "wb") as f:
                f.write(decrypted_data)
            self.request.sendall(b"226|Transfer Complete\n") 
            self.log.info(f"226|Transfer Complete: {self.filename} {self.filesize} bytes")
        except Exception as e:
            self.log.error(f"Decryption failed for {self.filename}: {e}")
            self.request.sendall(b"500|Decryption Failed\n")
        
class Get(Comm):
    """
    This method is a placeholder and should be implemented with the actual logic to read a file from the server,
    encrypt it, and send it back to the client.

    Encrypts and sends a requested file to the client.

    If the file exists in the 'received' directory, it is read, encrypted
    with the session cipher, and sent over the socket.

    Args:
        filename (str): The name of the file to send.
        cipher (AESCipher): The cipher instance for this session.

    **Command**:
    - Client sends: `GET|<filename>`

    **Protocol & Responses**:
    - If file found:
        1. Sends header: `b"200|<encrypted_size>\\n"`
        2. Sends body: The encrypted file data.
    - If file not found: `b"404|File not found: {filename}\\n"`
    - On server-side error: `b"500|Server Read Error\\n"`
    """

    def __init__(self, filename: str, cipher: AESCipher, **kwargs):
        """the initializer for the `GET` method.

        Args:
            filename (str): The name of the file to send back to the client, used to locate the file in the server's 'received' directory.
            cipher (AESCipher): The cipher instance for this session, used to encrypt the file data before sending it to the client.
        """
        self.filename = filename
        self.cipher = cipher
        super().__init__(**kwargs)

    def __script__(self):
        """
        Execute the GET command to encrypt and send a file to the client.

        This method locates the requested file in the 'received' directory,
        reads its contents, encrypts it using the session cipher, and sends
        the encrypted data to the client. It first sends a header with the
        encrypted data size, followed by the encrypted file data.

        If the file does not exist, a 404 response is sent. If any error
        occurs during reading or encryption, a 500 error response is sent.
        """
        filepath = os.path.join("received", self.filename)
        if not os.path.exists(filepath):
            self.log.warning(f"Client requested non-existent file: {self.filename}")
            self.request.sendall(f"404|File not found: {self.filename}\n".encode())
            return

        try:
            with open(filepath, "rb") as f:
                raw_data = f.read()
            
            encrypted_data = self.cipher.encrypt(raw_data)
            self.request.sendall(f"200|{len(encrypted_data)}\n".encode())
            
            self.request.sendall(encrypted_data)
            self.log.info(f"Sent: {self.filename}")
        except Exception as e:
            self.log.error(f"Error reading or sending file {self.filename}: {e}")
            self.request.sendall(b"500|Server Read Error\n")

class List(Comm):
    """
    This method is a placeholder and should be implemented with the actual logic to list files in the 'received' directory.

    Sends a list of available files in the 'received' directory to the client.

    The server responds with a header `200|<content_length>` followed by a
    newline-separated string of filenames.

    **Command**:
    - Client sends: `LIST`

    **Protocol**:
    1.  Sends header: `b"200|<size>"`
    2.  Sends body: A string of filenames.
    """

    def __init__(self, **kwargs):
        """the initializer for the `LIST` method.
        """
        super().__init__(**kwargs)

    def __script__(self):
        """
        Execute the LIST command to send a list of available files to the client.

        This method retrieves the list of files in the 'received' directory,
        formats them as a newline-separated string, and sends this list to
        the client. It first sends a header with the size of the file list
        string, followed by the actual list data.

        The response includes all files present in the received directory,
        allowing clients to see what files are available for download.
        """
        files = os.listdir("received")
        file_list = "\n".join(files)
        self.request.sendall(f"200|{len(file_list)}\n".encode())
        self.request.sendall(file_list.encode())
        self.log.info(f"200|Sent file list with {len(files)} entries")

class Delete(Comm):
    """
    This method is a placeholder and should be implemented with the actual logic to delete a file from the server's 'received' directory.

    Deletes a specified file from the server's 'received' directory.

    Args:
        filename (str): The name of the file to delete.

    **Command**:
    - Client sends: `DELETE|<filename>`

    **Responses**:
    - On success: `b"200|File deleted\\n"`
    - If file not found: `b"404|File not found\\n"`
    """

    def __init__(self, filename: str, **kwargs):
        """the initializer for the `DELETE` method.

        Args:
            filename (str): The name of the file to delete from the server's 'received' directory, used to locate and remove the file if it exists.
        """
        self.filename = filename
        super().__init__(**kwargs)

    def __script__(self):
        """
        Execute the DELETE command to remove a file from the server.

        This method attempts to delete the specified file from the 'received'
        directory. If the file exists, it is removed and a success response
        is sent to the client. If the file does not exist, a 404 error
        response is sent instead.

        The operation is logged with appropriate severity levels for
        monitoring and debugging.
        """
        self.filepath = os.path.join("received", self.filename)
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
            self.request.sendall(b"200|File deleted\n")
            self.log.info(f"200|Deleted file: {self.filename}")
        else:
            self.request.sendall(b"404|File not found\n")
            self.log.warning(f"404|File not found for deletion: {self.filename}")

class Hlist(Comm):
    """
    The script method for the Hlist command, which returns the list of supported
    commands as plain text.

    Responses:
    - On success: `200|<length>` `<list of commands>`
    """

    def __init__(self, commands: list[str], request, log: Logger, **kwargs):
        """the initializer for the `HLIST` method.

        Args:
            commands (list[str]): List of supported commands to return to the client.
            request: The socket request object for the current client connection.
            log (Logger): A logger instance for logging command execution details.
        """
        self.commands = commands
        super().__init__(request, log, **kwargs)

    def __script__(self):
        """
        Execute the HLIST command to send the list of supported commands to the client.

        This method formats the list of available commands as a newline-separated
        string, encodes it, and sends it to the client. It first sends a header
        with the size of the command list payload, followed by the actual list.

        This helps clients understand what operations are available on the server.
        """
        command_list = "\n".join(self.commands)
        payload = command_list.encode()
        self.request.sendall(f"200|{len(payload)}\n".encode())
        self.request.sendall(payload)
        self.log.info(f"200|Executed Hlist with {len(self.commands)} commands")
