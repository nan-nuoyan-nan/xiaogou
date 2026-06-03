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

    def run(self, dev_ids, save_dir=None):
        for did, result in camera.stream(dev_ids, save_dir=save_dir):
            result["nano_id"] = self.id
            result["dev_id"] = did
            backword.send(result)


if __name__ == '__main__':
    import sys
    vs = vision_stream()
    args = [a for a in sys.argv[1:] if not a.startswith("--save=")]
    dev_ids = [int(x) for x in args] if args else [0]
    save_arg = [a for a in sys.argv[1:] if a.startswith("--save=")]
    save_dir = save_arg[0].split("=")[1] if save_arg else None
    camera.kill_camera_processes()
    vs.run(dev_ids, save_dir=save_dir)
