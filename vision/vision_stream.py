import subprocess
import camera
import backword


class vision_stream:
    def __init__(self): 
        try:
            ip = subprocess.check_output("hostname -I", shell=True).decode().strip()
            local_ip = next(i for i in ip.split() if i.startswith("192.168.123."))
            self.id = local_ip.split('.')[-1]
        except Exception:
            self.id = "0"

    def run(self, dev_ids):
        for did, result in camera.stream(dev_ids):
            result["nano_id"] = self.id
            result["dev_id"] = did
            backword.send(result)


if __name__ == '__main__':
    import sys
    vs = vision_stream()
    dev_ids = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [0]
    camera.kill_camera_processes()
    vs.run(dev_ids)
