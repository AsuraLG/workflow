from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import json
import os
import uuid
from src.utils.path_utils import PathUtils

@dataclass
class Action:
    """工作流动作类"""
    type: str  # 'folder' 或 'file'
    path: str
    delay: float

@dataclass
class Workflow:
    """工作流类"""
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actions: List[Action] = field(default_factory=list)

    def add_action(self, action_type: str, path: str, delay: float) -> None:
        """添加动作到工作流"""
        self.actions.append(Action(type=action_type, path=path, delay=delay))

    def remove_action(self, index: int) -> None:
        """从工作流中移除动作"""
        if 0 <= index < len(self.actions):
            del self.actions[index]

    def to_dict(self) -> Dict:
        """将工作流转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'actions': [
                {
                    'type': action.type,
                    'path': action.path,
                    'delay': action.delay
                }
                for action in self.actions
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Workflow':
        """从字典创建工作流"""
        workflow = cls(
            name=data['name'],
            id=data.get('id', str(uuid.uuid4()))  # 为旧数据生成新ID
        )
        for action_data in data.get('actions', []):
            workflow.add_action(
                action_type=action_data['type'],
                path=action_data['path'],
                delay=action_data['delay']
            )
        return workflow

class WorkflowManager:
    """工作流管理器类"""
    def __init__(self, workflows_file: Optional[str] = None):
        self.workflows_file = workflows_file or os.path.join(PathUtils.get_app_dir(), "workflows.json")
        self.workflows: Dict[str, Workflow] = {}  # key 是工作流ID
        self.load_workflows()

    def load_workflows(self) -> None:
        """从文件加载工作流"""
        if os.path.exists(self.workflows_file):
            try:
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    workflows_data = json.load(f)
                    self.workflows = {
                        data.get('id', str(uuid.uuid4())): Workflow.from_dict(data)
                        for data in workflows_data.values()
                    }
            except Exception as e:
                print(f"加载工作流文件时出错: {e}")
                self.workflows = {}

    def save_workflows(self) -> None:
        """保存工作流到文件"""
        try:
            workflows_data = {
                workflow.id: workflow.to_dict()
                for workflow in self.workflows.values()
            }
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(workflows_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存工作流文件时出错: {e}")

    def is_name_duplicate(self, name: str, exclude_id: Optional[str] = None) -> bool:
        """检查工作流名称是否重复

        Args:
            name: 要检查的名称
            exclude_id: 要排除的工作流ID（用于编辑时排除自身）

        Returns:
            bool: 如果名称重复返回True，否则返回False
        """
        # 检查除了当前编辑的工作流之外的所有工作流是否有重名
        for workflow_id, workflow in self.workflows.items():
            if workflow_id != exclude_id and workflow.name == name:
                return True
        return False

    def add_workflow(self, workflow: Workflow) -> Tuple[bool, str]:
        """添加工作流

        Args:
            workflow: 要添加的工作流

        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        if self.is_name_duplicate(workflow.name):
            return False, "工作流名称已存在"
        self.workflows[workflow.id] = workflow
        self.save_workflows()
        return True, ""

    def update_workflow(self, workflow: Workflow) -> Tuple[bool, str]:
        """更新工作流

        Args:
            workflow: 要更新的工作流

        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        if self.is_name_duplicate(workflow.name, workflow.id):
            return False, "工作流名称已存在"
        self.workflows[workflow.id] = workflow
        self.save_workflows()
        return True, ""

    def remove_workflow(self, workflow_id: str) -> bool:
        """移除工作流"""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            self.save_workflows()
            return True
        return False

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """获取工作流"""
        return self.workflows.get(workflow_id)

    def copy_workflow(self, source_id: str, new_name: str) -> Tuple[bool, str]:
        """复制工作流

        Args:
            source_id: 源工作流ID
            new_name: 新工作流名称

        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        if self.is_name_duplicate(new_name):
            return False, "工作流名称已存在"

        source_workflow = self.get_workflow(source_id)
        if not source_workflow:
            return False, "源工作流不存在"

        new_workflow = Workflow(name=new_name)
        for action in source_workflow.actions:
            new_workflow.add_action(action.type, action.path, action.delay)

        self.workflows[new_workflow.id] = new_workflow
        self.save_workflows()
        return True, ""
