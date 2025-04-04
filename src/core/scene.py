from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json
import os
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
        workflow = cls(name=data['name'])
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
        self.workflows: Dict[str, Workflow] = {}
        self.load_workflows()

    def load_workflows(self) -> None:
        """从文件加载工作流"""
        if os.path.exists(self.workflows_file):
            try:
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    workflows_data = json.load(f)
                    self.workflows = {
                        name: Workflow.from_dict(data)
                        for name, data in workflows_data.items()
                    }
            except Exception as e:
                print(f"加载工作流文件时出错: {e}")
                self.workflows = {}

    def save_workflows(self) -> None:
        """保存工作流到文件"""
        try:
            workflows_data = {
                name: workflow.to_dict()
                for name, workflow in self.workflows.items()
            }
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(workflows_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存工作流文件时出错: {e}")

    def add_workflow(self, workflow: Workflow) -> None:
        """添加工作流"""
        self.workflows[workflow.name] = workflow
        self.save_workflows()

    def remove_workflow(self, workflow_name: str) -> bool:
        """移除工作流"""
        if workflow_name in self.workflows:
            del self.workflows[workflow_name]
            self.save_workflows()
            return True
        return False

    def get_workflow(self, workflow_name: str) -> Optional[Workflow]:
        """获取工作流"""
        return self.workflows.get(workflow_name)

    def copy_workflow(self, source_name: str, target_name: str) -> bool:
        """复制工作流"""
        if source_name in self.workflows and target_name not in self.workflows:
            source_workflow = self.workflows[source_name]
            new_workflow = Workflow(name=target_name)
            for action in source_workflow.actions:
                new_workflow.add_action(action.type, action.path, action.delay)
            self.add_workflow(new_workflow)
            return True
        return False
