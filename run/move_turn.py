



def move_turn(cmd, move_state, run):
    s = move_state
    cmd.mode = 2                                # 0:待机趴下 1:强制站立 2:连续行走（可走可转）
    cmd.euler = [0, 0, 0]                       # 身体姿态 [roll横滚, pitch俯仰, yaw偏航]
    cmd.bodyHeight = s.get('height', 0)          # 身体高度偏移 正数抬高 负数压低
    cmd.gaitType = s.get('gait', 0)              # 步态 0:默认 1:trot小跑 2:walk走步
    cmd.footRaiseHeight = s.get('foot', 0)       # 抬脚高度 值越大腿抬越高

    if run == 'move':
        cmd.velocity = [s.get('vx', 0), s.get('vy', 0)]   # 水平速度 [前后, 左右] 范围-1~1
        cmd.yawSpeed = 0                                   # 旋转速度 直行时为0
    elif run == 'turn':
        cmd.velocity = [0, 0]                              # 水平速度 原地转为0
        cmd.yawSpeed = s.get('wz', 0)                      # 旋转速度 正=逆时针 负=顺时针
    elif run == 'move_turn':
        cmd.velocity = [s.get('vx', 0), s.get('vy', 0)]   # 水平速度 弯道时边前进边转
        cmd.yawSpeed = s.get('wz', 0)                      # 旋转速度 和velocity同一帧发送






def leap(cmd, move_state):
    """
    跨栏/越障专用动作包 (开环盲跨)
    
    开放控制的参数 (move_state):
    - vx: 前进速度，建议慢速 (默认 0.15)
    - foot: 抬脚高度，必须大于障碍物高度 (默认 0.1)
    - height: 身体高度微调 (默认 0.03，防托底)
    """
    s = move_state
    
    cmd.mode = 2                                # 保持行走模式
    cmd.gaitType = 2                            # 强制切到走步(walk)，三腿支撑最稳
    
    # 核心跨越参数
    cmd.velocity = [s.get('vx', 0.15), 0]       # 强制直行，禁止侧移
    cmd.yawSpeed = 0                            # 强制禁止旋转
    
    # 姿态微调
    cmd.footRaiseHeight = s.get('foot', 0.1)    # 夸张的高抬腿
    cmd.bodyHeight = s.get('height', 0.03)      # 身体微抬，防止肚子蹭到栏杆
    cmd.euler = [0, -0.05, 0]                   # 微微抬头(pitch=-0.05)，重心后移，方便前腿跨越













