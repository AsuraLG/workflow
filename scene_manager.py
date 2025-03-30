import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import os
import time
import sys

def resource_path(relative_path):
    """ 获取资源绝对路径 """
    try:
        # PyInstaller创建临时文件夹,将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SceneDialog:
    def __init__(self, parent, scene_name=None, actions=None):
        self.result = None
        self.parent = parent

        dialog = tk.Toplevel(parent)
        dialog.title("场景编辑")
        dialog.geometry("600x400")

        # 配置对话框的网格布局权重
        dialog.grid_rowconfigure(1, weight=1)  # 操作列表区域可伸缩
        dialog.grid_columnconfigure(0, weight=1)

        # 场景名称框架
        name_frame = ttk.Frame(dialog, padding="10")
        name_frame.grid(row=0, column=0, sticky="ew")
        name_frame.grid_columnconfigure(1, weight=1)  # 输入框可伸缩

        ttk.Label(name_frame, text="场景名称:", font=("微软雅黑", 9)).grid(row=0, column=0, padx=(0, 10))
        name_entry = ttk.Entry(name_frame, font=("微软雅黑", 9))
        name_entry.grid(row=0, column=1, sticky="ew")
        if scene_name:
            name_entry.insert(0, scene_name)

        # 操作列表框架
        actions_frame = ttk.LabelFrame(dialog, text="操作列表", padding="10")
        actions_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))

        # 配置操作列表框架的网格布局权重
        actions_frame.grid_rowconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(0, weight=1)

        # 创建列表容器
        list_container = ttk.Frame(actions_frame)
        list_container.grid(row=0, column=0, sticky="nsew")
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        # 创建列表和滚动条
        self.actions_listbox = tk.Listbox(list_container, font=("微软雅黑", 9), activestyle="none")
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.actions_listbox.yview)

        self.actions_listbox.configure(yscrollcommand=scrollbar.set)
        self.actions_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 添加双击事件绑定
        self.actions_listbox.bind('<Double-Button-1>', self.on_double_click_action)

        # 按钮框架
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.grid(row=2, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)  # 使按钮居中

        # 创建内部按钮框架用于居中对齐
        inner_button_frame = ttk.Frame(button_frame)
        inner_button_frame.grid(row=0, column=0)

        # 添加按钮
        buttons = [
            ("添加文件夹", lambda: self.add_action(dialog, 'folder')),
            ("添加文件", lambda: self.add_action(dialog, 'file')),
            ("删除操作", self.remove_action),
            ("保存", lambda: self.save(dialog, name_entry.get())),
            ("取消", dialog.destroy)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(inner_button_frame, text=text, command=command, width=10)
            btn.pack(side=tk.LEFT, padx=5)

        # 加载现有操作
        self.actions = actions if actions else []
        self.update_actions_list()

        # 设置对话框模态
        dialog.transient(parent)
        dialog.grab_set()

        # 设置最小窗口大小
        dialog.minsize(500, 300)

        # 将对话框位置设置为相对于父窗口居中
        dialog.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        dialog.geometry(f"+{x}+{y}")

        parent.wait_window(dialog)

    def add_action(self, parent, action_type, path=None):
        if path is None:
            if action_type == 'folder':
                path = filedialog.askdirectory(parent=parent)
            else:
                path = filedialog.askopenfilename(parent=parent)

        if path:
            delay = simpledialog.askfloat("延迟", "请输入延迟时间（秒）:", initialvalue=0.0)
            if delay is not None:
                self.actions.append({
                    'type': action_type,
                    'path': path,
                    'delay': delay
                })
                self.update_actions_list()

    def remove_action(self):
        selection = self.actions_listbox.curselection()
        if selection:
            index = selection[0]
            del self.actions[index]
            self.update_actions_list()

    def update_actions_list(self):
        self.actions_listbox.delete(0, tk.END)
        for action in self.actions:
            type_str = "文件夹" if action['type'] == 'folder' else "文件"
            self.actions_listbox.insert(tk.END, f"{type_str}: {action['path']} (延迟: {action['delay']}秒)")

    def save(self, dialog, scene_name):
        if not scene_name:
            messagebox.showwarning("警告", "请输入场景名称")
            return

        self.result = (scene_name, self.actions)
        dialog.destroy()

    def on_double_click_action(self, event):
        """处理操作列表的双击事件"""
        selection = self.actions_listbox.curselection()
        if selection:
            index = selection[0]
            action = self.actions[index]
            path = action['path']

            # 如果是文件，打开其所在目录
            if action['type'] == 'file':
                path = os.path.dirname(path)

            # 打开目录
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("错误", f"无法打开路径：{path}\n错误信息：{str(e)}")

class SceneManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("场景管理器")
        self.root.geometry("600x400")  # 调整窗口大小

        # 配置根窗口的网格布局权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # 获取应用数据目录
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # 如果是直接运行的py文件
            self.app_dir = os.path.dirname(os.path.abspath(__file__))

        self.scenes_file = os.path.join(self.app_dir, "scenes.json")
        self.scenes = self.load_scenes()

        self.setup_ui()

    def load_scenes(self):
        if os.path.exists(self.scenes_file):
            with open(self.scenes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_scenes(self):
        with open(self.scenes_file, 'w', encoding='utf-8') as f:
            json.dump(self.scenes, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 配置主框架的网格布局权重
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=3)  # 列表区域占比更大
        main_frame.grid_columnconfigure(1, weight=1)  # 按钮区域占比较小

        # 创建左侧框架（包含场景列表）
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # 配置列表框架的网格布局权重
        list_frame.grid_rowconfigure(0, weight=0)  # 标题行不伸缩
        list_frame.grid_rowconfigure(1, weight=1)  # 列表区域自动伸缩
        list_frame.grid_columnconfigure(0, weight=1)

        # 添加场景列表标题
        title_label = ttk.Label(list_frame, text="场景列表", font=("微软雅黑", 10, "bold"))
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # 创建场景列表和滚动条
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        self.scene_listbox = tk.Listbox(list_container, selectmode=tk.SINGLE, font=("微软雅黑", 9), activestyle="none")
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.scene_listbox.yview)

        self.scene_listbox.configure(yscrollcommand=scrollbar.set)
        self.scene_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.scene_listbox.bind('<<ListboxSelect>>', self.on_select_scene)
        self.scene_listbox.bind('<Double-Button-1>', self.on_double_click_scene)  # 添加双击事件

        # 创建右侧按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=1, sticky="n")

        # 添加按钮
        buttons = [
            ("新建场景", self.create_scene),
            ("编辑场景", self.edit_scene),
            ("删除场景", self.delete_scene),
            ("复制场景", self.copy_scene),
            ("执行场景", self.execute_scene)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, command=command, width=15)  # 统一按钮宽度
            btn.pack(pady=5)

        # 更新场景列表
        self.update_scene_list()

    def update_scene_list(self):
        self.scene_listbox.delete(0, tk.END)
        for scene_name in self.scenes.keys():
            self.scene_listbox.insert(tk.END, scene_name)

    def on_select_scene(self, event):
        selection = self.scene_listbox.curselection()
        if selection:
            self.selected_scene = self.scene_listbox.get(selection[0])

    def on_double_click_scene(self, event):
        """处理场景列表的双击事件"""
        selection = self.scene_listbox.curselection()
        if selection:
            self.selected_scene = self.scene_listbox.get(selection[0])
            self.edit_scene()

    def create_scene(self):
        dialog = SceneDialog(self.root)
        if dialog.result:
            scene_name, actions = dialog.result
            self.scenes[scene_name] = actions
            self.save_scenes()
            self.update_scene_list()

    def edit_scene(self):
        if not hasattr(self, 'selected_scene'):
            messagebox.showwarning("警告", "请先选择一个场景")
            return

        dialog = SceneDialog(self.root, self.selected_scene, self.scenes[self.selected_scene])
        if dialog.result:
            scene_name, actions = dialog.result
            if scene_name != self.selected_scene:
                del self.scenes[self.selected_scene]
            self.scenes[scene_name] = actions
            self.save_scenes()
            self.update_scene_list()

    def delete_scene(self):
        if not hasattr(self, 'selected_scene'):
            messagebox.showwarning("警告", "请先选择一个场景")
            return

        if messagebox.askyesno("确认", f"确定要删除场景 '{self.selected_scene}' 吗？"):
            del self.scenes[self.selected_scene]
            self.save_scenes()
            self.update_scene_list()

    def copy_scene(self):
        if not hasattr(self, 'selected_scene'):
            messagebox.showwarning("警告", "请先选择一个场景")
            return

        base_name = self.selected_scene
        counter = 1
        new_name = f"{base_name} (副本 {counter})"

        while new_name in self.scenes:
            counter += 1
            new_name = f"{base_name} (副本 {counter})"

        self.scenes[new_name] = self.scenes[base_name].copy()
        self.save_scenes()
        self.update_scene_list()

    def execute_scene(self):
        if not hasattr(self, 'selected_scene'):
            messagebox.showwarning("警告", "请先选择一个场景")
            return

        actions = self.scenes[self.selected_scene]
        for action in actions:
            if action['type'] == 'folder':
                os.startfile(action['path'])
            elif action['type'] == 'file':
                os.startfile(action['path'])
            time.sleep(action['delay'])

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SceneManager()
    app.run()
