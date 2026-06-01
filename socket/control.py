
import subprocess


class control:
    def __init__(self):
        self.processes = []

    def ping(self, obj: list):
        for item in obj:
            ip = item.get("ip")
            pwd = item.get("pwd")
            if not (ip and pwd):
                continue
            try:
                result = subprocess.check_output([
                    "sshpass", "-p", pwd,
                    "ssh", "-o", "StrictHostKeyChecking=no",
                    f"unitree@{ip}", "hostname"
                ], timeout=5)
                print(f"{ip} 连通 -> {result.decode().strip()}")
            except Exception as e:
                print(f"{ip} 不通: {e}")

    def activation(self, obj: list):
        for item in obj:
            ip = item.get("ip")
            pwd = item.get("pwd")
            script = item.get("script")
            
            if not (ip and pwd and script):
                continue
                
            cmd_list = [
                "sshpass",
                "-p", pwd,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                f"unitree@{ip}",
                f"python3 {script}"
            ]
            
            p = subprocess.Popen(cmd_list)
            self.processes.append(p)
            print(f"已发送激活指令至: {ip} -> 运行 {script}")

    def kill(self, obj: list):
        for item in obj:
            ip = item.get("ip")
            pwd = item.get("pwd")
            if not (ip and pwd):
                continue

            cmd = "killall -9 point_cloud_node example_point 2>/dev/null"
            cmd_list = [
                "sshpass",
                "-p", pwd,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                f"unitree@{ip}",
                cmd
            ]
            p = subprocess.Popen(cmd_list)
            self.processes.append(p)
            print(f"已杀掉 {ip} 上的摄像头进程")

    def command(self, obj: list):
        for item in obj:
            ip = item.get("ip")
            pwd = item.get("pwd")
            cmd = item.get("cmd")

            if not (ip and pwd and cmd):
                continue

            cmd_list = [
                "sshpass",
                "-p", pwd,
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                f"unitree@{ip}",
                cmd
            ]

            p = subprocess.Popen(cmd_list)
            self.processes.append(p)
            print(f"已发送指令至: {ip} -> {cmd}")

    def scp(self, obj: list):
        for item in obj:
            src = item.get("src")
            ip = item.get("ip")
            pwd = item.get("pwd")
            dst = item.get("dst")

            if not (src and ip and pwd and dst):
                continue

            cmd_list = [
                "sshpass",
                "-p", pwd,
                "scp",
                "-o", "StrictHostKeyChecking=no",
                src,
                f"unitree@{ip}:{dst}"
            ]

            p = subprocess.Popen(cmd_list)
            self.processes.append(p)
            print(f"正在传输: {src} -> {ip}:{dst}")
