import cv2
import numpy as np
import subprocess

CROP = (110, 30, 410, 330)


def kill_camera_processes():
    cmds = [
        "ps -A | grep point | awk '{print $1}' | xargs -r kill -9",
        "ps -aux | grep mqttControlNode | grep -v grep | awk '{print $2}' | xargs -r kill -9",
        "ps -aux | grep live_human_pose | grep -v grep | awk '{print $2}' | xargs -r kill -9",
        "ps -aux | grep rosnode | grep -v grep | awk '{print $2}' | xargs -r kill -9",
    ]
    for cmd in cmds:
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _process(frame):
    h, w = frame.shape[:2]
    cl, ct, cr, cb = CROP
    roi = frame[ct:cb, cl:cr]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {"has_line": False, "offset_ratio": 0, "cx_px": 0}
    largest = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return {"has_line": False, "offset_ratio": 0, "cx_px": 0}
    cx = M["m10"] / M["m00"] + cl
    return {"has_line": True, "offset_ratio": round((cx - w / 2) / (w / 2), 3), "cx_px": int(cx)}


def stream(dev_ids=[0]):
    if isinstance(dev_ids, int):
        dev_ids = [dev_ids]
    caps = {did: cv2.VideoCapture(did, cv2.CAP_V4L2) for did in dev_ids}
    caps = {k: v for k, v in caps.items() if v.isOpened()}
    if not caps:
        return
    try:
        while True:
            for did, cap in caps.items():
                ret, frame = cap.read()
                if ret and frame is not None:
                    yield (did, _process(frame))
    finally:
        for cap in caps.values():
            cap.release()
