import socket
import json
import threading


class Receiver:
    def __init__(self, port=10001): # port是UDP监听端口号，默认10001
        self._data = {} # 存储接收到的数据，格式为 {nano_id: 数据字典}，比如 {"15": {"offset_ratio": -0.155, ...}}
        self._lock = threading.Lock() # 线程锁，用于保护_data字典的读写安全（防止后台线程写的同时主线程读导致数据冲突）
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 创建UDP套接字（AF_INET=IPv4，SOCK_DGRAM=UDP无连接模式）
        self._sock.bind(("0.0.0.0", port)) # 绑定到所有网卡接口的指定端口上，开始监听来自Nano的UDP数据包
        # 创建一个后台线程来持续监听UDP数据（因为recvfrom是阻塞调用，会卡住当前线程）
        self._thread = threading.Thread(target=self._listen, daemon=True) # target指定线程要执行的函数是self._listen；daemon=True表示守护线程（主程序退出时自动结束）
        self._thread.start() # 立即启动后台线程，_listen开始运行

    def _listen(self): # 后台监听函数，在独立线程中无限循环执行
        while True: # 永远循环，不停接收数据
            try:
                raw, _ = self._sock.recvfrom(4096) # 阻塞等待接收UDP数据包，4096是最大接收字节数；返回(raw_bytes, sender_address)，sender_address这里不需要所以用_忽略
                info = json.loads(raw.decode()) # 把收到的字节流decode成字符串，再用json.loads解析成Python字典
                with self._lock: # 加锁，确保写_data的时候主线程不会同时读取（防止竞态条件）
                    self._data[info.get("nano_id", "?")] = info # 以nano_id为key存储数据，如果JSON里没有nano_id字段就用"?"代替
            except Exception: pass # 如果收到损坏的数据或解码失败，跳过继续等下一条（不崩溃）

    def get(self, nano_id=None): # 主线程调用的取数据函数，nano_id是指定要取哪个Nano的数据（可选）
        with self._lock: # 加锁，确保读_data的时候后台线程不会同时写入
            if nano_id is not None: # 如果指定了nano_id
                return self._data.get(nano_id, {}) # 只返回该nano的最新数据字典，如果没有则返回空字典{}
            return dict(self._data) # 没有指定则返回全部数据的副本（dict()创建浅拷贝，防止外部修改影响内部数据）
