@echo off
chcp 65001
echo 正在激活虚拟环境...
call .\venv\Scripts\activate.bat

echo 正在安装依赖...
pip install -r requirements.txt

echo 正在打包应用...
pyinstaller --noconfirm --onefile --windowed --name "场景管理器" scene_manager.py

echo 正在复制数据文件...
copy scenes.json dist\

echo 打包完成！
pause
