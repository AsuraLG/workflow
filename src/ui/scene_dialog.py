import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Optional, List, Dict, Callable
import os

class WorkflowDialog:
    def __init__(
        self,
        parent: tk.Tk,
        workflow_name: Optional[str] = None,
        actions: Optional[List[Dict]] = None,
        on_save: Optional[Callable[[str, List[Dict]], None]] = None
    ):
        self.parent = parent
        self.on_save = on_save
        self.actions = actions if actions else []

        # 使用普通的 Toplevel
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("工作流编辑")
        self.dialog.geometry("600x400")

        # 注册拖拽目标
        self.dialog.drop_target_register('DND_Files')
        self.dialog.dnd_bind('<<Drop>>', self._on_drop)

        self._setup_ui()
        self._center_dialog()

        # 如果是编辑模式，设置工作流名称
        if workflow_name:
            self.name_entry.insert(0, workflow_name)

    def _setup_ui(self) -> None:
        """设置UI组件"""
        # 配置对话框的网格布局权重
        self.dialog.grid_rowconfigure(1, weight=1)
        self.dialog.grid_columnconfigure(0, weight=1)

        # 工作流名称框架
        name_frame = ttk.Frame(self.dialog, padding="10")
        name_frame.grid(row=0, column=0, sticky="ew")
        name_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(name_frame, text="工作流名称:", font=("微软雅黑", 9)).grid(row=0, column=0, padx=(0, 10))
        self.name_entry = ttk.Entry(name_frame, font=("微软雅黑", 9))
        self.name_entry.grid(row=0, column=1, sticky="ew")

        # 操作列表框架
        actions_frame = ttk.LabelFrame(self.dialog, text="操作列表", padding="10")
        actions_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
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

        # 绑定事件
        self.actions_listbox.bind('<Double-Button-1>', self._on_double_click_action)

        # 按钮框架
        button_frame = ttk.Frame(self.dialog, padding="10")
        button_frame.grid(row=2, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)

        # 创建内部按钮框架用于居中对齐
        inner_button_frame = ttk.Frame(button_frame)
        inner_button_frame.grid(row=0, column=0)

        # 添加按钮
        buttons = [
            ("添加文件夹", lambda: self._add_action('folder')),
            ("添加文件", lambda: self._add_action('file')),
            ("删除操作", self._remove_action),
            ("保存", self._save),
            ("取消", self.dialog.destroy)
        ]

        for text, command in buttons:
            btn = ttk.Button(inner_button_frame, text=text, command=command, width=10)
            btn.pack(side=tk.LEFT, padx=5)

        # 设置对话框模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 设置最小窗口大小
        self.dialog.minsize(500, 300)

        # 更新操作列表
        self._update_actions_list()

    def _center_dialog(self) -> None:
        """将对话框居中显示"""
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def _add_action(self, action_type: str, path: Optional[str] = None) -> None:
        """添加动作"""
        if path is None:
            if action_type == 'folder':
                path = filedialog.askdirectory(parent=self.dialog)
            else:
                path = filedialog.askopenfilename(parent=self.dialog)

        if path:
            delay = simpledialog.askfloat("延迟", "请输入延迟时间（秒）:", initialvalue=0.0)
            if delay is not None:
                self.actions.append({
                    'type': action_type,
                    'path': path,
                    'delay': delay
                })
                self._update_actions_list()

    def _remove_action(self) -> None:
        """移除动作"""
        selection = self.actions_listbox.curselection()
        if selection:
            index = selection[0]
            del self.actions[index]
            self._update_actions_list()

    def _update_actions_list(self) -> None:
        """更新动作列表显示"""
        self.actions_listbox.delete(0, tk.END)
        for action in self.actions:
            type_str = "文件夹" if action['type'] == 'folder' else "文件"
            self.actions_listbox.insert(tk.END, f"{type_str}: {action['path']} (延迟: {action['delay']}秒)")

    def _save(self) -> None:
        """保存工作流"""
        workflow_name = self.name_entry.get()
        if not workflow_name:
            messagebox.showwarning("警告", "请输入工作流名称")
            return

        if self.on_save:
            self.on_save(workflow_name, self.actions)
        self.dialog.destroy()

    def _on_double_click_action(self, event: tk.Event) -> None:
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

    def _on_drop(self, event: tk.Event) -> None:
        """处理拖拽释放事件"""
        try:
            # 获取拖拽的文件路径
            files = event.data.split()
            for file_path in files:
                # 移除路径中的引号（如果有）
                file_path = file_path.strip('"')

                # 检查是文件还是文件夹
                if os.path.isdir(file_path):
                    self._add_action('folder', file_path)
                elif os.path.isfile(file_path):
                    self._add_action('file', file_path)
        except Exception as e:
            messagebox.showerror("错误", f"处理拖拽文件时出错：{str(e)}")
