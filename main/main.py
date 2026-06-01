import sys
import time
import os
cur = os.path.dirname(os.path.abspath(__file__))
lib = os.path.join(cur, '../lib/python/arm64')
run_dir = os.path.join(cur, '../run')

sys.path.append(lib)
sys.path.append(run_dir)
import robot_interface as sdk
from move_turn import move_turn, leap

class Main:
    def __init__(self):
        pass
    
    def action(self):
        HIGHLEVEL = 0xee
        udp = sdk.UDP(HIGHLEVEL, 8080, "192.168.123.161", 8082)
        cmd = sdk.HighCmd()    
        dog = sdk.HighState()  
        udp.InitCmdData(cmd)   
                               
        will_run = {}          # 外部注入 {'run': 'move'/'turn'/'move_turn', 'state': {...}}
        start_tick = 0         # 当前动作开始的时刻（tick），0=无动作
        motiontime = 0         # 全局计时器，每2ms+1，相当于500Hz的帧计数
        while True:            
            time.sleep(0.002)  
            motiontime += 1     
            udp.Recv()        
            udp.GetRecv(dog)

            cmd.mode = 1               # 1:强制站立（比赛全程不趴下）
            cmd.gaitType = 0         # 0:默认步态  1:trot小跑  2:walk走步
            cmd.speedLevel = 0       # 速度档位 0:默认
            cmd.footRaiseHeight = 0  # 抬脚高度 越大腿抬越高
            cmd.bodyHeight = 0       # 身体高度偏移 正数变高 负数压低
            cmd.euler = [0, 0, 0]    # 身体姿态 [roll横滚, pitch俯仰, yaw偏航]
            cmd.velocity = [0, 0]    # 水平速度 [前后, 左右] 范围-1.0~1.0
            cmd.yawSpeed = 0.0       # 旋转速度 正=逆时针 负=顺时针
            cmd.reserve = 0          # 保留字段
                            
            run = will_run.get('run', False)       # 动作类型 'move'/'turn'/'move_turn'/'leap'
            state = will_run.get('state', {})      # 动作参数
            if run and state:
                if start_tick == 0:                # 新动作第一帧，记录起始时间
                    start_tick = motiontime
                
                # 根据 run 类型分发到不同的执行函数
                if run == 'leap':
                    leap(cmd, state)
                else:
                    move_turn(cmd, state, run)
                
                t = state.get('t', 0)              # 动作持续时间（秒）
                if t > 0 and motiontime - start_tick >= int(t * 500):  # t秒到
                    will_run.clear()               # 动作结束，回到默认站立
                    start_tick = 0
            else:
                start_tick = 0                     # 无动作时归零

            udp.SetSend(cmd)
            udp.Send()






if __name__ == '__main__':
    main = Main()
    main.action()
    