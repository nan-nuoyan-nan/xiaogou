"""Nano 15 发送端 - 简单UDP发送测试"""
import socket, json, time, random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
target = ("192.168.12.1", 10001)

count = 0
while True:
    data = {
        "nano_id": "15",
        "dev_id": "0",
        "has_line": True,
        "offset_ratio": round(random.uniform(-0.2, 0.2), 3),
        "msg": f"test_{count}"
    }
    sock.sendto(json.dumps(data).encode(), target)
    print(f"[发送] {data}")
    count += 1
    time.sleep(0.5)
