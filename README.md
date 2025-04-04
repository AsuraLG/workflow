# 工作流管理器

一个简单的工作流管理工具，用于管理和执行文件/文件夹操作序列。

## 功能特点

- 创建工作流，包含多个文件/文件夹操作
- 为每个操作设置延迟时间
- 编辑、复制和删除工作流
- 执行工作流，自动按顺序打开文件/文件夹
- 双击操作项可快速打开对应目录

## 项目结构

```
workflow/
├── src/                    # 源代码目录
│   ├── core/              # 核心功能模块
│   │   └── scene.py       # 工作流和动作类定义
│   ├── ui/                # 用户界面模块
│   │   ├── main_window.py # 主窗口
│   │   └── scene_dialog.py # 工作流编辑对话框
│   ├── utils/             # 工具模块
│   │   └── path_utils.py  # 路径处理工具
│   └── main.py            # 程序入口
├── requirements.txt        # 项目依赖
├── run.bat                # 运行脚本
└── README.md              # 项目说明
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

1. 双击 `run.bat` 文件运行程序
2. 或在命令行中执行：
   ```bash
   python src/main.py
   ```

## 使用方法

1. **新建工作流**
   - 点击"新建工作流"按钮
   - 输入工作流名称
   - 添加文件或文件夹操作
   - 为每个操作设置延迟时间
   - 点击"保存"按钮

2. **编辑工作流**
   - 选择要编辑的工作流
   - 点击"编辑工作流"按钮
   - 修改工作流名称或操作
   - 点击"保存"按钮

3. **复制工作流**
   - 选择要复制的工作流
   - 点击"复制工作流"按钮
   - 输入新工作流名称
   - 点击"确定"按钮

4. **删除工作流**
   - 选择要删除的工作流
   - 点击"删除工作流"按钮
   - 确认删除

5. **执行工作流**
   - 选择要执行的工作流
   - 点击"执行工作流"按钮
   - 程序将按顺序执行所有操作

## 技术栈

- Python 3.x
- tkinter (GUI)
- ttkthemes (主题支持)

## 开发环境设置

1. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```

2. 激活虚拟环境：
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 打包说明

使用 PyInstaller 打包：
```bash
pyinstaller --onefile --windowed src/main.py
```

## 注意事项

- 工作流数据保存在 `workflows.json` 文件中
- 确保有足够的权限访问指定的文件和文件夹
- 延迟时间单位为秒，可以为小数
