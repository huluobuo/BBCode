"""
Ollama配置界面
提供Ollama服务器地址和模型设置
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from thonny import get_workbench
from thonny.ui_utils import show_dialog


class OllamaConfigDialog(tk.Toplevel):
    """Ollama配置对话框"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Ollama配置")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()
        
        self._create_ui()
        self._load_settings()
        
        # 居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
    
    def _create_ui(self):
        """创建UI界面"""
        # 主框架
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="Ollama服务器配置", 
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 服务器地址
        server_frame = ttk.LabelFrame(main_frame, text="服务器设置", padding="10")
        server_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 主机地址
        ttk.Label(server_frame, text="主机地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.host_entry = ttk.Entry(server_frame, width=30)
        self.host_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        ttk.Label(server_frame, text="例如: 127.0.0.1 或 localhost", foreground="gray").grid(
            row=0, column=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        
        # 端口
        ttk.Label(server_frame, text="端口:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(server_frame, width=30)
        self.port_entry.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        ttk.Label(server_frame, text="例如: 11434", foreground="gray").grid(
            row=1, column=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        
        server_frame.columnconfigure(1, weight=1)
        
        # 模型设置
        model_frame = ttk.LabelFrame(main_frame, text="模型设置", padding="10")
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(model_frame, text="模型名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.model_entry = ttk.Entry(model_frame, width=30)
        self.model_entry.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=5)
        ttk.Label(model_frame, text="例如: gemma3:1b, llama3, qwen2.5", foreground="gray").grid(
            row=0, column=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        
        model_frame.columnconfigure(1, weight=1)
        
        # 知识库设置
        kb_frame = ttk.LabelFrame(main_frame, text="知识库设置", padding="10")
        kb_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.use_kb_var = tk.BooleanVar(value=True)
        self.use_kb_check = ttk.Checkbutton(
            kb_frame, 
            text="启用知识库", 
            variable=self.use_kb_var
        )
        self.use_kb_check.pack(anchor=tk.W)
        
        ttk.Label(
            kb_frame, 
            text="启用后，AI会自动检索相关知识库内容来回答问题",
            foreground="gray",
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(btn_frame, text="测试连接", command=self._test_connection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="恢复默认", command=self._reset_defaults).pack(side=tk.LEFT)
        
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_frame, text="保存", command=self._save_settings).pack(side=tk.RIGHT)
    
    def _load_settings(self):
        """加载当前设置"""
        wb = get_workbench()
        
        host = wb.get_option("assistance.ollama_host", "127.0.0.1")
        port = wb.get_option("assistance.ollama_port", "11434")
        model = wb.get_option("assistance.ollama_model", "gemma3:1b")
        use_kb = wb.get_option("assistance.use_knowledge", True)
        
        self.host_entry.delete(0, tk.END)
        self.host_entry.insert(0, host)
        
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, port)
        
        self.model_entry.delete(0, tk.END)
        self.model_entry.insert(0, model)
        
        self.use_kb_var.set(use_kb)
    
    def _save_settings(self):
        """保存设置"""
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        model = self.model_entry.get().strip()
        use_kb = self.use_kb_var.get()
        
        # 验证输入
        if not host:
            messagebox.showerror("错误", "请输入主机地址")
            return
        
        if not port:
            messagebox.showerror("错误", "请输入端口")
            return
        
        if not model:
            messagebox.showerror("错误", "请输入模型名称")
            return
        
        try:
            int(port)
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字")
            return
        
        # 保存设置
        wb = get_workbench()
        wb.set_option("assistance.ollama_host", host)
        wb.set_option("assistance.ollama_port", port)
        wb.set_option("assistance.ollama_model", model)
        wb.set_option("assistance.use_knowledge", use_kb)
        
        messagebox.showinfo("成功", "设置已保存\n\n请重启Thonny以使更改生效")
        self.destroy()
    
    def _test_connection(self):
        """测试Ollama连接"""
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        model = self.model_entry.get().strip()
        
        if not host or not port:
            messagebox.showwarning("提示", "请先输入主机地址和端口")
            return
        
        try:
            import urllib.request
            import json
            
            # 测试连接
            url = f"http://{host}:{port}/api/tags"
            
            self.config(cursor="wait")
            self.update()
            
            try:
                with urllib.request.urlopen(url, timeout=5) as response:
                    data = json.loads(response.read().decode())
                    models = [m.get("name", "") for m in data.get("models", [])]
                    
                    if model in models:
                        messagebox.showinfo(
                            "连接成功", 
                            f"成功连接到Ollama服务器\n\n可用模型:\n" + "\n".join(models[:10])
                        )
                    else:
                        messagebox.showwarning(
                            "模型未找到",
                            f"已连接到服务器，但未找到模型 '{model}'\n\n可用模型:\n" + "\n".join(models[:10])
                        )
            except urllib.error.URLError as e:
                messagebox.showerror("连接失败", f"无法连接到Ollama服务器:\n{e}")
            except Exception as e:
                messagebox.showerror("错误", f"测试连接时出错:\n{e}")
            finally:
                self.config(cursor="")
                
        except ImportError:
            messagebox.showerror("错误", "缺少必要的模块")
    
    def _reset_defaults(self):
        """恢复默认设置"""
        if messagebox.askyesno("确认", "确定要恢复默认设置吗？"):
            self.host_entry.delete(0, tk.END)
            self.host_entry.insert(0, "127.0.0.1")
            
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, "11434")
            
            self.model_entry.delete(0, tk.END)
            self.model_entry.insert(0, "gemma3:1b")
            
            self.use_kb_var.set(True)


def open_ollama_config_dialog():
    """打开Ollama配置对话框"""
    from thonny import get_workbench
    dialog = OllamaConfigDialog(get_workbench())
    show_dialog(dialog, master=get_workbench())


def load_plugin():
    """加载插件"""
    from thonny import get_workbench
    
    # 在工具菜单中添加Ollama配置
    get_workbench().add_command(
        "open_ollama_config",
        "tools",
        "Ollama配置",
        open_ollama_config_dialog,
        group=10
    )
