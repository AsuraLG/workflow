import os
import sys
from typing import Optional

class PathUtils:
    @staticmethod
    def get_resource_path(relative_path: str) -> str:
        """获取资源绝对路径"""
        try:
            # PyInstaller创建临时文件夹,将路径存储在_MEIPASS中
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @staticmethod
    def get_app_dir() -> str:
        """获取应用程序目录"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            return os.path.dirname(sys.executable)
        else:
            # 如果是直接运行的py文件
            return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def ensure_directory_exists(directory: str) -> None:
        """确保目录存在，如果不存在则创建"""
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def get_file_extension(file_path: str) -> Optional[str]:
        """获取文件扩展名"""
        _, ext = os.path.splitext(file_path)
        return ext.lower() if ext else None
