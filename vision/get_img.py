import sys
import os
import cv2

CAMERAS = {
    1: ("192.168.123.13", 9001),
    2: ("192.168.123.13", 9002),
    3: ("192.168.123.14", 9003),
    4: ("192.168.123.14", 9004),
    5: ("192.168.123.15", 9005),
}


def capture(cam_id=5, save_dir="frames"):
    ip, port = CAMERAS.get(cam_id, (None, None))
    if not (ip and port):
        print(f"无效的摄像头编号: {cam_id}")
        return

    os.makedirs(save_dir, exist_ok=True)
    count = 0
    pipe = None
    cap = None

    while True:
        if cap is None:
            pipe = (
                f"udpsrc address={ip} port={port} "
                "! application/x-rtp,media=video,encoding-name=H264 "
                "! rtph264depay ! h264parse ! avdec_h264 "
                "! videoconvert "
                "! appsink drop=true max-buffers=1 sync=false"
            )
            cap = cv2.VideoCapture(pipe, cv2.CAP_GSTREAMER)
            if not cap.isOpened():
                print("打开UDP流失败，1秒后重试...")
                cap = None
                continue

        ret, frame = cap.read()
        if ret and frame is not None and frame.shape[0] > 100:
            filename = os.path.join(save_dir, f"{count:07d}.jpg")
            cv2.imwrite(filename, frame)
            count += 1
        else:
            cap.release()
            cap = None


if __name__ == '__main__':
    cam_id = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    save_dir = sys.argv[2] if len(sys.argv) > 2 else "frames"
    capture(cam_id, save_dir)
