import os
from benchmarker import BenchMark
from e2eeftp import e2eeftpClient


def main():
    client = e2eeftpClient()
    print("Benchmarking server with 1md playload...")

    # Calculate path relative to the script location to ensure the file is found
    payload_path = os.path.join(os.path.dirname(__file__), "playloads", "playload.txt")

    with BenchMark():
        client.send(payload_path)


if __name__ == "__main__":
    main()
