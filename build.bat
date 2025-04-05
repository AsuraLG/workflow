@echo off
chcp 65001
echo 正在激活虚拟环境...
call .\venv\Scripts\activate.bat

echo 正在清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo 正在打包应用...
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name "工作流管理器" ^
    --paths src ^
    --add-data "src/utils/workflows.json;utils" ^
    --hidden-import=ui ^
    --hidden-import=ui.main_window ^
    --hidden-import=ui.scene_dialog ^
    --hidden-import=core ^
    --hidden-import=core.scene ^
    --hidden-import=utils ^
    --hidden-import=utils.path_utils ^
    --hidden-import=ttkthemes ^
    --hidden-import=tkinter ^
    --hidden-import=tkinterdnd2 ^
    --hidden-import=json ^
    --hidden-import=os ^
    --hidden-import=time ^
    --hidden-import=subprocess ^
    --hidden-import=sys ^
    --hidden-import=uuid ^
    --hidden-import=dataclasses ^
    src/main.py

echo 正在复制数据文件...
copy src\utils\workflows.json dist\

echo 打包完成！
pause
