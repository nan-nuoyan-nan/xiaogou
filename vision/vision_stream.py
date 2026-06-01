"""
这个是整个视觉流的函数用来控制拍摄
以及图片分析以及数据的信息的回流
"""






import socket
import subprocess
import backword
import vision
class vision_stream:
    def __init__(self):
        import subprocess
        # 使用 shell 命令直接获取以 192.168.123 开头的 IP，并提取最后一位
        try:
            ip = subprocess.check_output("hostname -I", shell=True).decode().strip()
            # 从所有返回的IP中找到192.168.123网段的那个
            local_ip = next(i for i in ip.split() if i.startswith("192.168.123."))
            self.id = local_ip.split('.')[-1]
        except Exception:
            self.id = "0"  # 失败则默认0

    def run(self, stream: list):
        import get_frame
        # 使用生成器遍历，每次吐出一帧图像，同时保持摄像头不关闭
        for frame in get_frame.stream(stream[0], stream[1]):
            # 1. 传给视觉分析模块处理
            result = vision.process(frame)
            
            # 2. 将本机的 ID 塞入结果中
            result["nano_id"] = self.id
            
            # 3. 将结果通过 UDP 回传给树莓派
            backword.send(result)



















