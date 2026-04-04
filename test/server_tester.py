from e2eeftp import e2eeftpClient
from time import sleep


client = e2eeftpClient()


while True:
    try:
        client.list()
        sleep(5)
    except KeyboardInterrupt:
        print("Exiting...")
        break
