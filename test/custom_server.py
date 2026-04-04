"""
This script runs the secure file transfer server.

It instantiates and starts the Server from the pyproto package, which listens
for incoming client connections.
"""
from e2eeftp.server.server import E2EEFTPRequestHandler, e2eeftp
from e2eeftp.auth.e2ee import AESCipher
import os
import logging
import socketserver


# It's good practice to use the same logger as the base class
log = logging.getLogger(__name__)

class CustomE2EERequestHandler(E2EEFTPRequestHandler):
    """
    An extended request handler that adds support for RENAME and STAT commands.
    """

    def _arg_paser(self, request_parts, cipher):
        super()._arg_paser(request_parts, cipher)
        # For custamizing your server, you can modify this methos to parse the command header and return the appropriate arguments for your custom commands.
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
        elif command == "RENAME":
            cmd_args = [request_parts[1], request_parts[2]]
        elif command == "STAT":
            cmd_args = [request_parts[1]]
        return tuple(cmd_args) 

    def _rename_file(self, old_filename: str, new_filename: str) -> None:
        """
        Renames a file in the 'received' directory.

        Args:
            old_filename (str): The current name of the file.
            new_filename (str): The new name for the file.

        **Responses**:
        - On success: `b"200|File renamed successfully\\n"`
        - If old file not found: `b"404|Source file not found\\n"`
        - If new file name already exists: `b"409|Destination file already exists\\n"` (409 Conflict)
        - On other errors: `b"500|Rename failed\\n"`
        """
        old_filepath = os.path.join("received", old_filename)
        new_filepath = os.path.join("received", new_filename)

        if not os.path.exists(old_filepath):
            log.warning(f"Rename failed: source file '{old_filename}' not found.")
            self.request.sendall(b"404|Source file not found\n")
            return
        
        if os.path.exists(new_filepath):
            log.warning(f"Rename failed: destination file '{new_filename}' already exists.")
            self.request.sendall(b"409|Destination file already exists\n")
            return

        try:
            log.info(f"Renaming '{old_filename}' to '{new_filename}'")
            os.rename(old_filepath, new_filepath)
            self.request.sendall(b"200|File renamed successfully\n")
        except OSError as e:
            log.error(f"Error renaming file: {e}")
            self.request.sendall(b"500|Rename failed\n")

    def _get_file_stats(self, filename: str) -> None:
        """
        Sends statistics (size, modification time) for a specified file.

        Args:
            filename (str): The name of the file to get stats for.

        **Protocol & Responses**:
        - If file found: `b"200|<filesize>|<mod_time>\\n"`
        - If file not found: `b"404|File not found\\n"`
        """
        filepath = os.path.join("received", filename)
        if not os.path.exists(filepath):
            log.warning(f"Stat request for non-existent file: {filename}")
            self.request.sendall(b"404|File not found\n")
            return
        
        try:
            stats = os.stat(filepath)
            response = f"200|{stats.st_size}|{int(stats.st_mtime)}\n"
            log.info(f"Sending stats for {filename}: {stats.st_size} bytes, modified at {int(stats.st_mtime)}")
            self.request.sendall(response.encode())
        except OSError as e:
            log.error(f"Error getting stats for file {filename}: {e}")
            self.request.sendall(b"500|Could not retrieve file stats\n")

    # Inherits flexible dispatch from E2EEFTPRequestHandler.
    # This subclass only overrides command implementations (RENAME, STAT) and
    # does not need to reimplement low-level header parsing.

class CustomE2EEFTPServer(e2eeftp):
    def __init__(self, host: str='127.0.0.1', port: int=5001):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), CustomE2EERequestHandler)
        self.host, self.port = host, port

if __name__ == "__main__":
    server = CustomE2EEFTPServer()
    server.run()