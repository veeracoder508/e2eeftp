# CHANGELOG
version: 0.0.0b4

type: beta

*****

- Changed file structure. **(tag: struct)**
    ```
    src\
    ├── benchmarker\ 
    │   ├── __init__.py
    │   └── bm.py
    │
    └── e2eeftp\
        ├── auth\
        │   ├── __init__.py
        │   ├── e2ee.py
        │   └── key.py
        ├── client\
        │   ├── __init__.py
        │   ├── __main__.py
        │   ├── cli.py
        │   └── client.py
        ├── server\
        │   ├── __init__.py
        │   ├── commands.py
        │   └── server.py
        ├── __init__.py
        └── cli.py
    ```
    * Made the benchmarker a separate module.

- Renamed the command base class from `HList` to `Comm`. **(tag: name_scheme)**

- Added `method:e2eeftp.server.server.E2EEFTPRequestHandler.update_command_handlers() -> None` to update the `e2eeftp.server.server.E2EEFTPRequestHandler.command_handlers: dict[str, str]` each time the client sends an request. **(tag: feature)**

- Changed `class:e2eeftp.client.client.e2eeftpClient` to also work with `with..as` statement. **(tag: feature_change)**
    ```python
    # syntax: 
    from e2eeftp import e2eeftpClient
    
    with e2eeftpClient(host='127.0.0.1', port=8080) as client:
        client.send("file.jpg")    # Testing send request
        client.get('file.jpg')     # Testing get request
        print(client.list_files()) # Testing list request
        print(client.hlist())      # Testing hlist request
    ```

- Added `method:e2eeftp.server.server.E2EEFTPRequestHandler.setup() -> None` to run the setup script `method:e2eeftp.server.server.E2EEFTPRequestHandler.update_command_handlers() -> None`. **(tag: feature)**

- Added docstrings:
    * `example._server.py`
    * `example.client_cli.py`
    * `example.client.py`
    * `example.server.py`
    * `src.benchmarker.__init__.py`
    * `src.benchmarker.__init__.py`
    * `src.auth.e2ee.py`