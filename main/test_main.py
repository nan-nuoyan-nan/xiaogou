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
    print(f"  [SSH输出] {result.stdout.strip()}")
    if result.stderr.strip():
        print(f"  [SSH错误] {result.stderr.strip()}")
    return result


def main():
    nano_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.123.15"
    dev_id = sys.argv[2] if len(sys.argv) > 2 else "0"

    print(f"[树莓派] 启动接收器 :10001")
    recv = Receiver(10001)

    ctrl = control()

    # 第1步: 阻塞式SSH到Nano杀进程（必须等杀完才能启动）
    print(f"[树莓派] SSH到 {nano_ip} 杀摄像头占用进程...")
    ssh_run(nano_ip, PWD,
        "ps -A | grep point | awk '{print $1}' | xargs -r kill -9; "
        "ps aux | grep mqttControlNode | grep -v grep | awk '{print $2}' | xargs -r kill -9; "
        "ps aux | grep live_human_pose | grep -v grep | awk '{print $2}' | xargs -r kill -9; "
        "ps aux | grep rosnode | grep -v grep | awk '{print $2}' | xargs -r kill -9; "
        "ps aux | grep python3 | grep vision | grep -v grep | awk '{print $2}' | xargs -r kill -9; "
        "echo KILL_DONE"
    )
    time.sleep(2)  # 等摄像头设备释放

    # 第2步: 启动vision_stream
    print(f"[树莓派] 启动 Nano 上的 vision_stream...")
    ctrl.activation([{
        "ip": nano_ip,
        "pwd": PWD,
        "script": f"~/xiaogou/vision/vision_stream.py {dev_id}"
    }])

    print(f"[树莓派] 等待 Nano {nano_ip} 发来数据...")
    time.sleep(5)

    try:
        count = 0
        while count < 10:
            data = recv.get()
            if data:
                for nid, info in data.items():
                    print(f"[接收] nano_id={nid} dev={info.get('dev_id')} "
                          f"offset={info.get('offset_ratio')} has_line={info.get('has_line')}")
                count += 1
            else:
                print("[等待] 暂无数据...")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        print("[树莓派] 停止Nano上的vision_stream...")
        ctrl.command([{
            "ip": nano_ip,
            "pwd": PWD,
            "cmd": "pkill -f vision_stream.py; pkill -f 'python3.*camera'"
        }])

    print("测试完成")


if __name__ == '__main__':
    main()
