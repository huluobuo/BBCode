# BBCode 云知识库服务器（简化版）

无需 API 认证，适合本地或内网使用的云知识库服务器。

## 特点

- 🔓 **无需认证**：开箱即用，无需配置 API Key
- 🎨 **Web 管理界面**：内置美观的管理后台，支持 Markdown 实时预览
- 📝 **Markdown 支持**：完整的 Markdown 编辑、预览、导入导出
- 👁️ **实时预览**：编辑时实时查看 Markdown 渲染效果
- 📥 **导入导出**：支持 JSON 和 Markdown 文件导入导出
- 📄 **文档转换**：支持 PDF、Word、TXT 导入并自动转换为 Markdown
- 📱 **跨平台**：支持 Windows、macOS、Linux
- 🔄 **实时同步**：支持 BBCode 客户端实时同步
- 💾 **本地存储**：数据以 JSON 格式本地存储

## 快速开始

### 1. 安装依赖

确保已安装 Python 3.7+，然后安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

**Windows:**
```bash
start_server.bat
```

**macOS/Linux:**
```bash
chmod +x start_server.sh
./start_server.sh
```

**或者直接使用 Python:**
```bash
python server.py
```

### 3. 访问管理界面

打开浏览器访问：http://localhost:5000

## 管理界面功能

### Markdown 编辑器

管理界面提供强大的 Markdown 编辑功能：

- **分屏编辑**：左侧编辑，右侧实时预览
- **工具栏**：快速插入常用 Markdown 语法
  - 粗体、斜体
  - 标题（H1-H3）
  - 列表（有序/无序）
  - 代码块
  - 引用
  - 链接、图片
  - 分隔线
- **模板插入**：一键插入文章模板
- **GitHub 风格**：使用 GitHub Markdown CSS 样式

### 导入导出

**导出功能：**
- 点击"导出全部"按钮
- 下载 JSON 格式的备份文件
- 包含所有知识条目和元数据

**导入功能：**
- 支持导入 JSON 文件（从本系统导出）
- 支持导入 Markdown 文件（.md）
- 自动解析并创建知识条目

### 文档导入转换

支持将各种文档格式自动转换为 Markdown：

**支持的格式：**
- 📕 **PDF** (.pdf) - 提取文本并保留页面结构
- 📘 **Word** (.docx, .doc) - 保留标题、列表、表格格式
- 📄 **文本** (.txt) - 直接转换为 Markdown

**使用方法：**
1. 点击"导入文档"按钮
2. 选择要导入的文件（PDF、Word 或 TXT）
3. 系统自动转换并创建知识条目
4. 转换后的内容保留原始文档的结构和格式

**转换特点：**
- 自动检测文档标题
- 保留段落和列表格式
- Word 表格转换为 Markdown 表格
- PDF 按页组织内容
- 添加导入来源标签

### 查看页面

每个知识条目都有独立的查看页面：
- 美观的 Markdown 渲染
- 显示分类、标签、更新时间
- 支持从查看页面直接编辑

## 在 BBCode 中使用

### 本机使用

1. 打开 BBCode 应用
2. 点击 **对话管理 ▼** → **知识库** → **云知识库设置...**
3. 输入服务器地址：`http://localhost:5000`
4. **API 密钥留空**（因为是简化版，无需认证）
5. 点击 **测试连接**，应该显示"连接成功（无需认证）"
6. 勾选 **启用云端同步**
7. 点击 **保存设置**
8. 点击 **立即同步** 开始同步

### 局域网共享使用 👥

服务器启动后会自动显示局域网 IP 地址，例如：

```
🌐 访问地址:
   本机访问: http://127.0.0.1:5000
   本机访问: http://localhost:5000
   局域网访问: http://192.168.1.100:5000  ← 其他设备使用这个地址
```

**其他电脑/设备连接步骤：**

1. 确保服务器电脑和其他设备在同一局域网
2. 在 BBCode 设置中输入服务器地址：`http://192.168.1.100:5000`（替换为实际IP）
3. API 密钥留空
4. 点击测试连接，确认连接成功
5. 保存设置并开始同步

**注意：** 如果连接失败，请检查 Windows 防火墙设置，确保允许 Python 通过防火墙。

## 数据存储

服务器数据存储在 `data/` 目录下：

- `data/knowledge.json` - 知识库数据
- `data/uploads/` - 上传的文件

## API 接口

服务器提供以下 REST API：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/knowledge` | GET | 获取所有知识条目 |
| `/api/v1/knowledge` | POST | 创建知识条目 |
| `/api/v1/knowledge/<id>` | GET | 获取单个知识条目 |
| `/api/v1/knowledge/<id>` | PUT | 更新知识条目 |
| `/api/v1/knowledge/<id>` | DELETE | 删除知识条目 |
| `/api/v1/categories` | GET | 获取分类列表 |
| `/api/v1/tags` | GET | 获取标签列表 |

## 配置选项

编辑 `server.py` 可以修改以下配置：

```python
# 数据目录
DATA_DIR = Path(__file__).parent / "data"

# 服务器端口（在底部修改）
app.run(host='0.0.0.0', port=5000, debug=True)
```

## 生产环境部署

### 使用 Gunicorn（Linux/macOS）

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### 使用 Waitress（Windows）

```bash
pip install waitress
waitress-serve --port=5000 server:app
```

### 后台运行

**Windows（使用 NSSM）:**
```bash
nssm install CloudKB "C:\Python39\python.exe" "C:\CloudKB\server.py"
```

**Linux（使用 systemd）:**
创建 `/etc/systemd/system/cloudkb.service`:

```ini
[Unit]
Description=BBCode Cloud KB Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/cloudkb
ExecStart=/usr/bin/python3 /opt/cloudkb/server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

然后：
```bash
sudo systemctl enable cloudkb
sudo systemctl start cloudkb
```

## 局域网共享详细指南

### 网络要求

- 所有设备连接到同一路由器/交换机
- 服务器电脑的防火墙允许 5000 端口（或自定义端口）
- 设备之间可以互相 ping 通

### 查找服务器 IP 地址

服务器启动时会自动显示局域网 IP，也可以手动查找：

**Windows:**
```cmd
ipconfig
```
查找 "IPv4 地址"，通常是 `192.168.x.x` 或 `10.0.x.x`

**macOS/Linux:**
```bash
ifconfig
# 或
ip addr
```

### 防火墙设置

**Windows 防火墙设置：**

1. 打开 "Windows Defender 防火墙"
2. 点击 "允许应用通过防火墙"
3. 点击 "更改设置"
4. 找到 Python 或 Python.exe，勾选 "专用" 和 "公用"
5. 或者添加端口规则：
   - 选择 "入站规则" → "新建规则"
   - 选择 "端口" → "TCP"
   - 输入端口 `5000`
   - 选择 "允许连接"
   - 应用规则

**临时关闭防火墙（仅测试）：**
```cmd
netsh advfirewall set allprofiles state off
```
测试完成后记得重新开启！

### 测试连接

在其他设备上测试是否能访问服务器：

```bash
# 测试网络连通性
ping 192.168.1.100

# 测试端口连通性（Windows）
telnet 192.168.1.100 5000

# 或使用浏览器访问
http://192.168.1.100:5000
```

### 多台设备同时使用

✅ **支持场景：**
- 多人同时查看知识库
- 多人同时同步到本地
- 通过 Web 界面管理内容

⚠️ **注意事项：**
- 同时编辑同一条目可能导致数据覆盖
- 建议协商好编辑分工
- 定期刷新页面查看最新内容

### 移动端访问

手机/平板也可以访问：
1. 确保手机连接同一 WiFi
2. 浏览器访问 `http://服务器IP:5000`
3. 或使用 BBCode（如果支持移动端）

## 故障排除

### 端口被占用

如果 5000 端口被占用，使用其他端口：

```bash
# 使用 8080 端口
python server.py --port 8080
```

### 无法访问

**本机可以访问，其他设备无法访问：**

1. 检查防火墙设置（最常见原因）
2. 确认服务器启动参数包含 `host='0.0.0.0'`
3. 检查是否在同一网段
4. 尝试关闭防火墙测试

**连接超时：**
- 检查 IP 地址是否正确
- 确认服务器正在运行
- 检查网络连接

**数据丢失**

定期备份 `data/knowledge.json` 文件。

## 安全提示

⚠️ **注意**：简化版服务器没有认证机制，仅建议在以下场景使用：

- 本地开发环境
- 受信任的内网环境
- 个人使用

如需对外提供服务，建议：
1. 使用反向代理（Nginx/Apache）
2. 配置 HTTPS
3. 添加 IP 白名单
4. 或切换到需要认证的版本

## 更新日志

### v1.0.0
- 初始版本
- 无认证设计
- 内置 Web 管理界面
- 支持完整的 CRUD 操作
