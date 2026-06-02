import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../socket'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../vision'))
from receiver import Receiver
from control import control

PWD = "123"


def main():
    nano_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.123.15"
    dev_id = sys.argv[2] if len(sys.argv) > 2 else "0"

    print(f"[树莓派] 启动接收器 :10001")
    recv = Receiver(10001)

    ctrl = control()
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

    print("测试完成")


if __name__ == '__main__':
    main()
