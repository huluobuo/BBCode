"""
知识库UI界面
提供知识库管理界面
"""

import os
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog, ttk
from typing import Optional

from thonny import get_workbench
from thonny.plugins.knowledge_base import get_knowledge_base, reload_knowledge_base
from thonny.ui_utils import ems_to_pixels, show_dialog


class KnowledgeBaseDialog(tk.Toplevel):
    """知识库管理对话框"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("知识库管理")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()

        self.kb = get_knowledge_base()

        self._create_ui()
        self._refresh_file_list()

    def _create_ui(self):
        """创建UI界面"""
        # 主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部信息
        info_frame = ttk.LabelFrame(main_frame, text="知识库信息", padding="5")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        self.info_label = ttk.Label(info_frame, text=f"知识库目录: {self.kb.kb_dir}")
        self.info_label.pack(anchor=tk.W)

        self.count_label = ttk.Label(info_frame, text="文件数量: 0")
        self.count_label.pack(anchor=tk.W)

        # 文件列表
        list_frame = ttk.LabelFrame(main_frame, text="知识文件", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 文件列表和滚动条
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(list_container, selectmode=tk.SINGLE, font=("Segoe UI", 10))
        scrollbar = ttk.Scrollbar(
            list_container, orient=tk.VERTICAL, command=self.file_listbox.yview
        )
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox.bind("<<ListboxSelect>>", self._on_file_select)
        self.file_listbox.bind("<Double-Button-1>", self._on_file_double_click)

        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="新建文件", command=self._create_new_file).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="刷新", command=self._refresh_file_list).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="删除", command=self._delete_selected_file).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(btn_frame, text="打开目录", command=self._open_kb_directory).pack(side=tk.LEFT)

        # 内容预览
        preview_frame = ttk.LabelFrame(main_frame, text="内容预览", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True)

        self.preview_text = scrolledtext.ScrolledText(
            preview_frame, wrap=tk.WORD, font=("Consolas", 9), height=10, state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # 关闭按钮
        ttk.Button(main_frame, text="关闭", command=self.destroy).pack(pady=(10, 0))

    def _refresh_file_list(self):
        """刷新文件列表"""
        self.file_listbox.delete(0, tk.END)
        files = self.kb.list_knowledge_files()

        for filename in files:
            self.file_listbox.insert(tk.END, filename)

        self.count_label.config(text=f"文件数量: {len(files)}")

        # 清空预览
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.config(state=tk.DISABLED)

    def _on_file_select(self, event):
        """文件选择事件"""
        selection = self.file_listbox.curselection()
        if not selection:
            return

        filename = self.file_listbox.get(selection[0])
        self._show_file_preview(filename)

    def _on_file_double_click(self, event):
        """文件双击事件"""
        selection = self.file_listbox.curselection()
        if not selection:
            return

        filename = self.file_listbox.get(selection[0])
        self._edit_file(filename)

    def _show_file_preview(self, filename: str):
        """显示文件预览"""
        filepath = os.path.join(self.kb.kb_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # 限制预览长度
            if len(content) > 1000:
                content = content[:1000] + "\n\n... (内容已截断)"

            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", content)
            self.preview_text.config(state=tk.DISABLED)

        except Exception as e:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", f"无法读取文件: {e}")
            self.preview_text.config(state=tk.DISABLED)

    def _create_new_file(self):
        """创建新文件"""
        dialog = NewKnowledgeDialog(self)
        if dialog.result:
            title, content = dialog.result
            try:
                filepath = self.kb.add_knowledge(title, content)
                filename = os.path.basename(filepath)
                self._refresh_file_list()

                # 选中新文件
                for i in range(self.file_listbox.size()):
                    if self.file_listbox.get(i) == filename:
                        self.file_listbox.selection_set(i)
                        self.file_listbox.see(i)
                        break

                messagebox.showinfo("成功", f"知识文件已创建: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"创建文件失败: {e}")

    def _delete_selected_file(self):
        """删除选中的文件"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个文件")
            return

        filename = self.file_listbox.get(selection[0])

        if messagebox.askyesno("确认删除", f"确定要删除文件 '{filename}' 吗？"):
            try:
                if self.kb.delete_knowledge_file(filename):
                    self._refresh_file_list()
                    messagebox.showinfo("成功", "文件已删除")
                else:
                    messagebox.showerror("错误", "删除文件失败")
            except Exception as e:
                messagebox.showerror("错误", f"删除文件失败: {e}")

    def _edit_file(self, filename: str):
        """编辑文件"""
        filepath = os.path.join(self.kb.kb_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            dialog = EditKnowledgeDialog(self, filename, content)
            if dialog.result is not None:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(dialog.result)
                reload_knowledge_base()
                self._show_file_preview(filename)
                messagebox.showinfo("成功", "文件已保存")

        except Exception as e:
            messagebox.showerror("错误", f"编辑文件失败: {e}")

    def _open_kb_directory(self):
        """打开知识库目录"""
        import platform
        import subprocess

        try:
            if platform.system() == "Windows":
                subprocess.run(["explorer", self.kb.kb_dir], check=True)
            elif platform.system() == "Darwin":
                subprocess.run(["open", self.kb.kb_dir], check=True)
            else:
                subprocess.run(["xdg-open", self.kb.kb_dir], check=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录: {e}")


class NewKnowledgeDialog(tk.Toplevel):
    """新建知识对话框"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("新建知识")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()

        self.result = None

        self._create_ui()
        self.wait_window(self)

    def _create_ui(self):
        """创建UI"""
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # 标题输入
        ttk.Label(frame, text="标题:").pack(anchor=tk.W)
        self.title_entry = ttk.Entry(frame, font=("Segoe UI", 10))
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        self.title_entry.focus()

        # 内容输入
        ttk.Label(frame, text="内容 (支持Markdown格式):").pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, font=("Consolas", 9), height=15
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 提示
        hint = """提示: 使用 # 标题 来创建知识条目
使用 关键词: xxx, yyy 来添加关键词"""
        ttk.Label(frame, text=hint, foreground="gray", font=("Segoe UI", 9)).pack(anchor=tk.W)

        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="确定", command=self._on_ok).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT)

    def _on_ok(self):
        """确定按钮"""
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()

        if not title:
            messagebox.showwarning("提示", "请输入标题")
            return

        if not content:
            messagebox.showwarning("提示", "请输入内容")
            return

        self.result = (title, content)
        self.destroy()


class EditKnowledgeDialog(tk.Toplevel):
    """编辑知识对话框"""

    def __init__(self, parent, filename: str, content: str):
        super().__init__(parent)
        self.title(f"编辑: {filename}")
        self.geometry("700x600")
        self.transient(parent)
        self.grab_set()

        self.result = None

        self._create_ui(content)
        self.wait_window(self)

    def _create_ui(self, content: str):
        """创建UI"""
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # 内容编辑
        ttk.Label(frame, text="内容 (支持Markdown格式):").pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(
            frame, wrap=tk.WORD, font=("Consolas", 9), height=20
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.content_text.insert("1.0", content)

        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="保存", command=self._on_save).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT)

    def _on_save(self):
        """保存按钮"""
        content = self.content_text.get("1.0", tk.END).strip()
        self.result = content
        self.destroy()


def open_knowledge_base_dialog():
    """打开知识库管理对话框"""
    from thonny import get_workbench

    dialog = KnowledgeBaseDialog(get_workbench())
    show_dialog(dialog, master=get_workbench())


def load_plugin():
    """加载插件"""
    # 添加菜单项
    from thonny import get_workbench

    def open_kb_dialog():
        dialog = KnowledgeBaseDialog(get_workbench())
        show_dialog(dialog, master=get_workbench())

    # 在工具菜单中添加知识库管理
    get_workbench().add_command(
        "open_knowledge_base", "tools", "知识库管理", open_kb_dialog, group=10
    )
