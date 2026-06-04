import sys
import os
import time
import subprocess
sys.path.append(os.path.join(os.path.dirname(__file__), '../socket'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../vision'))
from receiver import Receiver
from control import control

PWD = "123"


def ssh_run(ip, pwd, cmd):
    """阻塞式SSH执行，等远程命令完成后才返回"""
    result = subprocess.run([
        "sshpass", "-p", pwd,
        "ssh", "-o", "StrictHostKeyChecking=no",
        f"unitree@{ip}", cmd
    ], capture_output=True, text=True, timeout=15)
    return result


def main():
    nano_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.123.15"
    dev_id = sys.argv[2] if len(sys.argv) > 2 else "0"
    # 数据保存路径，默认保存在当前目录的data文件夹下
    save_dir = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(save_dir, exist_ok=True)
    # 生成带时间戳的文件名
    filename = os.path.join(save_dir, f"offset_{time.strftime('%Y%m%d_%H%M%S')}.txt")

    print(f"[树莓派] 启动接收器 :10001")
    recv = Receiver(10001)

    ctrl = control()

    # === 测试UDP通讯 ===
    print(f"[树莓派] 测试UDP通讯...")
    ctrl.activation([{
        "ip": nano_ip,
        "pwd": PWD,
        "script": f"~/xiaogou/vision/send_true.py"
    }])
    time.sleep(10)
    data = recv.get()
    if data:
        print(f"[树莓派] ✅ UDP链路正常")
    else:
        print(f"[树莓派] ❌ UDP不通，退出")
        return

    # 杀进程
    print(f"[树莓派] SSH到 {nano_ip} 杀摄像头占用进程...")
    ssh_run(nano_ip, PWD,
        "ps -A | grep point | awk '{print $1}' | xargs -r kill -9; "
        "ps aux | grep mqttControlNode | grep -v grep | awk '{print $2}' | xargs -r kill -9; "
        "ps aux | grep live_human_pose | grep -v grep | awk '{print $2}' | xargs -r kill -9; "
        "ps aux | grep rosnode | grep -v grep | awk '{print $2}' | xargs -r kill -9; "
        "ps aux | grep python3 | grep vision | grep -v grep | awk '{print $2}' | xargs -r kill -9; "
        "echo KILL_DONE"
    )
    time.sleep(2)

    # 启动vision_stream（阻塞式SSH + nohup确保进程不被SIGHUP杀死）
    print(f"[树莓派] 启动 Nano 上的 vision_stream...")
    ssh_run(nano_ip, PWD,
        f"nohup python3 ~/xiaogou/vision/vision_stream.py {dev_id} > /tmp/vision.log 2>&1 &"
    )

    print(f"[树莓派] 等待 Nano {nano_ip} 初始化...")
    time.sleep(8)

    # 打开文件准备写入
    print(f"[树莓派] 开始记录数据到 {filename}")
    print(f"[树莓派] 按 Ctrl+C 停止记录")
    with open(filename, "w") as f:
        f.write("timestamp,offset_ratio,has_line\n")  # 表头
        try:
            while True:
                data = recv.get()
                if data:
                    for nid, info in data.items():
                        ts = time.time()  # 精确时间戳（秒级小数）
                        offset = info.get("offset_ratio", 0)
                        has_line = info.get("has_line", False)
                        line = f"{ts:.6f},{offset},{has_line}\n"
                        f.write(line)
                        f.flush()  # 立即写入磁盘，防止缓冲丢失
                        print(f"[记录] ts={ts:.3f} offset={offset} has_line={has_line}")
                time.sleep(0.1)  # 100ms采样一次
        except KeyboardInterrupt:
            print("\n[树莓派] 记录停止")

    # 清理
    print("[树莓派] 停止Nano上的vision_stream...")
    ctrl.command([{
        "ip": nano_ip,
        "pwd": PWD,
        "cmd": "pkill -f vision_stream.py; pkill -f 'python3.*camera'; pkill -f send_true"
    }])

    print(f"[树莓派] 数据已保存到 {filename}")
    print("测试完成")


if __name__ == '__main__':
    main()
