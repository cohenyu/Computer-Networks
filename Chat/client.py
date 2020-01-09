from socket import socket, AF_INET, SOCK_DGRAM
import sys


def main():
    # create the socket
    s = socket(AF_INET, SOCK_DGRAM)
    # get the ip and port
    dest_ip = sys.argv[1]
    dest_port = int(sys.argv[2])
    # get the massage from the client
    msg = raw_input()
    while not msg == 'quit':
        # send the massage to the server
        s.sendto(msg, (dest_ip, dest_port))
        # get the massage from the server
        data, sender_info = s.recvfrom(2048)
        # print the massage if the massage is not empty
        if data:
            print(data)
        msg = raw_input()
    s.close()


if __name__ == "__main__":
    main()