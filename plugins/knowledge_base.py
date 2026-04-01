"""
知识库管理模块 - 增强版
提供知识库文件的加载、检索、去重和相似度检测功能
支持云端同步
"""

import os
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from difflib import SequenceMatcher
import threading


class KnowledgeItem:
    """知识条目"""

    def __init__(self, title: str, content: str, source_file: str, keywords: List[str] = None):
        self.title = title
        self.content = content
        self.source_file = source_file
        self.keywords = keywords or []
        self.id = self._generate_id()
        self.created_at = datetime.now().isoformat()
        self.similarity_hash = self._calculate_similarity_hash()

    def _generate_id(self) -> str:
        """生成唯一ID"""
        content_hash = hashlib.md5(
            f"{self.title}:{self.content[:100]}".encode('utf-8')
        ).hexdigest()[:12]
        return content_hash

    def _calculate_similarity_hash(self) -> str:
        """计算用于相似度比较的哈希"""
        # 对内容进行规范化处理
        normalized = self._normalize_text(self.content)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    def _normalize_text(self, text: str) -> str:
        """规范化文本用于比较"""
        # 移除多余空白
        text = ' '.join(text.split())
        # 转为小写
        text = text.lower()
        # 移除标点符号
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def calculate_similarity(self, other: 'KnowledgeItem') -> float:
        """计算与另一个条目的相似度 (0-1)"""
        # 标题相似度
        title_sim = SequenceMatcher(None, 
            self._normalize_text(self.title), 
            self._normalize_text(other.title)
        ).ratio()

        # 内容相似度
        content_sim = SequenceMatcher(None, 
            self._normalize_text(self.content), 
            self._normalize_text(other.content)
        ).ratio()

        # 关键词重叠度
        if self.keywords and other.keywords:
            set1 = set(k.lower() for k in self.keywords)
            set2 = set(k.lower() for k in other.keywords)
            keyword_sim = len(set1 & set2) / max(len(set1 | set2), 1)
        else:
            keyword_sim = 0.0

        # 加权平均
        return title_sim * 0.4 + content_sim * 0.5 + keyword_sim * 0.1

    def __repr__(self):
        return f"KnowledgeItem(id='{self.id}', title='{self.title}', source='{self.source_file}')"

    def __eq__(self, other):
        if not isinstance(other, KnowledgeItem):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class KnowledgeBase:
    """知识库管理器 - 支持去重和相似度检测"""

    DEFAULT_KB_DIR = "knowledge_base"
    SIMILARITY_THRESHOLD = 0.85  # 相似度阈值，超过则认为重复

    def __init__(self, kb_dir: Optional[str] = None):
        """初始化知识库

        Args:
            kb_dir: 知识库目录路径，默认为工作目录下的 knowledge_base 文件夹
        """
        if kb_dir is None:
            self.kb_dir = os.path.join(os.getcwd(), self.DEFAULT_KB_DIR)
        else:
            self.kb_dir = kb_dir

        self.knowledge_items: List[KnowledgeItem] = []
        self._cloud_client = None
        self._last_sync_time: Optional[str] = None
        self._sync_enabled = False
        self._lock = threading.RLock()  # 线程锁

        self._ensure_kb_dir_exists()
        self.load_all_knowledge()
        self._init_cloud_client()

    def _init_cloud_client(self):
        """初始化云客户端"""
        try:
            from plugins.cloud_kb_client import get_cloud_kb_client
            self._cloud_client = get_cloud_kb_client()
            self._load_cloud_config()
        except ImportError:
            self._cloud_client = None

    def _load_cloud_config(self):
        """加载云端配置"""
        try:
            from PyQt6.QtCore import QSettings
            settings = QSettings("BBCode", "IDE")
            server_url = settings.value("cloud_kb.server_url", "")
            api_key = settings.value("cloud_kb.api_key", "")
            self._sync_enabled = settings.value("cloud_kb.sync_enabled", False) in [True, "true", "True"]

            if self._cloud_client and server_url and api_key:
                self._cloud_client.set_credentials(server_url, api_key)
        except Exception:
            pass

    def is_cloud_sync_enabled(self) -> bool:
        """检查是否启用了云端同步"""
        return self._sync_enabled and self._cloud_client is not None and self._cloud_client.is_configured()

    def sync_from_cloud(self) -> Tuple[bool, str]:
        """从云端同步知识库

        Returns:
            (success, message) 元组
        """
        if not self.is_cloud_sync_enabled():
            return False, "云端同步未启用或未配置"

        if self._cloud_client is None:
            return False, "云客户端未初始化"

        try:
            result = self._cloud_client.sync_from_cloud(self.kb_dir)
            if result.success:
                self._last_sync_time = datetime.now().isoformat()
                self.load_all_knowledge()  # 重新加载知识库
                return True, result.message
            else:
                return False, result.message
        except Exception as e:
            return False, f"同步失败: {str(e)}"

    def test_cloud_connection(self) -> Tuple[bool, str]:
        """测试云端连接

        Returns:
            (success, message) 元组
        """
        if self._cloud_client is None:
            return False, "云客户端未初始化"

        if not self._cloud_client.is_configured():
            return False, "云知识库未配置"

        return self._cloud_client.test_connection()

    def get_last_sync_time(self) -> Optional[str]:
        """获取上次同步时间"""
        return self._last_sync_time

    def set_cloud_sync_enabled(self, enabled: bool):
        """设置云端同步开关"""
        self._sync_enabled = enabled
        try:
            from PyQt6.QtCore import QSettings
            settings = QSettings("BBCode", "IDE")
            settings.setValue("cloud_kb.sync_enabled", enabled)
        except Exception:
            pass

    def update_cloud_credentials(self, server_url: str, api_key: str):
        """更新云端凭证"""
        if self._cloud_client:
            self._cloud_client.set_credentials(server_url, api_key)

        try:
            from PyQt6.QtCore import QSettings
            settings = QSettings("BBCode", "IDE")
            settings.setValue("cloud_kb.server_url", server_url)
            settings.setValue("cloud_kb.api_key", api_key)
        except Exception:
            pass

    def _ensure_kb_dir_exists(self):
        """确保知识库目录存在"""
        if not os.path.exists(self.kb_dir):
            os.makedirs(self.kb_dir)
            # 创建示例知识文件
            self._create_sample_knowledge()

    def _create_sample_knowledge(self):
        """创建示例知识文件"""
        sample_content = """# Python 基础知识

## 变量和数据类型

Python 中的基本数据类型包括：
- int: 整数
- float: 浮点数
- str: 字符串
- bool: 布尔值
- list: 列表
- dict: 字典

## 条件语句

```python
if condition:
    # 代码块
elif another_condition:
    # 代码块
else:
    # 代码块
```

## 循环

for 循环示例：
```python
for item in iterable:
    # 处理每个元素
```

while 循环示例：
```python
while condition:
    # 循环体
```

关键词: python, 基础, 变量, 数据类型, 条件, 循环
"""
        sample_file = os.path.join(self.kb_dir, "python_basics.md")
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write(sample_content)

    def load_all_knowledge(self):
        """加载所有知识文件"""
        with self._lock:
            self.knowledge_items = []

            if not os.path.exists(self.kb_dir):
                return

            for filename in os.listdir(self.kb_dir):
                if filename.endswith(".md") or filename.endswith(".txt"):
                    filepath = os.path.join(self.kb_dir, filename)
                    try:
                        self._load_knowledge_file(filepath)
                    except Exception as e:
                        print(f"加载知识文件失败 {filename}: {e}")

            # 加载后进行去重处理
            self._deduplicate_items()

    def _load_knowledge_file(self, filepath: str):
        """加载单个知识文件"""
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        filename = os.path.basename(filepath)

        # 解析知识条目
        sections = self._parse_sections(content)

        for section in sections:
            title = section.get("title", "未命名")
            section_content = section.get("content", "")
            keywords = section.get("keywords", [])

            item = KnowledgeItem(
                title=title, content=section_content, source_file=filename, keywords=keywords
            )
            self.knowledge_items.append(item)

    def _parse_sections(self, content: str) -> List[Dict]:
        """解析知识文件内容，按标题分割成多个条目"""
        sections = []

        # 查找文件末尾的关键词行
        keywords = []
        keyword_match = re.search(r"关键词[:：]\s*(.+?)(?:\n|$)", content, re.DOTALL)
        if keyword_match:
            keywords = [k.strip() for k in keyword_match.group(1).split(",")]
            # 移除关键词行
            content = content[: keyword_match.start()]

        # 按 # 标题分割
        pattern = r"^(#{1,3})\s+(.+)$"
        lines = content.split("\n")

        current_section = None
        current_content = []

        for line in lines:
            match = re.match(pattern, line)
            if match:
                # 保存上一个section
                if current_section:
                    sections.append(
                        {
                            "title": current_section,
                            "content": "\n".join(current_content).strip(),
                            "keywords": keywords,
                        }
                    )
                current_section = match.group(2)
                current_content = []
            else:
                current_content.append(line)

        # 保存最后一个section
        if current_section:
            sections.append(
                {
                    "title": current_section,
                    "content": "\n".join(current_content).strip(),
                    "keywords": keywords,
                }
            )

        # 如果没有找到任何标题，将整个文件作为一个条目
        if not sections and content.strip():
            sections.append(
                {"title": "未分类知识", "content": content.strip(), "keywords": keywords}
            )

        return sections

    def _deduplicate_items(self):
        """对知识条目进行去重"""
        with self._lock:
            unique_items: List[KnowledgeItem] = []
            duplicates: List[Tuple[KnowledgeItem, KnowledgeItem, float]] = []

            for item in self.knowledge_items:
                is_duplicate = False
                for existing in unique_items:
                    similarity = item.calculate_similarity(existing)
                    if similarity >= self.SIMILARITY_THRESHOLD:
                        is_duplicate = True
                        duplicates.append((item, existing, similarity))
                        break

                if not is_duplicate:
                    unique_items.append(item)

            self.knowledge_items = unique_items

            if duplicates:
                print(f"知识库去重: 发现并移除了 {len(duplicates)} 个重复条目")

            return duplicates

    def find_similar_items(self, query_item: KnowledgeItem, threshold: float = 0.7) -> List[Tuple[KnowledgeItem, float]]:
        """查找与指定条目相似的知识条目

        Args:
            query_item: 查询条目
            threshold: 相似度阈值

        Returns:
            [(item, similarity), ...] 按相似度排序
        """
        with self._lock:
            results = []
            for item in self.knowledge_items:
                if item.id != query_item.id:
                    similarity = item.calculate_similarity(query_item)
                    if similarity >= threshold:
                        results.append((item, similarity))

            # 按相似度降序排序
            results.sort(key=lambda x: x[1], reverse=True)
            return results

    def check_duplicate(self, title: str, content: str) -> Optional[Tuple[KnowledgeItem, float]]:
        """检查是否存在重复内容

        Args:
            title: 标题
            content: 内容

        Returns:
            如果存在重复，返回 (item, similarity)，否则 None
        """
        temp_item = KnowledgeItem(title=title, content=content, source_file="temp")

        with self._lock:
            for item in self.knowledge_items:
                similarity = item.calculate_similarity(temp_item)
                if similarity >= self.SIMILARITY_THRESHOLD:
                    return (item, similarity)

        return None

    def get_duplicate_groups(self) -> List[List[KnowledgeItem]]:
        """获取所有重复条目组

        Returns:
            每组包含相似的条目
        """
        with self._lock:
            groups: List[List[KnowledgeItem]] = []
            processed: Set[str] = set()

            for item in self.knowledge_items:
                if item.id in processed:
                    continue

                similar_items = [item]
                processed.add(item.id)

                for other in self.knowledge_items:
                    if other.id not in processed:
                        similarity = item.calculate_similarity(other)
                        if similarity >= self.SIMILARITY_THRESHOLD:
                            similar_items.append(other)
                            processed.add(other.id)

                if len(similar_items) > 1:
                    groups.append(similar_items)

            return groups

    def merge_duplicates(self, keep_strategy: str = "longest") -> int:
        """合并重复条目

        Args:
            keep_strategy: 保留策略，可选 "longest"(最长), "newest"(最新), "oldest"(最早)

        Returns:
            合并的条目数量
        """
        with self._lock:
            groups = self.get_duplicate_groups()
            merged_count = 0

            for group in groups:
                if len(group) < 2:
                    continue

                # 选择保留的条目
                if keep_strategy == "longest":
                    keep = max(group, key=lambda x: len(x.content))
                elif keep_strategy == "newest":
                    keep = max(group, key=lambda x: x.created_at)
                else:  # oldest
                    keep = min(group, key=lambda x: x.created_at)

                # 合并其他条目的信息
                for item in group:
                    if item.id != keep.id:
                        # 合并关键词
                        keep.keywords = list(set(keep.keywords + item.keywords))
                        # 合并来源文件信息
                        if item.source_file != keep.source_file:
                            keep.source_file += f", {item.source_file}"
                        merged_count += 1

                # 移除被合并的条目
                self.knowledge_items = [item for item in self.knowledge_items
                                        if item.id == keep.id or item not in group]

            return merged_count

    def search(self, query: str, top_k: int = 3) -> List[KnowledgeItem]:
        """搜索相关知识

        Args:
            query: 查询文本
            top_k: 返回最相关的k个结果

        Returns:
            相关知识条目列表
        """
        with self._lock:
            if not self.knowledge_items:
                return []

            query_lower = query.lower()
            query_keywords = set(query_lower.split())

            scored_items = []

            for item in self.knowledge_items:
                score = self._calculate_relevance(item, query_lower, query_keywords)
                if score > 0:
                    scored_items.append((score, item))

            # 按分数排序，返回top_k
            scored_items.sort(key=lambda x: x[0], reverse=True)
            return [item for _, item in scored_items[:top_k]]

    def _calculate_relevance(self, item: KnowledgeItem, query: str, query_keywords: set) -> float:
        """计算知识条目与查询的相关性分数"""
        score = 0.0

        # 标题匹配（权重高）
        title_lower = item.title.lower()
        if query in title_lower:
            score += 10.0
        for keyword in query_keywords:
            if keyword in title_lower:
                score += 3.0

        # 内容匹配
        content_lower = item.content.lower()
        if query in content_lower:
            score += 5.0
        for keyword in query_keywords:
            if keyword in content_lower:
                score += 1.0

        # 关键词匹配（权重最高）
        for keyword in item.keywords:
            if keyword.lower() in query_keywords or query in keyword.lower():
                score += 5.0

        return score

    def get_context_for_query(self, query: str, max_length: int = 2000) -> str:
        """获取查询相关的知识上下文

        Args:
            query: 查询文本
            max_length: 最大上下文长度

        Returns:
            格式化的知识上下文字符串
        """
        relevant_items = self.search(query, top_k=3)

        if not relevant_items:
            return ""

        context_parts = ["### 相关知识库内容\n"]

        current_length = len(context_parts[0])

        for item in relevant_items:
            item_text = f"\n【{item.title}】\n{item.content}\n"

            if current_length + len(item_text) > max_length:
                # 如果超过长度限制，截断内容
                remaining = max_length - current_length - 50
                if remaining > 100:
                    item_text = f"\n【{item.title}】\n{item.content[:remaining]}...\n"
                else:
                    break

            context_parts.append(item_text)
            current_length += len(item_text)

        return "".join(context_parts)

    def add_knowledge(self, title: str, content: str, filename: Optional[str] = None,
                      keywords: List[str] = None, check_duplicate: bool = True) -> Tuple[str, bool]:
        """添加新知识

        Args:
            title: 知识标题
            content: 知识内容
            filename: 保存的文件名，默认为标题的拼音或英文转换
            keywords: 关键词列表
            check_duplicate: 是否检查重复

        Returns:
            (filepath, is_new) 元组，is_new为False表示是重复条目
        """
        # 检查重复
        if check_duplicate:
            duplicate = self.check_duplicate(title, content)
            if duplicate:
                return (os.path.join(self.kb_dir, duplicate[0].source_file), False)

        if filename is None:
            # 将标题转换为文件名（简单处理）
            filename = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
            filename = filename[:50] + ".md"

        if not filename.endswith(".md"):
            filename += ".md"

        filepath = os.path.join(self.kb_dir, filename)

        # 构建内容
        content_to_write = f"# {title}\n\n{content}\n"
        if keywords:
            content_to_write += f"\n关键词: {', '.join(keywords)}\n"

        # 如果文件已存在，追加内容
        if os.path.exists(filepath):
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"\n\n{content_to_write}")
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content_to_write)

        # 重新加载知识库
        self.load_all_knowledge()

        return (filepath, True)

    def list_knowledge_files(self) -> List[str]:
        """列出所有知识文件"""
        if not os.path.exists(self.kb_dir):
            return []

        files = []
        for filename in os.listdir(self.kb_dir):
            if filename.endswith(".md") or filename.endswith(".txt"):
                files.append(filename)
        return files

    def delete_knowledge_file(self, filename: str) -> bool:
        """删除知识文件"""
        filepath = os.path.join(self.kb_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            self.load_all_knowledge()
            return True
        return False

    def get_statistics(self) -> Dict[str, any]:
        """获取知识库统计信息"""
        with self._lock:
            total_items = len(self.knowledge_items)
            total_files = len(self.list_knowledge_files())

            # 计算重复组
            duplicate_groups = self.get_duplicate_groups()

            # 关键词统计
            all_keywords = []
            for item in self.knowledge_items:
                all_keywords.extend(item.keywords)
            keyword_counts = {}
            for kw in all_keywords:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

            return {
                "total_items": total_items,
                "total_files": total_files,
                "duplicate_groups": len(duplicate_groups),
                "duplicates_total": sum(len(group) for group in duplicate_groups),
                "top_keywords": sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            }


# 全局知识库实例
_kb_instance: Optional[KnowledgeBase] = None
_kb_lock = threading.Lock()


def get_knowledge_base() -> KnowledgeBase:
    """获取全局知识库实例"""
    global _kb_instance
    if _kb_instance is None:
        with _kb_lock:
            if _kb_instance is None:
                _kb_instance = KnowledgeBase()
    return _kb_instance


def reload_knowledge_base():
    """重新加载知识库"""
    global _kb_instance
    with _kb_lock:
        if _kb_instance is not None:
            _kb_instance.load_all_knowledge()


def check_and_merge_duplicates(keep_strategy: str = "longest") -> int:
    """检查并合并重复条目

    Args:
        keep_strategy: 保留策略

    Returns:
        合并的条目数量
    """
    kb = get_knowledge_base()
    return kb.merge_duplicates(keep_strategy)


def get_kb_statistics() -> Dict[str, any]:
    """获取知识库统计信息"""
    kb = get_knowledge_base()
    return kb.get_statistics()
