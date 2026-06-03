#!/bin/bash
# Nano 上的启动脚本：杀旧进程 → 启动sender
pkill -f sender.py
pkill -f 'python3.*vision'
ps -A | grep point | awk '{print $1}' | xargs -r kill -9
sleep 1
cd ~/xiaogou/test
exec python3 sender.py
