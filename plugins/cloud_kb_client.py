# -*- coding: utf-8 -*-
"""
云知识库客户端模块
支持通过云端服务器更新和管理知识库
"""

import json
import urllib.request
import urllib.error
import urllib.parse
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum


class SyncStatus(Enum):
    """同步状态"""
    PENDING = "pending"
    SYNCING = "syncing"
    SUCCESS = "success"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class CloudKnowledgeItem:
    """云端知识条目"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    version: int
    created_at: str
    updated_at: str
    checksum: str
    author: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CloudKnowledgeItem':
        return cls(**data)
    
    def calculate_checksum(self) -> str:
        """计算内容校验和"""
        content = f"{self.title}{self.content}{self.version}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()


@dataclass
class SyncResult:
    """同步结果"""
    success: bool
    message: str
    downloaded: int = 0
    uploaded: int = 0
    conflicts: List[Dict] = None
    
    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []


class CloudKnowledgeBaseClient:
    """云知识库客户端"""
    
    DEFAULT_TIMEOUT = 30
    API_VERSION = "v1"
    
    def __init__(self, server_url: str = "", api_key: str = ""):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self._auth_required: Optional[bool] = None  # None = 未知, True = 需要, False = 不需要
        self._last_sync_time: Optional[str] = None
        self._local_cache: Dict[str, CloudKnowledgeItem] = {}
    
    def is_configured(self) -> bool:
        """检查是否已配置
        
        支持两种模式：
        1. 有认证：需要 server_url 和 api_key
        2. 无认证：只需要 server_url
        """
        if not self.server_url:
            return False
        # 如果已知不需要认证，则只需要 server_url
        if self._auth_required is False:
            return True
        # 默认需要 api_key
        return bool(self.api_key)
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Version": self.API_VERSION
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _make_request(self, method: str, endpoint: str, 
                      data: Optional[dict] = None,
                      timeout: int = None) -> Tuple[bool, Any]:
        """发送HTTP请求"""
        if not self.server_url:
            return False, "云知识库未配置"
        
        url = f"{self.server_url}/api/{self.API_VERSION}/{endpoint}"
        timeout = timeout or self.DEFAULT_TIMEOUT
        
        try:
            if data:
                req_data = json.dumps(data).encode('utf-8')
            else:
                req_data = None
            
            req = urllib.request.Request(
                url,
                data=req_data,
                headers=self._get_headers(),
                method=method
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                return True, response_data
                
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP错误 {e.code}: {e.reason}"
            try:
                error_body = json.loads(e.read().decode('utf-8'))
                if 'message' in error_body:
                    error_msg = error_body['message']
            except:
                pass
            return False, error_msg
            
        except urllib.error.URLError as e:
            return False, f"连接错误: {e.reason}"
            
        except json.JSONDecodeError:
            return False, "服务器返回无效JSON数据"
            
        except Exception as e:
            return False, f"请求失败: {str(e)}"
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试服务器连接
        
        同时检测服务器是否需要认证
        """
        success, result = self._make_request("GET", "health")
        if success:
            # 检查服务器是否需要认证
            if isinstance(result, dict):
                auth_disabled = result.get('auth') == 'disabled'
                auth_required = result.get('auth_required', True)
                if auth_disabled or auth_required is False:
                    self._auth_required = False
                    return True, "连接成功（无需认证）"
            self._auth_required = True
            return True, "连接成功（需要认证）"
        return False, str(result)
    
    def get_server_info(self) -> Tuple[bool, Dict]:
        """获取服务器信息"""
        return self._make_request("GET", "info")
    
    def list_knowledge_items(self, category: Optional[str] = None,
                             tags: Optional[List[str]] = None,
                             search: Optional[str] = None) -> Tuple[bool, List[CloudKnowledgeItem]]:
        """获取知识条目列表"""
        params = {}
        if category:
            params['category'] = category
        if tags:
            params['tags'] = ','.join(tags)
        if search:
            params['search'] = search
        
        endpoint = "knowledge"
        if params:
            endpoint += "?" + urllib.parse.urlencode(params)
        
        success, result = self._make_request("GET", endpoint)
        if success and isinstance(result, list):
            items = [CloudKnowledgeItem.from_dict(item) for item in result]
            return True, items
        return False, []
    
    def get_knowledge_item(self, item_id: str) -> Tuple[bool, Optional[CloudKnowledgeItem]]:
        """获取单个知识条目"""
        success, result = self._make_request("GET", f"knowledge/{item_id}")
        if success and isinstance(result, dict):
            return True, CloudKnowledgeItem.from_dict(result)
        return False, None
    
    def create_knowledge_item(self, title: str, content: str,
                              category: str = "general",
                              tags: Optional[List[str]] = None,
                              author: Optional[str] = None) -> Tuple[bool, Optional[CloudKnowledgeItem]]:
        """创建新知识条目"""
        data = {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags or [],
            "author": author
        }
        
        success, result = self._make_request("POST", "knowledge", data)
        if success and isinstance(result, dict):
            return True, CloudKnowledgeItem.from_dict(result)
        return False, None
    
    def update_knowledge_item(self, item_id: str, **kwargs) -> Tuple[bool, Optional[CloudKnowledgeItem]]:
        """更新知识条目"""
        success, result = self._make_request("PUT", f"knowledge/{item_id}", kwargs)
        if success and isinstance(result, dict):
            return True, CloudKnowledgeItem.from_dict(result)
        return False, None
    
    def delete_knowledge_item(self, item_id: str) -> Tuple[bool, str]:
        """删除知识条目"""
        success, result = self._make_request("DELETE", f"knowledge/{item_id}")
        if success:
            return True, "删除成功"
        return False, str(result)
    
    def get_categories(self) -> Tuple[bool, List[str]]:
        """获取所有分类"""
        success, result = self._make_request("GET", "categories")
        if success and isinstance(result, list):
            return True, result
        return False, []
    
    def get_tags(self) -> Tuple[bool, List[str]]:
        """获取所有标签"""
        success, result = self._make_request("GET", "tags")
        if success and isinstance(result, list):
            return True, result
        return False, []
    
    def sync_from_cloud(self, local_kb_dir: str,
                        since: Optional[str] = None) -> SyncResult:
        """从云端同步知识库到本地"""
        if not self.is_configured():
            return SyncResult(False, "云知识库未配置")
        
        # 获取服务器上的所有条目
        success, cloud_items = self.list_knowledge_items()
        if not success:
            return SyncResult(False, f"获取云端数据失败: {cloud_items}")
        
        downloaded = 0
        updated = 0
        
        try:
            for item in cloud_items:
                # 转换为本地格式保存
                filename = f"{item.id}.md"
                filepath = os.path.join(local_kb_dir, filename)
                
                # 构建markdown内容
                content = self._convert_to_markdown(item)
                
                # 检查文件是否存在且内容相同
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                    if existing_content != content:
                        updated += 1
                else:
                    downloaded += 1
                
                # 写入文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 更新缓存
                self._local_cache[item.id] = item
            
            self._last_sync_time = datetime.now().isoformat()
            
            return SyncResult(
                True,
                f"同步成功: 下载 {downloaded} 个, 更新 {updated} 个",
                downloaded=downloaded,
                uploaded=0
            )
            
        except Exception as e:
            return SyncResult(False, f"同步失败: {str(e)}")
    
    def _convert_to_markdown(self, item: CloudKnowledgeItem) -> str:
        """将云端条目转换为Markdown格式"""
        lines = [
            f"# {item.title}",
            "",
            f"**ID**: {item.id}",
            f"**分类**: {item.category}",
            f"**标签**: {', '.join(item.tags)}",
            f"**版本**: {item.version}",
            f"**更新时间**: {item.updated_at}",
            "",
            "---",
            "",
            item.content,
            "",
            "---",
            "",
            f"关键词: {', '.join(item.tags)}"
        ]
        return '\n'.join(lines)
    
    def get_last_sync_time(self) -> Optional[str]:
        """获取上次同步时间"""
        return self._last_sync_time
    
    def set_credentials(self, server_url: str, api_key: str):
        """设置服务器凭证"""
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key


# 全局客户端实例
_cloud_kb_client: Optional[CloudKnowledgeBaseClient] = None


def get_cloud_kb_client() -> CloudKnowledgeBaseClient:
    """获取全局云知识库客户端实例"""
    global _cloud_kb_client
    if _cloud_kb_client is None:
        _cloud_kb_client = CloudKnowledgeBaseClient()
    return _cloud_kb_client


def init_cloud_kb_client(server_url: str = "", api_key: str = "") -> CloudKnowledgeBaseClient:
    """初始化云知识库客户端"""
    global _cloud_kb_client
    _cloud_kb_client = CloudKnowledgeBaseClient(server_url, api_key)
    return _cloud_kb_client
