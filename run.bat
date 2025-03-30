@echo off
chcp 65001
echo 正在激活虚拟环境...
call .\venv\Scripts\activate.bat

echo 正在运行程序...
python scene_manager.py

echo 程序已退出
pause
