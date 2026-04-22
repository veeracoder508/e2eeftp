# CHANGELOG
version: 0.0.0

type: stable

total changes: 13

*****

- Fixed `AttributeError` in `Comm` subclasses by ensuring all instance attributes are assigned before calling the base class constructor. **(tag: fix)**

- Prevented state leakage between client sessions by moving `command_handlers` and `req` from class attributes to instance-specific attributes in `E2EEFTPRequestHandler`. **(tag: fix/security)**

- Fixed a typo in `_send_list` command registration that caused the server to incorrectly attempt a file transfer instead of a directory listing. **(tag: fix)**

- Corrected `match/case` syntax in `_arg_paser` to use the bitwise OR (`|`) for multiple patterns instead of a tuple-matching comma. **(tag: fix)**

- Fixed missing command registration in `custom_server.py` to ensure `RENAME` and `STAT` are correctly dispatched to their handlers. **(tag: fix)**

- Renamed: **(tag: rename)**
    * `e2eeftp.server.commands.Comm.__hlist__: str` >> `e2eeftp.server.commands.Comm.__comm__: str`
    * `e2eeftp.server.commands.Comm.set_hlist() -> None` >> `e2eeftp.server.commands.Comm.set_comm() -> None`
    * `e2eeftp.server.commands.Comm.get_hlist() -> str` >> `e2eeftp.server.commands.Comm.get_comm() -> str`

- Changes the arguments for `e2eeftp.server.commands.Comm`. **(tag: change)**
    ```python
    Comm(request, log: Logger)            # Old
    Comm(request, log: Logger, comm: str) # New
    ```

- Added `e2eeftp.server.commands.StartSession(Comm)` and `e2eeftp.server.commands.EndSession(Comm)`. **(tag: change)**

- Added `e2eeftp.client.client.e2eeftpClient.start_session(user_id: str)` and `e2eeftp.client.client.e2eeftpClient.end_session()`. **(tag: )**

- Added `e2eeftp.client.client.e2eeftpClient.__str__: str`. **(tag: feature)**

- Removed `e2eeftp.server.server.main()`. **(tag: removal)**

- Implemented automatic command registration for `E2EEFTPRequestHandler` subclasses using the `__init_subclass__` hook, allowing seamless inheritance and merging of command mappings. **(tag: feature)**

- Centralized application versioning by moving `__version__` to the root `__init__.py`, ensuring a single source of truth for the server and client components. **(tag: structure)**

- Enhanced the CLI `PING` command to perform a TCP connection check when a port is provided, providing a more accurate status for the service than standard ICMP pings. **(tag: feature)**