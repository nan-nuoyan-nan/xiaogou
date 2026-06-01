import sys
import os
import cv2


def stream(dev_id=0, save_dir=None):
    cap = cv2.VideoCapture(dev_id)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        
    if not cap.isOpened():
        return
        
    count = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
                
            if save_dir:
                cv2.imwrite(os.path.join(save_dir, f"{count:07d}.jpg"), frame)
                count += 1
                
            yield frame
    finally:
        cap.release()


if __name__ == '__main__':
    dev_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    save_dir = sys.argv[2] if len(sys.argv) > 2 else "frames"
    stream(dev_id, save_dir)
