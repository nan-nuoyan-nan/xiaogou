import socket
import json

TARGET = ("192.168.123.161", 10001)

_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send(data: dict):
    _sock.sendto(json.dumps(data).encode(), TARGET)
