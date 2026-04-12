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

- Added `e2eeftp.server.server.E2EEFTPRequestHandler.update_command_handlers()` to update the `e2eeftp.server.server.E2EEFTPRequestHandler.command_handlers: dict[str, str]` each time the server is initialized. **(tag: feature)**
