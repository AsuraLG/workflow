@echo off
chcp 65001
echo 正在创建虚拟环境...
python -m venv venv

echo 正在激活虚拟环境...
call .\venv\Scripts\activate.bat

echo 正在安装依赖...
pip install -r requirements.txt

echo 设置完成！
echo 请使用 run.bat 来运行程序
pause
