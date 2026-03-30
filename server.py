from e2eeftp import e2eeftp
from e2eeftp.auth.key import generate_keys


if __name__ == "__main__":
    server = e2eeftp()
    generate_keys()
    server.run()