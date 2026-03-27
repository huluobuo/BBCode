# BBCode - Python IDE

基于 PyQt6 的现代化 Python 集成开发环境。

## 功能特性

### 代码编辑器
- ✅ 行号显示
- ✅ Python 语法高亮
- ✅ 实时语法检查（红色下划线标记错误）
- ✅ 多标签页编辑
- ✅ 自动保存历史

### 文件浏览器
- ✅ 树形文件浏览
- ✅ 上一级文件夹导航
- ✅ 双击打开文件
- ✅ 路径显示

### AI 助手
- ✅ Ollama 本地模型支持
- ✅ 流式实时响应
- ✅ 消息气泡界面
- ✅ 代码块高亮

### 终端
- ✅ Python Shell
- ✅ 系统命令执行
- ✅ 命令历史

## 项目结构

```
BBCode/
├── bbcode/                 # 核心代码包
│   ├── __init__.py        # 包初始化
│   ├── editor.py          # 代码编辑器（行号、语法高亮、语法检查）
│   ├── filebrowser.py     # 文件浏览器
│   ├── terminal.py        # 终端组件
│   ├── ai_chat.py         # AI 聊天组件
│   └── main_window.py     # 主窗口
├── main.py                # 程序入口
└── README.md              # 说明文档
```

## 运行方式

### 使用系统 Python
```bash
python main.py
```

### 使用项目内置 Python
```bash
python\python.exe main.py
```

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+N | 新建文件 |
| Ctrl+O | 打开文件 |
| Ctrl+S | 保存文件 |
| Ctrl+Shift+S | 另存为 |
| Ctrl+Z | 撤销 |
| Ctrl+Y | 重做 |
| Ctrl+X | 剪切 |
| Ctrl+C | 复制 |
| Ctrl+V | 粘贴 |
| F5 | 运行代码 |
| Ctrl+Enter | AI 聊天发送 |

## AI 助手使用

1. 确保已安装并启动 Ollama:
   ```bash
   ollama serve
   ```

2. 下载推荐模型:
   ```bash
   ollama pull qwen2.5-coder:7b
   ```

3. 启动 BBCode，AI 助手会自动连接 Ollama

## 依赖

- Python 3.8+
- PyQt6

安装依赖:
```bash
pip install PyQt6
```

## 版本历史

### v3.0.0
- 重构项目结构，精简代码
- 整合所有功能到核心模块
- 优化性能和用户体验

## 许可证

MIT License
