"""
This modudle contains all the command handlers for the secure file transfer server.
"""
from logging import Logger
import os


__all__ = ["HList", "Send", "Get", "List", "Delete", "get_hlist", "eval_command"]


class HList:
    """
    The base class for all commands, used to identify the command type in a structured way.

    Args:
        __hlist__ (str): A string identifier for the command type, used for dispatching.
    """
    __hlist__: str

    def __init__(self, request, log: Logger): 
        """
        Args:
            request: The socket request object for the current client connection.
            log (Logger): A logger instance for logging command execution details.  
        """
        self.request = request
        self.log: Logger = log

    def __script__(self): 
        """ 
        A placeholder method that can be implemented by subclasses to define the command's behavior. 

        This method is intended to be overridden by subclasses to provide specific functionality for each command type.
        """


class Send(HList):
    __hlist__ = "SEND"

    def __init__(self, filename: str, filesize: int, cipher, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.filesize = filesize
        self.cipher = cipher

    def __script__(self):
        """
        The script method for the SEND command, which would contain the logic to handle file uploads from the client. 

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

        **Responses**:
        - On success: `b"226|Transfer Complete\\n"`
        - On decryption failure: `b"500|Decryption Failed\\n"`
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
            self.log.info(f"Stored: {write_path}")
        except Exception as e:
            self.log.error(f"Decryption failed for {self.filename}: {e}")
            self.request.sendall(b"500|Decryption Failed\n")
        
class Get(HList):
    __hlist__ = "GET"

    def __init__(self, filename: str, cipher, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.cipher = cipher

    def __script__(self):
        """
        The script method for the GET command, which would contain the logic to handle file requests from the client.

        This method is a placeholder and should be implemented with the actual logic to read a file from the server,
        encrypt it, and send it back to the client.

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

class List(HList):
    __hlist__ = "LIST"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __script__(self):
        """
        The script method for the LIST command, which would contain the logic to handle file listing requests from the client.

        This method is a placeholder and should be implemented with the actual logic to list files in the 'received' directory.

        Sends a list of available files in the 'received' directory to the client.

        The server responds with a header `200|<content_length>` followed by a
        newline-separated string of filenames.

        **Protocol**:
        1.  Sends header: `b"200|<size>"`
        2.  Sends body: A string of filenames.
        """
        self.log.info("Sending file list...")
        files = os.listdir("received")
        file_list = "\n".join(files)
        self.request.sendall(f"200|{len(file_list)}\n".encode())
        self.request.sendall(file_list.encode())

class Delete(HList):
    __hlist__ = "DELETE"

    def __init__(self, filename: str, **kwargs):
        super().__init__(**kwargs)
        self.filename = filename

    def __script__(self):
        """
        The script method for the DELETE command, which would contain the logic to handle file deletion requests from the client.

        This method is a placeholder and should be implemented with the actual logic to delete a file from the server's 'received' directory.

        Deletes a specified file from the server's 'received' directory.

        Args:
            filename (str): The name of the file to delete.

        **Responses**:
        - On success: `b"200|File deleted\\n"`
        - If file not found: `b"404|File not found\\n"`
        """
        self.filepath = os.path.join("received", self.filename)
        if os.path.exists(self.filepath):
            self.log.info(f"Deleting file: {self.filename}")
            os.remove(self.filepath)
            self.request.sendall(b"200|File deleted\n")
        else:
            self.request.sendall(b"404|File not found\n")

def get_hlist(command: HList): 
    """
    Returns the `__hlist__` value for the given command.
    """
    return command.__hlist__

def eval_command(command: HList):
    """
    Evaluates the command by calling its `__script__` method.
    """
    command.__script__()
