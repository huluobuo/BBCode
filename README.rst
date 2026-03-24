BBCode - 基于 Thonny 的 Python IDE
================================

BBCode 是一个基于 Thonny Python IDE 的定制版本，专为 Python 开发者和教育用途设计。

.. image:: res/bbc.png
   :width: 200
   :alt: BBCode Logo

特性
----

- 🚀 **基于 Thonny 的稳定基础** - 继承 Thonny 的所有优秀特性
- 🎨 **自定义主题支持** - 内置深色/浅色主题切换
- 🔧 **集成开发环境** - 完整的 Python 开发工具链
- 📚 **教育友好** - 适合初学者和教育用途
- 🔍 **调试功能** - 内置调试器和变量查看器
- 📦 **包管理** - 集成 pip 包管理器
- 🌐 **多语言支持** - 支持中文界面

系统要求
--------

- **操作系统**: Windows 10 +
- **Python 版本**: 支持 Python 3.9, 3.10, 3.11, 3.12, 3.13
- **内存**: 最低 2GB RAM，推荐 4GB 或以上
- **磁盘空间**: 至少 200MB 可用空间

快速开始
--------

### Windows 用户

1. 下载并解压 BBCode 发行包
2. 双击运行 `BBCode.bat` (控制台模式) 或 `BBCodew.bat` (无控制台模式)
3. 开始编写 Python 代码！

### 从源代码运行

如果您有 Python 环境，可以直接运行：

```bash
python launcher.py
```

项目结构
--------

```
BBCode/
├── thonny/           # Thonny 核心代码
├── plugins/          # 插件目录
│   └── bbcode_info.py # BBCode 信息面板插件
├── python/           # 内置 Python 解释器
├── res/             # 资源文件（图标、图片等）
├── BBCode.bat       # Windows 启动脚本（控制台）
├── BBCodew.bat      # Windows 启动脚本（无控制台）
├── launcher.py      # 主启动程序
└── VERSION          # 版本信息
```

插件系统
--------

BBCode 支持丰富的插件系统，当前包含以下插件：

- **BBCode 信息面板** - 显示版本信息和主题切换
- **调试器** - 集成调试功能
- **包管理器** - pip 包管理界面
- **AI助手** - 智能AI辅助代码
- **语法高亮** - 多语言语法支持

自定义开发
----------

### 添加新插件

在 `plugins/` 目录下创建新的 Python 文件：

```python
from thonny import get_workbench

def my_plugin_function():
    # 你的插件逻辑
    pass

def load_plugin():
    # 插件加载逻辑
    get_workbench().add_command(...)
```

### 修改主题

BBCode 支持自定义主题，可以通过修改插件或配置文件来实现主题定制。

版本信息
--------

- **当前版本**: 5.0.0b1.dev0
- **基于 Thonny**: 最新稳定版本
- **Python 支持**: 3.9-3.13

许可证
------

BBCode 基于 Thonny 开发，遵循相应的开源许可证。详细信息请查看 `LICENSE.txt` 文件。

贡献
----

欢迎贡献代码和报告问题！

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

常见问题
--------

### Q: 如何切换主题？
A: 点击界面右下角的主题切换按钮（🌙/☀️）

### Q: 如何安装第三方包？
A: 使用内置的包管理器或通过 Tools → Manage packages

### Q: 如何调试代码？
A: 使用调试工具栏或按 F5 开始调试

### Q: 支持哪些 Python 版本？
A: 支持 Python 3.9 到 3.13

技术支持
--------

如果您遇到问题或需要帮助，请：

1. 查看项目文档
2. 检查现有问题
3. 创建新的 issue

更新日志
--------

相关链接
--------

- [Thonny 官方网站](https://thonny.org)
- [Python 官方网站](https://python.org)
- [BBCode 项目仓库](https://github.com/huluobuo/bbcode)

---

*BBCode - 让 Python 编程更简单*