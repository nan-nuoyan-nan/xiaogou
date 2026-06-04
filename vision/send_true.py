import socket
import json
import time
import random

TARGET = ("192.168.12.1", 10001) # UDP目标地址：树莓派IP和端口号

_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 创建UDP套接字

def send(data: dict): # 发送函数，参数data是一个字典（包含nano_id、dev_id、offset_ratio等信息）
    _sock.sendto(json.dumps(data).encode(), TARGET) # json.dumps把字典转成JSON字符串，.encode()转成bytes字节流，sendto通过UDP发送到TARGET地址

if __name__ == '__main__':
    # 测试模式：发送10条模拟数据到树莓派
    for i in range(10):
        data = {
            "nano_id": "15",
            "dev_id": "0",
            "has_line": True,
            "offset_ratio": round(random.uniform(-0.2, 0.2), 3),
            "msg": f"test_{i}"
        }
        send(data)
        print(f"[发送] {data}")
        time.sleep(0.5)
    print("发送完成!")
