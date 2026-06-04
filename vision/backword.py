import socket
import json

TARGET = ("192.168.12.1", 10001) # UDP目标地址：树莓派IP和端口号

_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 创建UDP套接字，AF_INET表示IPv4协议族，SOCK_DGRAM表示UDP（无连接、数据报模式）

def send(data: dict): # 发送函数，参数data是一个字典（包含nano_id、dev_id、offset_ratio等信息）
    _sock.sendto(json.dumps(data).encode(), TARGET) # json.dumps把字典转成JSON字符串，.encode()转成bytes字节流，sendto通过UDP发送到TARGET地址
