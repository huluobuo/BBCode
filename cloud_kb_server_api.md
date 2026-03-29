# 云知识库服务器 API 文档

本文档描述了 BBCode 云知识库功能所需的服务器端 API 接口。

## 基础信息

- **API 版本**: v1
- **基础路径**: `/api/v1`
- **认证方式**: Bearer Token (通过 `Authorization` 请求头)

## 请求头

所有请求都需要包含以下头部：

```
Content-Type: application/json
Accept: application/json
X-API-Version: v1
Authorization: Bearer {your_api_key}
```

## API 端点

### 1. 健康检查

检查服务器是否正常运行。

- **URL**: `/api/v1/health`
- **方法**: `GET`
- **认证**: 可选

**响应示例**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. 服务器信息

获取服务器基本信息。

- **URL**: `/api/v1/info`
- **方法**: `GET`
- **认证**: 需要

**响应示例**:
```json
{
  "name": "BBCode Cloud KB Server",
  "version": "1.0.0",
  "total_items": 150,
  "categories": ["python", "javascript", "general"]
}
```

### 3. 获取知识条目列表

获取所有知识条目或按条件筛选。

- **URL**: `/api/v1/knowledge`
- **方法**: `GET`
- **认证**: 需要

**查询参数**:
- `category` (可选): 按分类筛选
- `tags` (可选): 按标签筛选，多个标签用逗号分隔
- `search` (可选): 搜索关键词

**响应示例**:
```json
[
  {
    "id": "python-basics",
    "title": "Python 基础知识",
    "content": "Python 是一种高级编程语言...",
    "category": "python",
    "tags": ["python", "基础", "入门"],
    "version": 3,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-10T12:00:00Z",
    "checksum": "a1b2c3d4e5f6",
    "author": "admin"
  }
]
```

### 4. 获取单个知识条目

获取指定 ID 的知识条目。

- **URL**: `/api/v1/knowledge/{id}`
- **方法**: `GET`
- **认证**: 需要

**响应示例**:
```json
{
  "id": "python-basics",
  "title": "Python 基础知识",
  "content": "Python 是一种高级编程语言...",
  "category": "python",
  "tags": ["python", "基础", "入门"],
  "version": 3,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-10T12:00:00Z",
  "checksum": "a1b2c3d4e5f6",
  "author": "admin"
}
```

### 5. 创建知识条目

创建新的知识条目。

- **URL**: `/api/v1/knowledge`
- **方法**: `POST`
- **认证**: 需要

**请求体**:
```json
{
  "title": "新的知识条目",
  "content": "这是知识条目的内容...",
  "category": "general",
  "tags": ["标签1", "标签2"],
  "author": "username"
}
```

**响应示例**:
```json
{
  "id": "new-knowledge-item",
  "title": "新的知识条目",
  "content": "这是知识条目的内容...",
  "category": "general",
  "tags": ["标签1", "标签2"],
  "version": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "checksum": "f6e5d4c3b2a1",
  "author": "username"
}
```

### 6. 更新知识条目

更新指定的知识条目。

- **URL**: `/api/v1/knowledge/{id}`
- **方法**: `PUT`
- **认证**: 需要

**请求体**:
```json
{
  "title": "更新后的标题",
  "content": "更新后的内容...",
  "category": "python",
  "tags": ["python", "更新"]
}
```

**响应示例**:
```json
{
  "id": "python-basics",
  "title": "更新后的标题",
  "content": "更新后的内容...",
  "category": "python",
  "tags": ["python", "更新"],
  "version": 4,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z",
  "checksum": "1a2b3c4d5e6f",
  "author": "admin"
}
```

### 7. 删除知识条目

删除指定的知识条目。

- **URL**: `/api/v1/knowledge/{id}`
- **方法**: `DELETE`
- **认证**: 需要

**响应示例**:
```json
{
  "message": "删除成功"
}
```

### 8. 获取分类列表

获取所有可用的分类。

- **URL**: `/api/v1/categories`
- **方法**: `GET`
- **认证**: 需要

**响应示例**:
```json
["python", "javascript", "general", "tips"]
```

### 9. 获取标签列表

获取所有可用的标签。

- **URL**: `/api/v1/tags`
- **方法**: `GET`
- **认证**: 需要

**响应示例**:
```json
["python", "基础", "进阶", "最佳实践", "入门"]
```

## 错误处理

所有错误响应都应遵循以下格式：

```json
{
  "error": true,
  "code": "ERROR_CODE",
  "message": "人类可读的错误描述"
}
```

### 常见错误码

- `400` - 请求参数错误
- `401` - 未授权（API Key 无效或缺失）
- `403` - 禁止访问
- `404` - 资源不存在
- `500` - 服务器内部错误

## 数据模型

### KnowledgeItem (知识条目)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | string | 唯一标识符 |
| title | string | 标题 |
| content | string | 内容（支持 Markdown） |
| category | string | 分类 |
| tags | array[string] | 标签列表 |
| version | integer | 版本号 |
| created_at | string (ISO 8601) | 创建时间 |
| updated_at | string (ISO 8601) | 更新时间 |
| checksum | string | 内容校验和（MD5） |
| author | string | 作者（可选） |

## 示例服务器实现

以下是一个使用 Python Flask 的简单服务器实现示例：

```python
from flask import Flask, request, jsonify
from functools import wraps
import hashlib
import time
from datetime import datetime

app = Flask(__name__)

# 配置
API_KEYS = {"your-api-key-here": "admin"}  # 在实际应用中使用数据库存储
KNOWLEDGE_ITEMS = {}  # 在实际应用中使用数据库存储

# 认证装饰器
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": True, "message": "缺少认证信息"}), 401
        
        api_key = auth_header[7:]  # 去掉 "Bearer "
        if api_key not in API_KEYS:
            return jsonify({"error": True, "message": "无效的 API Key"}), 401
        
        return f(*args, **kwargs)
    return decorated

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/v1/info', methods=['GET'])
@require_auth
def get_info():
    categories = set(item['category'] for item in KNOWLEDGE_ITEMS.values())
    return jsonify({
        "name": "BBCode Cloud KB Server",
        "version": "1.0.0",
        "total_items": len(KNOWLEDGE_ITEMS),
        "categories": list(categories)
    })

@app.route('/api/v1/knowledge', methods=['GET'])
@require_auth
def list_knowledge():
    items = list(KNOWLEDGE_ITEMS.values())
    
    # 应用筛选
    category = request.args.get('category')
    if category:
        items = [item for item in items if item['category'] == category]
    
    tags = request.args.get('tags')
    if tags:
        tag_list = tags.split(',')
        items = [item for item in items if any(tag in item['tags'] for tag in tag_list)]
    
    search = request.args.get('search')
    if search:
        search_lower = search.lower()
        items = [item for item in items 
                if search_lower in item['title'].lower() 
                or search_lower in item['content'].lower()]
    
    return jsonify(items)

@app.route('/api/v1/knowledge/<item_id>', methods=['GET'])
@require_auth
def get_knowledge(item_id):
    item = KNOWLEDGE_ITEMS.get(item_id)
    if not item:
        return jsonify({"error": True, "message": "知识条目不存在"}), 404
    return jsonify(item)

@app.route('/api/v1/knowledge', methods=['POST'])
@require_auth
def create_knowledge():
    data = request.json
    
    # 生成 ID
    item_id = data['title'].lower().replace(' ', '-')[:50]
    
    # 创建条目
    item = {
        "id": item_id,
        "title": data['title'],
        "content": data['content'],
        "category": data.get('category', 'general'),
        "tags": data.get('tags', []),
        "version": 1,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "checksum": hashlib.md5(f"{data['title']}{data['content']}1".encode()).hexdigest(),
        "author": data.get('author', 'unknown')
    }
    
    KNOWLEDGE_ITEMS[item_id] = item
    return jsonify(item), 201

@app.route('/api/v1/knowledge/<item_id>', methods=['PUT'])
@require_auth
def update_knowledge(item_id):
    item = KNOWLEDGE_ITEMS.get(item_id)
    if not item:
        return jsonify({"error": True, "message": "知识条目不存在"}), 404
    
    data = request.json
    
    # 更新字段
    if 'title' in data:
        item['title'] = data['title']
    if 'content' in data:
        item['content'] = data['content']
    if 'category' in data:
        item['category'] = data['category']
    if 'tags' in data:
        item['tags'] = data['tags']
    
    item['version'] += 1
    item['updated_at'] = datetime.now().isoformat()
    item['checksum'] = hashlib.md5(
        f"{item['title']}{item['content']}{item['version']}".encode()
    ).hexdigest()
    
    return jsonify(item)

@app.route('/api/v1/knowledge/<item_id>', methods=['DELETE'])
@require_auth
def delete_knowledge(item_id):
    if item_id not in KNOWLEDGE_ITEMS:
        return jsonify({"error": True, "message": "知识条目不存在"}), 404
    
    del KNOWLEDGE_ITEMS[item_id]
    return jsonify({"message": "删除成功"})

@app.route('/api/v1/categories', methods=['GET'])
@require_auth
def get_categories():
    categories = set(item['category'] for item in KNOWLEDGE_ITEMS.values())
    return jsonify(list(categories))

@app.route('/api/v1/tags', methods=['GET'])
@require_auth
def get_tags():
    tags = set()
    for item in KNOWLEDGE_ITEMS.values():
        tags.update(item['tags'])
    return jsonify(list(tags))

if __name__ == '__main__':
    # 添加一些示例数据
    KNOWLEDGE_ITEMS['python-basics'] = {
        "id": "python-basics",
        "title": "Python 基础知识",
        "content": "Python 是一种高级编程语言，具有简洁易读的语法...",
        "category": "python",
        "tags": ["python", "基础", "入门"],
        "version": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "checksum": "abc123",
        "author": "admin"
    }
    
    app.run(debug=True, port=5000)
```

## 部署建议

1. **使用 HTTPS**: 生产环境必须使用 HTTPS 保护 API 通信
2. **API Key 管理**: 使用安全的 API Key 生成和存储机制
3. **数据备份**: 定期备份知识库数据
4. **访问控制**: 实施适当的访问控制和速率限制
5. **日志记录**: 记录重要操作以便审计

## 客户端配置

在 BBCode 中配置云知识库：

1. 打开 **工具** → **云知识库设置**
2. 输入服务器地址（例如：`https://your-server.com`）
3. 输入 API 密钥
4. 点击 **测试连接** 验证配置
5. 启用 **云端同步**
6. 点击 **立即同步** 开始同步
