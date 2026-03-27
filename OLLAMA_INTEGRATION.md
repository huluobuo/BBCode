# BBCode Ollama 集成指南

## 🎉 Ollama 集成完成

BBCode 现在支持本地 Ollama AI 模型！

---

## 📋 前置要求

### 1. 安装 Ollama

**Windows:**
```powershell
# 下载安装程序
# https://ollama.com/download/windows

# 或使用命令行
winget install Ollama.Ollama
```

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. 启动 Ollama 服务

```bash
# 在终端运行
ollama serve
```

### 3. 下载模型

```bash
# 推荐代码模型
ollama pull qwen2.5-coder:7b

# 或其他模型
ollama pull llama3.2
ollama pull codellama:7b
ollama pull deepseek-coder:6.7b
```

---

## 🚀 使用说明

### 启动 BBCode PyQt6 版本

```bash
d:\code\BBCode\python\python.exe thonny\qt_main.py
```

### AI 聊天功能

1. **自动检测**: 启动时会自动检测 Ollama 状态
2. **模型选择**: 在聊天输入框右侧选择可用模型
3. **发送消息**: 输入问题后点击"发送"或按回车
4. **流式响应**: AI 回复会实时显示
5. **停止生成**: 点击"停止"按钮可中断生成

### 快捷操作

- **解释代码**: 解释选中代码的功能
- **优化代码**: 优化代码性能和可读性
- **生成注释**: 为代码添加详细注释
- **修复错误**: 检查并修复代码错误

---

## 🔧 配置文件

### 默认设置

```python
# Ollama 默认配置
host = "http://localhost:11434"
default_model = "qwen2.5-coder:7b"

# 生成参数
temperature = 0.7
top_p = 0.9
top_k = 40
num_predict = 2048
```

### 系统提示词

```
You are a helpful AI programming assistant. You help users with Python programming questions.

When answering:
1. Provide clear, concise explanations
2. Use code examples when helpful
3. Format code blocks with ```python
4. Be friendly and encouraging
5. If the user asks in Chinese, respond in Chinese

Current context: You are integrated into BBCode, a Python IDE.
```

---

## 📁 新增文件

| 文件 | 说明 | 行数 |
|------|------|------|
| `plugins/ollama_client.py` | Ollama API 客户端 | 333 |
| `plugins/qt_chat.py` | 更新后的聊天组件 | 580+ |

---

## 🔌 API 接口

### OllamaAPI 类

```python
from plugins.ollama_client import OllamaAPI

# 创建客户端
api = OllamaAPI()

# 检查可用性
if api.is_available():
    # 列出模型
    models = api.list_models()
    
    # 生成文本
    response = api.generate("Hello!")
    
    # 流式生成
    for chunk in api.generate_stream("Tell me a story"):
        print(chunk, end="")
```

### OllamaChatManager 类

```python
from plugins.ollama_client import OllamaChatManager

# 创建管理器
chat = OllamaChatManager()

# 设置模型
chat.set_model("qwen2.5-coder:7b")

# 发送消息（异步）
chat.send_message("解释这段代码", code_context="def foo(): pass")

# 连接信号
chat.message_chunk.connect(lambda chunk: print(chunk))
chat.error_occurred.connect(lambda err: print(f"Error: {err}"))
```

---

## 🐛 故障排除

### Ollama 未启动

**错误信息:**
```
Ollama 未启动。请运行: ollama serve
```

**解决方案:**
```bash
# 在终端运行
ollama serve
```

### 模型未找到

**错误信息:**
```
Ollama 已连接，但未找到模型
```

**解决方案:**
```bash
# 下载模型
ollama pull qwen2.5-coder:7b
```

### 连接超时

**错误信息:**
```
Request failed: <urlopen error [WinError 10061] ...>
```

**解决方案:**
1. 检查 Ollama 服务是否运行
2. 检查防火墙设置
3. 确认端口 11434 未被占用

---

## 🎯 功能特性

### ✅ 已实现
- [x] Ollama 服务自动检测
- [x] 模型列表获取
- [x] 流式响应（实时显示）
- [x] 模型选择下拉框
- [x] 停止生成按钮
- [x] 错误处理
- [x] 系统提示词配置

### 🚧 计划中
- [ ] 对话历史保存
- [ ] 自定义系统提示词
- [ ] 参数调节（temperature 等）
- [ ] 多轮对话上下文
- [ ] 代码片段自动提取

---

## 📊 性能说明

- **本地运行**: 所有 AI 推理在本地完成，无需联网
- **流式响应**: 实时显示生成内容，无需等待完整响应
- **后台线程**: AI 请求在后台线程执行，不阻塞 UI
- **内存占用**: 取决于所选模型（7B 模型约需 4-8GB 内存）

---

## 🔗 相关链接

- [Ollama 官网](https://ollama.com)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [可用模型列表](https://ollama.com/library)

---

## 💡 推荐模型

| 模型 | 大小 | 特点 | 适用场景 |
|------|------|------|----------|
| qwen2.5-coder:7b | 4.5GB | 代码能力强，中文好 | 通用编程 |
| codellama:7b | 3.8GB | Meta 出品，代码专用 | 代码生成 |
| deepseek-coder:6.7b | 3.8GB | 国产，代码能力强 | 中文编程 |
| llama3.2:3b | 2.0GB | 轻量级，速度快 | 简单任务 |

---

## 🎊 总结

BBCode 现在拥有完整的本地 AI 编程助手功能：

1. ✅ 自动检测 Ollama 服务
2. ✅ 支持所有 Ollama 模型
3. ✅ 流式实时响应
4. ✅ 代码解释/优化/注释/修复
5. ✅ 后台线程不卡顿

**享受本地 AI 编程助手吧！** 🚀
