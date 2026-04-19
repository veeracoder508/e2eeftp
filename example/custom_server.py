"""
This script runs the secure file transfer server.

It instantiates and starts the Server from the pyproto package, which listens
for incoming client connections.
"""
from src.e2eeftp.server.server import E2EEFTPRequestHandler, e2eeftp
from src.e2eeftp.server.commands import Comm
from src.e2eeftp.auth.e2ee import AESCipher
import os
import logging
import socketserver


log = logging.getLogger(__name__)

class Rename(Comm):
    """
    Renames a file in the 'received' directory.

    **Responses**:
    - On success: `b"200|File renamed successfully\\n"`
    - If old file not found: `b"404|Source file not found\\n"`
    - If new file name already exists: `b"409|Destination file already exists\\n"` (409 Conflict)
    - On other errors: `b"500|Rename failed\\n"`
    """

    def __init__(self, old_filename: str, new_filename: str, **kwargs) -> None:
        """The initializer for the `RNAME` method.

        Args:
            old_filename (str): The current name of the file.
            new_filename (str): The new name for the file.
        """
        self.old_filename = old_filename
        self.new_filename = new_filename
        super().__init__(**kwargs)

    def __script__(self) -> None:
        """
        Execute the RENAME command to change a file's name on the server.

        This method renames a file in the 'received' directory from the old
        filename to the new filename. It checks for the existence of the source
        file and ensures the destination doesn't already exist before performing
        the rename operation.

        Appropriate status codes are sent back to the client indicating
        success or the type of failure encountered.
        """
        old_filepath = os.path.join("received", self.old_filename)
        new_filepath = os.path.join("received", self.new_filename)

        if not os.path.exists(old_filepath):
            log.warning(f"Rename failed: source file '{self.old_filename}' not found.")
            self.request.sendall(b"404|Source file not found\n")
            return
        
        if os.path.exists(new_filepath):
            log.warning(f"Rename failed: destination file '{self.new_filename}' already exists.")
            self.request.sendall(b"409|Destination file already exists\n")
            return

        try:
            log.info(f"Renaming '{self.old_filename}' to '{self.new_filename}'")
            os.rename(old_filepath, new_filepath)
            self.request.sendall(b"200|File renamed successfully\n")
        except OSError as e:
            log.error(f"Error renaming file: {e}")
            self.request.sendall(b"500|Rename failed\n")

class Stat(Comm): 
    """
    Sends statistics (size, modification time) for a specified file.

    **Protocol & Responses**:
    - If file found: `b"200|<filesize>|<mod_time>\\n"`
    - If file not found: `b"404|File not found\\n"`
    """

    def __init__(self, filename: str, **kwargs) -> None:
        """The initializer for the `STAT` method.

        Args:
            filename (str): The name of the file to get stats for.
        """
        self.filename = filename
        super().__init__(**kwargs)

    def __script__(self):
        """
        Execute the STAT command to retrieve file statistics.

        This method gets the size and modification time of a file in the
        'received' directory. It uses os.stat() to retrieve the file information
        and sends it back to the client in a formatted response.

        If the file doesn't exist, a 404 error is returned. If there's an
        error accessing the file, a 500 error is sent.
        """
        filepath = os.path.join("received", self.filename)
        if not os.path.exists(filepath):
            log.warning(f"Stat request for non-existent file: {self.filename}")
            self.request.sendall(b"404|File not found\n")
            return
        
        try:
            stats = os.stat(filepath)
            response = f"200|{stats.st_size}|{int(stats.st_mtime)}\n"
            log.info(f"Sending stats for {self.filename}: {stats.st_size} bytes, modified at {int(stats.st_mtime)}")
            self.request.sendall(response.encode())
        except OSError as e:
            log.error(f"Error getting stats for file {self.filename}: {e}")
            self.request.sendall(b"500|Could not retrieve file stats\n")

        

class CustomE2EERequestHandler(E2EEFTPRequestHandler):
    """
    An extended request handler that adds support for RENAME and STAT commands.
    """
    # Now we only need to define the new commands. 
    # The base class automatically merges these with the defaults.
    command_handlers = {
        "RENAME": "_rename_file",
        "STAT": "_get_file_stats"
    }

    def _arg_paser(self, request_parts, cipher) -> tuple:
        """
        Parse command arguments for both standard and custom commands.

        This method extends the parent's argument parsing to handle the
        additional RENAME and STAT commands. It extracts the appropriate
        arguments from the command parts based on the command type.

        Args:
            request_parts: List of command parts split from the client request.
            cipher: The encryption cipher for the session.

        Returns:
            tuple: Parsed arguments for the command handler.
        """
        # For custamizing your server, you can modify this methos to parse the command header and return the appropriate arguments for your custom commands.
        cmd_args: list = []
        command = request_parts[0].upper()

        match command:
            # File Commands
            case "SEND":
                cmd_args = [request_parts[1], int(request_parts[2]), cipher]
            case "GET":
                cmd_args = [request_parts[1], cipher]
            case "LIST" | "HLIST":
                cmd_args = []
            case "DELETE":
                cmd_args = [request_parts[1]]
            # Custom commands
            case "RENAME":
                cmd_args = [request_parts[1], request_parts[2]]
            case "STAT":
                cmd_args = [request_parts[1]]
        
        return tuple(cmd_args) 

    def _rename_file(self, old_filename: str, new_filename: str) -> None:
        """
        Handle the RENAME command by creating and executing a Rename command object.

        Args:
            old_filename (str): The current filename to rename.
            new_filename (str): The new filename.
        """
        self.req["RENAME"] = Rename(
            old_filename=old_filename, 
            new_filename=new_filename, 
            request=self.request, 
            log=log, 
            comm=self._rename_file.__name__
        )

    def _get_file_stats(self, filename: str) -> None:
        """
        Handle the STAT command by creating and executing a Stat command object.

        Args:
            filename (str): The name of the file to get statistics for.
        """
        self.req["STAT"] = Stat(
            filename=filename, 
            request=self.request, 
            log=log, 
            comm=self._get_file_stats.__name__
        )

    # Inherits flexible dispatch from E2EEFTPRequestHandler.
    # This subclass only overrides command implementations (RENAME, STAT) and
    # does not need to reimplement low-level header parsing.

class CustomE2EEFTPServer(e2eeftp):
    """
    Custom E2EEFTP server that uses the extended request handler with RENAME and STAT commands.

    This server class inherits from the base e2eeftp server but uses CustomE2EERequestHandler
    instead of the standard handler, enabling support for additional file operations.
    """
    def __init__(self, host: str='127.0.0.1', port: int=5001):
        super().__init__(host, port)
        # Explicitly set the request handler to our custom version
        self.RequestHandlerClass = CustomE2EERequestHandler
        self.prompt = "dev"


def main():
    server = CustomE2EEFTPServer()
    server.run()
    

if __name__ == "__main__":
    main()
