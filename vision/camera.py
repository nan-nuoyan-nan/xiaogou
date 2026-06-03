import os
import cv2
import numpy as np
import subprocess

CROP = (110, 30, 410, 330)


def kill_camera_processes():
    cmds = [
        # 1. 杀点云处理 
        "ps -A | grep point | awk '{print $1}' | xargs -r kill -9",
        # 2. 杀MQTT控制节点
        "ps -aux | grep mqttControlNode | grep -v grep | awk '{print $2}' | xargs -r kill -9",
        # 3. 杀人体姿态估计
        "ps -aux | grep live_human_pose | grep -v grep | awk '{print $2}' | xargs -r kill -9",
        # 4. 杀ROS节点
        "ps -aux | grep rosnode | grep -v grep | awk '{print $2}' | xargs -r kill -9",
        # 5. 杀vision_stream也就是之前残留的进程
        "ps aux | grep python3 | grep vision | grep -v grep | awk '{print $2}' | xargs -r kill -9",
    ]
    for cmd in cmds:
        subprocess.run(cmd, shell=True, 
        stdout=subprocess.PIPE, # 这里表示的是捕获命令的输出，这里我们不关心，都是不打印的
        stderr=subprocess.PIPE # 这里表示的是捕获命令的错误输出，这里我们不关心，都是不打印的
        )


def _process(frame):# 这里输入的是一个BGR图像
    h, w = frame.shape[:2] # 图像高度和宽度
    cl, ct, cr, cb = CROP # 裁剪区域
    roi = frame[ct:cb, cl:cr] # 裁剪区域
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) # 转换为灰度图像
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV) 
    # 二值化处理，如果灰度值大于50，就设为255，否则设为0（黑）
    # 这里的这个最后一个参数进行了反转，也就是本来大于50也就是亮的区域变成了0（黑），本来小于等于0也就是暗的区域变成了255（亮）
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 这里的这个findContours只可以识别非纯白的区域
    # 这里的第二个参数是RETR_EXTERNAL，表示只返回外部轮廓
    # 这里的第三个参数是CHAIN_APPROX_SIMPLE，表示只返回轮廓的边界点，也就是轮廓的外接矩形的四个顶点
    # 这里返回的第一个是所有的轮廓每一个轮廓是由4个点点表示的，第二个是轮廓之间的嵌套关系这个是我们不需要的
    if not contours:
        return {"has_line": False, "offset_ratio": 0, "cx_px": 0} # 没有检测到线，返回{"has_line": False, "offset_ratio": 0, "cx_px": 0}
    largest = max(contours, key=cv2.contourArea) # 找到面积最大的轮廓，key设置规则为轮廓的面积，找到面积最大的轮廓
    M = cv2.moments(largest) # 计算轮廓的矩，相当于计算均匀的质量物体的重心，它是一个字典第一个是轮廓的面积，第二个是轮廓的中心坐标x，第三个是轮廓的中心坐标y，第四个是轮廓的中心坐标z，第五个是轮廓的中心坐标w，第六个是轮廓的中心坐标h，第七个是轮廓的中心坐标v
    # M["m00"]是轮廓的面积，M["m10"]是轮廓的中心坐标x，M["m01"]是轮廓的中心坐标y，M["m11"]是轮廓的中心坐标z，M["m20"]是轮廓的中心坐标w，M["m02"]是轮廓的中心坐标h，M["m22"]是轮廓的中心坐标v
    if M["m00"] == 0: # 如果轮廓面积为0，说明没有检测到线
        return {"has_line": False, "offset_ratio": 0, "cx_px": 0}
    cx = M["m10"] / M["m00"] + cl # 计算轮廓的中心坐标x，加上裁剪区域的左边界cl,这里使用x的总的坐标除以轮廓的面积，得到轮廓的中心坐标x
    return {"has_line": True, "offset_ratio": round((cx - w / 2) / (w / 2), 3), "cx_px": int(cx)}
    

def _draw(frame, result):
    h, w = frame.shape[:2]
    cl, ct, cr, cb = CROP
    cv2.rectangle(frame, (cl, ct), (cr, cb), (255, 255, 0), 1) #蓝绿色的矩形框，沿边界线，粗细是1
    cv2.line(frame, (w // 2, 0), (w // 2, h), (0, 255, 0), 1) # 绿色的线，从中心到顶部
    if result["has_line"]: # 如果检测到线
        cx = result["cx_px"]
        cv2.line(frame, (cx, ct), (cx, cb), (0, 0, 255), 2) # 红色的线，从中心到顶部，粗细是2
        cv2.putText(frame, str(result["offset_ratio"]), (cx + 5, ct + 20), # 这里写在红线的右侧5像素，剪切框的上面20像素
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1) # 红色的字体，从中心到顶部，字体细是0.5，字体颜色是红色，字体粗细是1


def stream(dev_ids=[0], save_dir=None): # dev_ids是摄像头设备号列表，默认只开0号摄像头；save_dir是保存图片的目录，如果不传就不保存
    # 参数兼容处理：如果传入的是整数（比如stream(0)），自动转成列表[0]
    if isinstance(dev_ids, int):
        dev_ids = [dev_ids]
    # 如果指定了保存目录，就创建这个目录（exist_ok=True表示目录已存在不报错）
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    # 打开所有指定的摄像头，CAP_V4L2强制使用V4L2后端（跳过GStreamer，避免WARN警告）
    caps = {did: cv2.VideoCapture(did, cv2.CAP_V4L2) for did in dev_ids}
    # 过滤掉打开失败的摄像头（比如被占用或不存在），只保留成功打开的
    caps = {k: v for k, v in caps.items() if v.isOpened()}
    # 如果所有摄像头都打不开，直接返回空（yield不会执行任何东西）
    if not caps:
        return
    # 设置每个摄像头的缓冲区大小为1帧（默认可能有好几帧缓冲，会导致图像延迟）
    for cap in caps.values():
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    count = 0 # 图片计数器，用于生成文件名 00000.jpg, 00001.jpg ...
    try:
        while True: # 无限循环，持续采集每一帧
            for did, cap in caps.items(): # 遍历所有摄像头（支持多摄像头同时采集）
                ret, frame = cap.read() # 读取一帧图像，ret表示是否成功(True/False)，frame是图像数据(BGR格式)
                if ret and frame is not None: # 确保读取成功且图像不为空
                    result = _process(frame) # 调用_process进行黑线检测，返回包含offset_ratio等信息的字典
                    if save_dir: # 如果需要保存图片
                        _draw(frame, result) # 在原图上画标注线（裁剪框、中线、检测线、数值）
                        cv2.imwrite(os.path.join(save_dir, f"{count:05d}.jpg"), frame) # 保存为5位数字编号的jpg文件
                        count += 1 # 计数器+1
                    yield (did, result) # yield返回(设备号, 检测结果)，这是一个生成器，每次yield一个值给调用者
    finally: # 无论正常结束还是break/异常退出，都会执行这里的清理代码
        for cap in caps.values():
            cap.release() # 释放摄像头资源（不释放的话/dev/video*会被一直占用）
