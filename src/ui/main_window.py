import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Dict, List
import os
import time
from src.core.scene import Workflow, WorkflowManager
from src.ui.scene_dialog import WorkflowDialog

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("工作流管理器")
        self.root.geometry("600x400")

        # 初始化工作流管理器
        self.workflow_manager = WorkflowManager()

        # 设置UI
        self._setup_ui()
        self._update_workflow_list()

    def _setup_ui(self) -> None:
        """设置UI组件"""
        # 配置根窗口的网格布局权重
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 配置主框架的网格布局权重
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=3)  # 列表区域占比更大
        main_frame.grid_columnconfigure(1, weight=1)  # 按钮区域占比较小

        # 创建左侧框架（包含工作流列表）
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(0, weight=0)  # 标题行不伸缩
        list_frame.grid_rowconfigure(1, weight=1)  # 列表区域自动伸缩
        list_frame.grid_columnconfigure(0, weight=1)

        # 添加工作流列表标题
        title_label = ttk.Label(list_frame, text="工作流列表", font=("微软雅黑", 10, "bold"))
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # 创建工作流列表和滚动条
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=1, column=0, sticky="nsew")
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        self.workflow_listbox = tk.Listbox(list_container, selectmode=tk.SINGLE, font=("微软雅黑", 9), activestyle="none")
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.workflow_listbox.yview)
        self.workflow_listbox.configure(yscrollcommand=scrollbar.set)
        self.workflow_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 绑定事件
        self.workflow_listbox.bind('<<ListboxSelect>>', self._on_select_workflow)
        self.workflow_listbox.bind('<Double-Button-1>', self._on_double_click_workflow)

        # 创建右侧按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=1, sticky="n")

        # 添加按钮
        buttons = [
            ("新建工作流", self._create_workflow),
            ("编辑工作流", self._edit_workflow),
            ("删除工作流", self._delete_workflow),
            ("复制工作流", self._copy_workflow),
            ("执行工作流", self._execute_workflow)
        ]

        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command, width=15)
            btn.pack(pady=5)

    def _update_workflow_list(self) -> None:
        """更新工作流列表"""
        self.workflow_listbox.delete(0, tk.END)
        for workflow_name in self.workflow_manager.workflows.keys():
            self.workflow_listbox.insert(tk.END, workflow_name)

    def _on_select_workflow(self, event: tk.Event) -> None:
        """处理工作流选择事件"""
        pass  # 可以在这里添加选中工作流时的处理逻辑

    def _on_double_click_workflow(self, event: tk.Event) -> None:
        """处理工作流双击事件"""
        self._edit_workflow()

    def _create_workflow(self) -> None:
        """创建新工作流"""
        dialog = WorkflowDialog(self.root, on_save=self._handle_workflow_save)
        if dialog.result:
            workflow_name, actions = dialog.result
            workflow = Workflow(name=workflow_name)
            for action in actions:
                workflow.add_action(action['type'], action['path'], action['delay'])
            self.workflow_manager.add_workflow(workflow)
            self._update_workflow_list()

    def _edit_workflow(self) -> None:
        """编辑工作流"""
        selection = self.workflow_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个工作流")
            return

        workflow_name = self.workflow_listbox.get(selection[0])
        workflow = self.workflow_manager.get_workflow(workflow_name)
        if workflow:
            actions = [{'type': a.type, 'path': a.path, 'delay': a.delay} for a in workflow.actions]
            dialog = WorkflowDialog(self.root, workflow_name=workflow_name, actions=actions, on_save=self._handle_workflow_save)
            if dialog.result:
                new_name, new_actions = dialog.result
                if new_name != workflow_name:
                    self.workflow_manager.remove_workflow(workflow_name)
                new_workflow = Workflow(name=new_name)
                for action in new_actions:
                    new_workflow.add_action(action['type'], action['path'], action['delay'])
                self.workflow_manager.add_workflow(new_workflow)
                self._update_workflow_list()

    def _delete_workflow(self) -> None:
        """删除工作流"""
        selection = self.workflow_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个工作流")
            return

        workflow_name = self.workflow_listbox.get(selection[0])
        if messagebox.askyesno("确认", f"确定要删除工作流 '{workflow_name}' 吗？"):
            if self.workflow_manager.remove_workflow(workflow_name):
                self._update_workflow_list()

    def _copy_workflow(self) -> None:
        """复制工作流"""
        selection = self.workflow_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个工作流")
            return

        source_name = self.workflow_listbox.get(selection[0])
        target_name = simpledialog.askstring("复制工作流", "请输入新工作流名称:", initialvalue=f"{source_name}_副本")
        if target_name:
            if self.workflow_manager.copy_workflow(source_name, target_name):
                self._update_workflow_list()
            else:
                messagebox.showerror("错误", "工作流名称已存在或源工作流不存在")

    def _execute_workflow(self) -> None:
        """执行工作流"""
        selection = self.workflow_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个工作流")
            return

        workflow_name = self.workflow_listbox.get(selection[0])
        workflow = self.workflow_manager.get_workflow(workflow_name)
        if workflow:
            for action in workflow.actions:
                try:
                    if action.delay > 0:
                        time.sleep(action.delay)
                    if action.type == 'file':
                        os.startfile(action.path)
                    else:
                        os.startfile(action.path)
                except Exception as e:
                    messagebox.showerror("错误", f"执行动作时出错：{str(e)}")
                    break

    def _handle_workflow_save(self, workflow_name: str, actions: List[Dict]) -> None:
        """处理工作流保存"""
        workflow = Workflow(name=workflow_name)
        for action in actions:
            workflow.add_action(action['type'], action['path'], action['delay'])
        self.workflow_manager.add_workflow(workflow)
        self._update_workflow_list()

    def run(self) -> None:
        """运行应用程序"""
        self.root.mainloop()
