from e2eeftp import e2eeftpClient
from time import sleep


def main():
    client = e2eeftpClient()
    
    while True:
        try:
            client.list()
            sleep(5)
        except KeyboardInterrupt:
            print("Exiting...")
            break


if __name__ == "__main__":
    main()
