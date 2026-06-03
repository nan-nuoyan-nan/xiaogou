"""树莓派 接收端 - 启动接收器 + SSH启动Nano发送"""
import sys, os, time, subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), '../socket'))
from receiver import Receiver

NANO_IP = "192.168.123.15"
PWD = "123"

# 1. 启动接收器
print("[树莓派] 启动接收器 :10001")
recv = Receiver(10001)

# 2. 先传启动脚本到Nano，再用ssh -f后台运行
print(f"[树莓派] 传启动脚本到 {NANO_IP}...")
subprocess.run([
    "sshpass", "-p", PWD,
    "scp", "-o", "StrictHostKeyChecking=no",
    os.path.join(os.path.dirname(__file__), 'run_sender.sh'),
    f"unitree@{NANO_IP}:~/xiaogou/test/"
], capture_output=True, timeout=15)

print(f"[树莓派] SSH到 {NANO_IP} 杀进程并启动sender...")
subprocess.run([
    "sshpass", "-p", PWD,
    "ssh", "-f", "-o", "StrictHostKeyChecking=no",
    f"unitree@{NANO_IP}",
    "bash ~/xiaogou/test/run_sender.sh"
], capture_output=True, timeout=15)
print("  [SSH] sender已后台启动")

time.sleep(2)
print("[树莓派] 开始接收...")

# 3. 接收数据
try:
    for _ in range(20):
        d = recv.get()
        if d:
            for n, i in d.items():
                print(f"[收到] nano={n} offset={i.get('offset_ratio')} msg={i.get('msg')}")
        else:
            print("[等待] ...")
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

# 4. 停止Nano上的sender
print("[树莓派] 停止sender...")
subprocess.run([
    "sshpass", "-p", PWD,
    "ssh", "-o", "StrictHostKeyChecking=no",
    f"unitree@{NANO_IP}",
    "pkill -f sender.py"
], capture_output=True, timeout=5)

print("测试完成!")
