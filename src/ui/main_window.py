import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Dict, List, Tuple
import os
import time
import tkinterdnd2
from src.core.scene import Workflow, WorkflowManager
from src.ui.scene_dialog import WorkflowDialog

class MainWindow:
    def __init__(self):
        self.root = tkinterdnd2.TkinterDnD.Tk()
        self.root.title("工作流管理器")
        self.root.geometry("600x400")

        # 初始化工作流管理器
        self.workflow_manager = WorkflowManager()

        # 用于存储列表项与工作流ID的映射
        self.list_item_to_id: Dict[str, str] = {}

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
        self.list_item_to_id.clear()

        # 按名称排序显示
        workflows = sorted(
            self.workflow_manager.workflows.values(),
            key=lambda w: w.name
        )
        for workflow in workflows:
            self.workflow_listbox.insert(tk.END, workflow.name)
            self.list_item_to_id[workflow.name] = workflow.id

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
            success, error = self.workflow_manager.add_workflow(workflow)
            if not success:
                messagebox.showerror("错误", error)
            else:
                self._update_workflow_list()

    def _get_selected_workflow_id(self) -> Optional[str]:
        """获取当前选中的工作流ID"""
        selection = self.workflow_listbox.curselection()
        if not selection:
            return None
        workflow_name = self.workflow_listbox.get(selection[0])
        return self.list_item_to_id.get(workflow_name)

    def _edit_workflow(self) -> None:
        """编辑工作流"""
        workflow_id = self._get_selected_workflow_id()
        if not workflow_id:
            messagebox.showwarning("警告", "请先选择一个工作流")
            return

        workflow = self.workflow_manager.get_workflow(workflow_id)
        if workflow:
            actions = [{'type': a.type, 'path': a.path, 'delay': a.delay} for a in workflow.actions]
            dialog = WorkflowDialog(self.root, workflow_name=workflow.name, actions=actions, on_save=lambda name, acts: self._handle_workflow_edit(workflow_id, name, acts))

    def _handle_workflow_edit(self, workflow_id: str, workflow_name: str, actions: List[Dict]) -> None:
        """处理工作流编辑保存

        Args:
            workflow_id: 要编辑的工作流ID
            workflow_name: 新的工作流名称
            actions: 新的动作列表
        """
        workflow = self.workflow_manager.get_workflow(workflow_id)
        if workflow:
            # 更新工作流
            workflow.name = workflow_name
            workflow.actions = []
            for action in actions:
                workflow.add_action(action['type'], action['path'], action['delay'])
            # 保存更改
            success, error = self.workflow_manager.update_workflow(workflow)
            if not success:
                messagebox.showerror("错误", error)
            else:
                self._update_workflow_list()

    def _delete_workflow(self) -> None:
        """删除工作流"""
        workflow_id = self._get_selected_workflow_id()
        if not workflow_id:
            messagebox.showwarning("警告", "请先选择一个工作流")
            return

        workflow = self.workflow_manager.get_workflow(workflow_id)
        if workflow and messagebox.askyesno("确认", f"确定要删除工作流 '{workflow.name}' 吗？"):
            if self.workflow_manager.remove_workflow(workflow_id):
                self._update_workflow_list()

    def _copy_workflow(self) -> None:
        """复制工作流"""
        workflow_id = self._get_selected_workflow_id()
        if not workflow_id:
            messagebox.showwarning("警告", "请先选择一个工作流")
            return

        workflow = self.workflow_manager.get_workflow(workflow_id)
        if workflow:
            target_name = simpledialog.askstring("复制工作流", "请输入新工作流名称:", initialvalue=f"{workflow.name}_副本")
            if target_name:
                success, error = self.workflow_manager.copy_workflow(workflow_id, target_name)
                if not success:
                    messagebox.showerror("错误", error)
                else:
                    self._update_workflow_list()

    def _execute_workflow(self) -> None:
        """执行工作流"""
        workflow_id = self._get_selected_workflow_id()
        if not workflow_id:
            messagebox.showwarning("警告", "请先选择一个工作流")
            return

        workflow = self.workflow_manager.get_workflow(workflow_id)
        if workflow:
            for action in workflow.actions:
                try:
                    if action.delay > 0:
                        time.sleep(action.delay)
                    os.startfile(action.path)
                except Exception as e:
                    messagebox.showerror("错误", f"执行动作时出错：{str(e)}")
                    break

    def _handle_workflow_save(self, workflow_name: str, actions: List[Dict]) -> None:
        """处理新建工作流保存"""
        # 创建新工作流
        workflow = Workflow(name=workflow_name)
        for action in actions:
            workflow.add_action(action['type'], action['path'], action['delay'])
        success, error = self.workflow_manager.add_workflow(workflow)
        if not success:
            messagebox.showerror("错误", error)
        else:
            self._update_workflow_list()

    def run(self) -> None:
        """运行应用程序"""
        self.root.mainloop()
