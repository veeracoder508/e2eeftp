from benchmarker import BenchMark
from e2eeftp import e2eeftpClient


def main():
    client = e2eeftpClient()

    with BenchMark():
        client.send("playlod.txt")


if __name__ == "__main__":
    main()
