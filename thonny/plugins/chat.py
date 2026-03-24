"""
AI编程助手聊天界面
提供与AI助手的交互功能，支持Markdown格式显示
"""

import datetime
import os.path
import re
import threading
import tkinter as tk
import uuid
from dataclasses import replace
from tkinter import messagebox, ttk
from typing import Dict, List, Optional, Tuple

from thonny import get_runner, get_shell, get_workbench, rst_utils, tktextext, ui_utils
from thonny.assistance import (
    Assistant,
    Attachment,
    ChatContext,
    ChatMessage,
    ChatResponseFragmentWithRequestId,
    format_file_url,
    logger,
)
from thonny.common import STRING_PSEUDO_FILENAME, ToplevelResponse
from thonny.languages import tr
from thonny.plugins.markdown_renderer import render_markdown
from thonny.tktextext import EnhancedText, TweakableText
from thonny.ui_utils import (
    LongTextDialog,
    create_custom_toolbutton_in_frame,
    ems_to_pixels,
    get_beam_cursor,
    get_hyperlink_cursor,
    lookup_style_option,
    shift_is_pressed,
    show_dialog,
    update_text_height,
)


class ChatView(tktextext.TextFrame):
    """AI聊天视图"""

    def __init__(self, master):
        # 根据主题获取背景色
        workbench = get_workbench()
        if workbench.uses_dark_ui_theme():
            bg_color = "#1a1a2e"
            text_color = "#eaeaea"
            assistant_bg = "#16213e"
            user_bg = "#0f3460"
            welcome_color = "#eaeaea"
            input_bg = "#252542"
            input_fg = "#eaeaea"
            border_color = "#e94560"
            button_bg = "#e94560"
        else:
            bg_color = "#F8F9FA"
            text_color = "#2C3E50"
            assistant_bg = "#E8F5E8"
            user_bg = "#E3F2FD"
            welcome_color = "#2C3E50"
            input_bg = "white"
            input_fg = "#2C3E50"
            border_color = "#3498DB"
            button_bg = "#3498DB"

        self._theme_colors = {
            "bg": bg_color,
            "text": text_color,
            "assistant_bg": assistant_bg,
            "user_bg": user_bg,
            "welcome": welcome_color,
            "input_bg": input_bg,
            "input_fg": input_fg,
            "border": border_color,
            "button_bg": button_bg,
        }

        super().__init__(
            master,
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            read_only=True,
            wrap="word",
            font=("Segoe UI", 10),
            padx=15,
            pady=10,
            insertwidth=0,
            background=bg_color,
            foreground=text_color,
            suppress_events=True,
        )

        self._init_state()
        self._setup_ui()
        self._bind_events()

    def _init_state(self):
        """初始化状态变量"""
        self._analyzer_instances: List = []
        self._chat_messages: List[ChatMessage] = []
        self._formatted_attachmets_per_message: Dict[str, str] = {}
        self._last_tagged_attachments: Dict[str, Attachment] = {}
        self._active_chat_request_id: Optional[str] = None
        self._snapshots_per_main_file: Dict = {}
        self._current_snapshot = None
        self._current_suggestions: List[str] = []
        self._accepted_warning_sets: List = []
        self._last_analysis_start_index = "1.0"
        self._last_analysis_end_index = "1.0"

        # 响应缓冲区
        self._response_buffer = ""
        self._response_start_index = None

    def _setup_ui(self):
        """设置UI"""
        self._configure_text_tags()
        self.query_box = self._create_query_panel()
        self.query_box.grid(row=1, column=1, sticky="nsew")

        from thonny.plugins.ollama import OllamaAssistant

        self._current_assistant: Assistant = OllamaAssistant()

    def _configure_text_tags(self):
        """配置文本标签样式"""
        colors = self._theme_colors

        # 助手消息样式 - 移除左边距
        self.text.tag_configure(
            "assistant_message",
            lmargin1=0,
            lmargin2=0,
            font=("Segoe UI", 10),
            lmargincolor=colors["bg"],
            background=colors["assistant_bg"],
            foreground="#4ecca3" if get_workbench().uses_dark_ui_theme() else "#2E7D32",
            spacing1=2,
            spacing3=2,
            borderwidth=1,
            relief="solid",
        )

        # 用户消息样式 - 移除左边距
        self.text.tag_configure(
            "user_message",
            lmargin1=0,
            lmargin2=0,
            font=("Segoe UI", 10, "bold"),
            lmargincolor=colors["bg"],
            background=colors["user_bg"],
            foreground="#e94560" if get_workbench().uses_dark_ui_theme() else "#1565C0",
            spacing1=2,
            spacing3=2,
            borderwidth=1,
            relief="solid",
        )

        # 系统消息样式
        self.text.tag_configure(
            "system_message",
            lmargin1=ems_to_pixels(5),
            lmargin2=ems_to_pixels(5),
            font=("Segoe UI", 9, "italic"),
            foreground="#a0a0a0" if get_workbench().uses_dark_ui_theme() else "#757575",
            spacing1=3,
            spacing3=3,
        )

        # 其他标签
        self.text.tag_configure("section_title", spacing3=5, font="BoldTkDefaultFont")
        self.text.tag_configure("intro", spacing3=10)
        self.text.tag_configure("suggestions_block", justify="right")

        # 代码块标签 - 可点击复制
        is_dark = get_workbench().uses_dark_ui_theme()
        self.text.tag_configure(
            "code_block",
            background="#2d2d4a" if is_dark else "#f5f5f5",
            foreground="#4ecca3" if is_dark else "#2E7D32",
            font=("Consolas", 10),
            spacing1=5,
            spacing3=5,
            lmargin1=10,
            lmargin2=10,
        )
        self.text.tag_bind("code_block", "<Enter>", lambda e: self.text.config(cursor="hand2"))
        self.text.tag_bind(
            "code_block", "<Leave>", lambda e: self.text.config(cursor=get_beam_cursor())
        )

        main_font = tk.font.nametofont("TkDefaultFont")
        italic_underline_font = main_font.copy()
        italic_underline_font.configure(slant="italic", size=main_font.cget("size"), underline=True)

        self.text.tag_configure("feedback_link", justify="right", font=italic_underline_font)
        self.text.tag_configure("python_errors_link", justify="right", font=italic_underline_font)

    def _bind_events(self):
        """绑定事件"""
        self.text.bind("<Motion>", self._on_mouse_move_in_text, True)
        self.text.bind("<Button-3>", self._show_context_menu, True)  # 右键菜单
        self.text.bind("<Control-c>", self._copy_selection, True)  # Ctrl+C 复制
        self.text.tag_bind(
            "python_errors_link",
            "<ButtonRelease-1>",
            lambda e: get_workbench().open_url("errors.rst"),
            True,
        )
        self.text.tag_bind(
            "attachments_link",
            "<ButtonRelease-1>",
            self._on_click_attachments_link,
            True,
        )
        # 代码块点击复制
        self.text.tag_bind(
            "code_block",
            "<ButtonRelease-1>",
            self._on_click_code_block,
            True,
        )

        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)
        get_workbench().bind("AiChatResponseFragment", self._handle_chat_fragment, True)

        self._ui_theme_binding = self.bind("<<ThemeChanged>>", self._on_theme_changed, True)
        self._configure_binding = self.bind("<Configure>", self._on_configure, True)
        self._workbench_binding = get_workbench().bind(
            "WorkbenchReady", self._workspace_ready, True
        )

    def _show_context_menu(self, event):
        """显示右键菜单"""
        menu = tk.Menu(self, tearoff=0)

        # 复制选中内容
        try:
            sel_start = self.text.index("sel.first")
            sel_end = self.text.index("sel.last")
            has_selection = True
        except tk.TclError:
            has_selection = False

        if has_selection:
            menu.add_command(
                label="📋 复制选中内容",
                command=lambda: self._copy_selection(None),
                accelerator="Ctrl+C",
            )
            menu.add_separator()

        # 复制消息
        menu.add_command(
            label="📄 复制当前消息",
            command=lambda: self._copy_message_at_index(f"@{event.x},{event.y}"),
        )
        menu.add_command(label="📑 复制所有对话", command=self._copy_all_conversation)
        menu.add_separator()

        # 复制代码块
        code_block = self._get_code_block_at_index(f"@{event.x},{event.y}")
        if code_block:
            menu.add_command(
                label="💻 复制代码块", command=lambda: self._copy_to_clipboard(code_block)
            )
            menu.add_separator()

        # 清空对话
        menu.add_command(label="🗑️ 清空对话", command=self._clear_conversation)

        menu.tk_popup(event.x_root, event.y_root)

    def _copy_selection(self, event):
        """复制选中的文本"""
        try:
            selected_text = self.text.get("sel.first", "sel.last")
            self._copy_to_clipboard(selected_text)
            return "break"
        except tk.TclError:
            pass
        return None

    def _copy_message_at_index(self, index):
        """复制指定位置的消息"""
        # 查找消息边界
        line_num = int(self.text.index(index).split(".")[0])

        # 向上查找消息开始
        start_line = line_num
        while start_line > 1:
            tags = self.text.tag_names(f"{start_line}.0")
            if any(tag in ["assistant_message", "user_message"] for tag in tags):
                start_line -= 1
            else:
                break
        start_line += 1

        # 向下查找消息结束
        end_line = line_num
        total_lines = int(self.text.index("end-1c").split(".")[0])
        while end_line < total_lines:
            tags = self.text.tag_names(f"{end_line}.0")
            if any(tag in ["assistant_message", "user_message"] for tag in tags):
                end_line += 1
            else:
                break

        # 获取消息内容
        message_text = self.text.get(f"{start_line}.0", f"{end_line}.0")
        self._copy_to_clipboard(message_text.strip())

    def _copy_all_conversation(self):
        """复制所有对话内容"""
        all_text = self.text.get("1.0", "end-1c")
        self._copy_to_clipboard(all_text)

    def _get_code_block_at_index(self, index):
        """获取指定位置的代码块内容"""
        # 检查是否在代码块内
        tags = self.text.tag_names(index)
        if "code_block" not in tags:
            return None

        # 获取代码块范围
        ranges = self.text.tag_ranges("code_block")
        for i in range(0, len(ranges), 2):
            start, end = ranges[i], ranges[i + 1]
            if self.text.compare(start, "<=", index) and self.text.compare(index, "<=", end):
                code = self.text.get(start, end)
                # 去除代码块标记
                code = re.sub(r"^```\w*\n?", "", code)
                code = re.sub(r"\n?```$", "", code)
                return code.strip()
        return None

    def _on_click_code_block(self, event):
        """点击代码块复制"""
        code = self._get_code_block_at_index(f"@{event.x},{event.y}")
        if code:
            self._copy_to_clipboard(code)
            self._show_copy_notification("代码已复制到剪贴板！")

    def _copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        self.clipboard_clear()
        self.clipboard_append(text)
        self._show_copy_notification("已复制到剪贴板！")

    def _show_copy_notification(self, message):
        """显示复制成功通知"""
        # 创建临时提示标签
        notification = tk.Label(
            self,
            text=message,
            background="#4CAF50" if not get_workbench().uses_dark_ui_theme() else "#2E7D32",
            foreground="white",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            relief="flat",
        )
        notification.place(relx=0.5, rely=0.9, anchor="center")

        # 2秒后消失
        self.after(2000, notification.destroy)

    def _clear_conversation(self):
        """清空对话"""
        if messagebox.askyesno("确认", "确定要清空所有对话内容吗？"):
            self.text.delete("1.0", "end")
            self._chat_messages.clear()

    def destroy(self):
        """清理资源"""
        if hasattr(self, "_configure_binding"):
            self.unbind("<Configure>", self._configure_binding)
        if hasattr(self, "_workbench_binding"):
            get_workbench().unbind("WorkbenchReady", self._workbench_binding)
        super().destroy()

    def _create_query_panel(self) -> tk.Frame:
        """创建查询面板"""
        colors = self._theme_colors
        background = colors["bg"]
        panel = tk.Frame(self, background=background)
        panel.rowconfigure(2, weight=1)
        panel.columnconfigure(1, weight=1)

        pad = ems_to_pixels(1.5)

        # 欢迎标签
        welcome_label = tk.Label(
            panel,
            text="💬 AI编程助手 - 随时为您解答编程问题",
            background=background,
            foreground=colors["welcome"],
            font=("Segoe UI", 11, "bold"),
            pady=ems_to_pixels(0.5),
        )
        welcome_label.grid(row=0, column=1, columnspan=2, sticky="w", padx=pad, pady=(pad, 0))

        # 建议文本框
        self.suggestions_text = TweakableText(
            panel,
            read_only=True,
            suppress_events=True,
            height=1,
            background=background,
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 9),
            cursor="arrow",
            insertwidth=0,
            wrap="word",
        )
        self.suggestions_text.grid(
            row=1, column=1, columnspan=2, sticky="nsew", padx=pad, pady=(pad, 0)
        )
        self.suggestions_text.tag_configure(
            "suggestion", foreground=colors["border"], font=("Segoe UI", 9)
        )
        self.suggestions_text.tag_configure("active", underline=True)

        self._setup_suggestion_bindings()

        # 输入区域
        border_frame = tk.Frame(panel, background=colors["border"])
        border_frame.grid(row=2, column=1, sticky="nsew", padx=pad, pady=(pad, pad))

        inside_frame = tk.Frame(border_frame, background=colors["input_bg"])
        inside_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        inside_frame.rowconfigure(0, weight=1)
        inside_frame.columnconfigure(0, weight=1)

        self.query_text = tk.Text(
            inside_frame,
            height=1,
            font=("Segoe UI", 10),
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            wrap="word",
            background=colors["input_bg"],
            foreground=colors["input_fg"],
            insertbackground=colors["border"],
        )
        self.query_text.bind("<Return>", self._on_press_enter, True)
        self.query_text.bind("<Key>", self._on_change_query, True)
        self.query_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 发送按钮
        submit_btn = create_custom_toolbutton_in_frame(
            panel,
            text="🚀 发送",
            command=self._on_click_submit,
            background=colors["button_bg"],
            foreground="white",
            borderwidth=0,
            bordercolor=colors["border"],
            font=("Segoe UI", 10, "bold"),
        )
        submit_btn.grid(row=2, column=2, sticky="e", padx=(0, pad), pady=pad)

        border_frame.rowconfigure(0, weight=1)
        border_frame.columnconfigure(0, weight=1)

        return panel

    def _setup_suggestion_bindings(self):
        """设置建议文本框的交互绑定"""

        def get_active_range(event):
            mouse_index = self.suggestions_text.index("@%d,%d" % (event.x, event.y))
            return self.suggestions_text.tag_prevrange("suggestion", mouse_index + "+1c")

        def on_motion(event):
            self.suggestions_text.tag_remove("active", "1.0", "end")
            active_range = get_active_range(event)
            if active_range:
                self.suggestions_text.tag_add("active", active_range[0], active_range[1])

        def on_leave(event):
            self.suggestions_text.tag_remove("active", "1.0", "end")

        def on_click(event):
            active_range = get_active_range(event)
            if active_range:
                suggestion = self.suggestions_text.get(active_range[0], active_range[1])
                self.submit_user_chat_message(suggestion)

        self.suggestions_text.tag_bind("suggestion", "<1>", on_click)
        self.suggestions_text.tag_bind("suggestion", "<Leave>", on_leave)
        self.suggestions_text.tag_bind("suggestion", "<Motion>", on_motion)

    def _handle_chat_fragment(
        self, fragment_with_request_id: ChatResponseFragmentWithRequestId
    ) -> None:
        """处理AI响应片段"""
        if fragment_with_request_id.request_id != self._active_chat_request_id:
            logger.info("Skipping chat fragment - request cancelled")
            return

        fragment = fragment_with_request_id.fragment

        # 记录起始位置（只在第一次）
        if self._response_start_index is None:
            self._response_start_index = self.text.index("end-1c")
            self.text.direct_insert("end", "\n", ("assistant_message",))

        # 直接追加内容，不重新渲染整个缓冲区
        self._response_buffer += fragment.content
        self.text.direct_insert("end", fragment.content, ("assistant_message",))
        self.text.see("end")

        # 更新消息历史
        self._update_chat_history(fragment.content)

        if fragment.is_final:
            self._finalize_response()

    def _update_chat_history(self, content: str):
        """更新聊天历史"""
        if self._chat_messages and self._chat_messages[-1].role == "assistant":
            last_msg = self._chat_messages.pop()
            from dataclasses import replace

            new_msg = replace(last_msg, content=last_msg.content + content)
            self._chat_messages.append(new_msg)
        else:
            self._chat_messages.append(ChatMessage("assistant", content, []))

    def _finalize_response(self):
        """完成响应处理 - 最终Markdown渲染"""
        if not self._response_buffer.strip():
            self._reset_response_state()
            return

        # 删除之前追加的原始内容
        end_index = self.text.index("end-1c")
        if self._response_start_index and self._response_start_index != end_index:
            self.text.direct_delete(self._response_start_index, end_index)

        # 重新渲染完整的Markdown内容
        render_markdown(self.text, self._response_buffer, ("assistant_message",))
        self.text.direct_insert("end", "\n", ("assistant_message",))
        self.text.see("end")

        self._reset_response_state()
        self._update_suggestions()

    def _reset_response_state(self):
        """重置响应状态"""
        self._response_buffer = ""
        self._response_start_index = None
        self._active_chat_request_id = None

    def submit_user_chat_message(self, message: str):
        """提交用户消息"""
        self._remove_suggestions()
        message = message.rstrip()

        # 处理文件命令
        if self._handle_file_command(message):
            self.query_text.delete("1.0", "end")
            return "break"

        # 准备新对话
        attachments, warnings = self.compile_attachments(message)
        self._prepare_new_completion()

        self._active_chat_request_id = str(uuid.uuid4())

        # 显示用户消息
        self._append_text("\n")
        self._append_text(message, tags=("user_message",))
        if attachments:
            self._formatted_attachmets_per_message[self._active_chat_request_id] = (
                self._current_assistant.format_attachments(attachments)
            )
            self._append_text(
                " 📎",
                tags=("attachments_link", f"att_{self._active_chat_request_id}", "user_message"),
            )
        self._append_text("\n", tags=("user_message",))
        self._append_text("\n")

        # 显示警告
        for warning in warnings:
            self._append_text(f"WARNING: {warning}\n\n")

        self._chat_messages.append(ChatMessage("user", message, attachments))
        self.query_text.delete("1.0", "end")

        # 启动AI响应线程
        for assistant in self.select_assistants_for_user_message(message):
            threading.Thread(
                target=self._complete_chat_in_thread,
                daemon=True,
                args=(assistant, self._active_chat_request_id),
            ).start()

        return "break"

    def _handle_file_command(self, message: str) -> bool:
        """处理文件相关命令"""
        msg_lower = message.lower().strip()

        if any(
            cmd in msg_lower
            for cmd in ["查看文件", "查看当前文件", "显示文件", "查看代码", "当前文件"]
        ):
            return self._show_current_file()

        if any(cmd in msg_lower for cmd in ["修改文件", "修改当前文件", "更新文件", "保存修改"]):
            return self._modify_current_file(message)

        return False

    def _show_current_file(self) -> bool:
        """显示当前文件内容"""
        try:
            editor = get_workbench().get_editor_notebook().get_current_editor()
            if editor is None:
                self._append_text("\n💡 当前没有打开的文件。\n", tags=("system_message",))
                return True

            file_path = (
                editor.get_target_path() if hasattr(editor, "get_target_path") else "未命名文件"
            )
            content = editor.get_content() if hasattr(editor, "get_content") else ""

            self._append_text("\n", tags=("system_message",))
            self._append_text(f"📄 当前文件：{file_path}\n", tags=("system_message",))
            self._append_text("```python\n", tags=("system_message",))
            self._append_text(content, tags=("system_message",))
            self._append_text("\n```\n", tags=("system_message",))
            return True

        except Exception as e:
            self._append_text(f"\n❌ 无法读取文件：{str(e)}\n", tags=("system_message",))
            return True

    def _modify_current_file(self, message: str) -> bool:
        """修改当前文件"""
        try:
            editor = get_workbench().get_editor_notebook().get_current_editor()
            if editor is None:
                self._append_text("\n💡 当前没有打开的文件。\n", tags=("system_message",))
                return True

            file_path = (
                editor.get_target_path() if hasattr(editor, "get_target_path") else "未命名文件"
            )

            # 提取代码块
            code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", message, re.DOTALL)
            if not code_blocks:
                self._append_text(
                    "\n💡 请提供代码块（使用```python标记）。\n", tags=("system_message",)
                )
                return True

            new_content = code_blocks[-1]

            if messagebox.askyesno("确认修改", f"确定要修改文件 {file_path} 吗？"):
                if hasattr(editor, "_code_view") and hasattr(editor._code_view, "set_content"):
                    editor._code_view.set_content(new_content)
                    self._append_text(f"\n✅ 文件 {file_path} 已更新。\n", tags=("system_message",))
                else:
                    self._append_text("\n❌ 无法修改文件内容。\n", tags=("system_message",))
            else:
                self._append_text("\n💡 已取消文件修改。\n", tags=("system_message",))

            return True

        except Exception as e:
            self._append_text(f"\n❌ 无法修改文件：{str(e)}\n", tags=("system_message",))
            return True

    def _append_text(self, chars, tags=(), source="analysis"):
        """追加文本到显示区域"""
        self.text.direct_insert("end", chars, tags=tags)
        if source == "analysis":
            self._last_analysis_end_index = self.text.index("end")
        self.text.see("end")

    def _prepare_new_completion(self):
        """准备新的对话完成"""
        self._cancel_analysis()
        self._cancel_completion()

    def _cancel_completion(self):
        """取消当前对话"""
        if self._current_assistant and self._active_chat_request_id:
            self._active_chat_request_id = None
            self._append_text("... [cancelled]", source="chat")
            self._current_assistant.cancel_completion()

    def _cancel_analysis(self):
        """取消分析"""
        if self._analyzer_instances:
            self._accepted_warning_sets.clear()
            for wp in self._analyzer_instances:
                wp.cancel_analysis()
            self._analyzer_instances = []

    def select_assistants_for_user_message(self, message: str) -> List[Assistant]:
        """选择处理用户消息的助手"""
        names = re.findall(r"@(\w+)", message)
        if not names:
            return [self._current_assistant]

        unique_names = list(set(map(lambda s: s.lower(), names)))
        result = []
        for name in unique_names:
            if name in get_workbench().assistants:
                result.append(get_workbench().assistants[name])
            else:
                self._append_text(f"No assistant named {name}")
        return result

    def _complete_chat_in_thread(self, assistant: Assistant, request_id: str):
        """在线程中完成对话"""
        try:
            context = ChatContext(messages=self._chat_messages)
            for fragment in assistant.complete_chat(context):
                get_workbench().queue_event(
                    "AiChatResponseFragment",
                    ChatResponseFragmentWithRequestId(fragment, request_id=request_id),
                )
                if fragment.is_final:
                    break
        except Exception as e:
            logger.exception("Chat completion error")
            from thonny.assistance import ChatResponseChunk

            get_workbench().queue_event(
                "AiChatResponseFragment",
                ChatResponseFragmentWithRequestId(
                    ChatResponseChunk(content=f"ERROR: {e}", is_final=True),
                    request_id=request_id,
                ),
            )

    def compile_attachments(self, message: str) -> Tuple[List[Attachment], List[str]]:
        """编译消息附件"""
        from thonny.shell import ExecutionInfo

        attachments = []
        warnings = []
        tags = re.findall(r"#(\w+)", message)
        current_editor = get_workbench().get_editor_notebook().get_current_editor()

        proper_tags = {
            "currentfile": "currentFile",
            "selectedcode": "selectedCode",
            "lastrun": "lastRun",
            "selectedoutput": "selectedOutput",
        }
        tags = [proper_tags.get(tag.lower(), tag) for tag in tags]

        for tag in ["currentFile", "selectedCode", "lastRun", "selectedOutput"]:
            if tag not in tags:
                continue

            attachment = self._create_attachment(tag, current_editor)
            if attachment:
                if (
                    attachment.tag not in self._last_tagged_attachments
                    or self._last_tagged_attachments.get(attachment.tag) != attachment
                ):
                    self._last_tagged_attachments[attachment.tag] = attachment
                    attachments.append(attachment)
            else:
                warnings.append(f"Can't attach #{tag}")

        return attachments, warnings

    def _create_attachment(self, tag: str, current_editor) -> Optional[Attachment]:
        """创建附件"""
        if tag == "currentFile" and current_editor:
            name = self._get_editor_name(current_editor)
            content = current_editor.get_content() if hasattr(current_editor, "get_content") else ""
            if content.strip():
                return Attachment(name, tag, content)

        elif tag == "selectedCode" and current_editor:
            text = current_editor.get_code_view().text
            sel = text.get_selection_indices()
            if sel[0]:
                return Attachment("Selected code", tag, text.get(sel[0], sel[1]))

        elif tag == "lastRun":
            last_run = get_shell().text.extract_last_execution_info("%Run")
            if last_run:
                content = get_shell().text.get(last_run.io_start_index, last_run.io_end_index)
                cmd = last_run.command_line.replace("%Run", "python")
                return Attachment(f"console log of `{cmd}`", tag, content)

        elif tag == "selectedOutput":
            text = get_shell().text
            sel = text.get_selection_indices()
            if sel[0]:
                return Attachment("Selected output", tag, text.get(sel[0], sel[1]))

        return None

    def _get_editor_name(self, editor) -> str:
        """获取编辑器名称"""
        if editor.is_local():
            return os.path.relpath(editor.get_target_path(), get_workbench().get_local_cwd())
        elif editor.is_remote():
            return editor.get_target_path().split("/")[-1]
        return "unnamed file"

    def _on_mouse_move_in_text(self, event=None):
        """鼠标移动处理"""
        tags = self.text.tag_names("@%d,%d" % (event.x, event.y))
        cursor = (
            get_hyperlink_cursor()
            if "attachments_link" in tags or "python_errors_link" in tags
            else get_beam_cursor()
        )
        if self.text.cget("cursor") != cursor:
            self.text.config(cursor=cursor)

    def _on_click_attachments_link(self, event: tk.Event):
        """点击附件链接"""
        tags = self.text.tag_names("@%d,%d" % (event.x, event.y))
        for tag in tags:
            if tag.startswith("att_"):
                request_id = tag.removeprefix("att_")
                if request_id in self._formatted_attachmets_per_message:
                    dlg = LongTextDialog(
                        title=tr("Attachments"),
                        text_content=self._formatted_attachmets_per_message[request_id],
                        parent=self,
                    )
                    show_dialog(dlg, master=get_workbench())

    def _remove_suggestions(self):
        """移除建议"""
        self.suggestions_text.direct_delete("1.0", "end")
        self._current_suggestions = []

    def _update_suggestions(self):
        """更新建议"""
        new_suggestions = []
        last_run = get_shell().text.extract_last_execution_info("%Run")
        editor = get_workbench().get_editor_notebook().get_current_editor()

        if editor and editor.get_content():
            new_suggestions.append("Check #currentFile")
        if get_shell().text.has_selection() and last_run:
            new_suggestions.append("Explain #selectedOutput in #lastRun")
        new_suggestions.append("Explain #lastRun")

        if new_suggestions != self._current_suggestions:
            self._remove_suggestions()
            for i, suggestion in enumerate(new_suggestions):
                prefix = "" if i == 0 else "  •  "
                self.suggestions_text.direct_insert("end", prefix)
                self.suggestions_text.direct_insert("end", suggestion, tags=("suggestion",))
            self._current_suggestions = new_suggestions
            update_text_height(self.suggestions_text, min_lines=1, max_lines=5)

    def _on_press_enter(self, event: tk.Event):
        """回车键处理"""
        if not shift_is_pressed(event) and self._current_assistant.get_ready():
            self.submit_user_chat_message(self.query_text.get("1.0", "end"))
        return "break"

    def _on_change_query(self, event: tk.Event):
        """查询文本变化处理"""
        update_text_height(self.query_text, 1, max_lines=10)

    def _on_click_submit(self):
        """点击提交按钮"""
        if self._current_assistant.get_ready():
            self.submit_user_chat_message(self.query_text.get("1.0", "end"))

    def _on_configure(self, event: tk.Event):
        """配置变化处理"""
        pass

    def _workspace_ready(self, event: tk.Event):
        """工作区就绪处理"""
        self._update_suggestions()

    def _on_theme_changed(self, event):
        """主题变化处理 - 重新应用主题颜色"""
        workbench = get_workbench()
        if workbench.uses_dark_ui_theme():
            bg_color = "#1a1a2e"
            text_color = "#eaeaea"
            assistant_bg = "#16213e"
            user_bg = "#0f3460"
            welcome_color = "#eaeaea"
            input_bg = "#252542"
            input_fg = "#eaeaea"
            border_color = "#e94560"
            button_bg = "#e94560"
            assistant_fg = "#4ecca3"
            user_fg = "#e94560"
            system_fg = "#a0a0a0"
        else:
            bg_color = "#F8F9FA"
            text_color = "#2C3E50"
            assistant_bg = "#E8F5E8"
            user_bg = "#E3F2FD"
            welcome_color = "#2C3E50"
            input_bg = "white"
            input_fg = "#2C3E50"
            border_color = "#3498DB"
            button_bg = "#3498DB"
            assistant_fg = "#2E7D32"
            user_fg = "#1565C0"
            system_fg = "#757575"

        self._theme_colors = {
            "bg": bg_color,
            "text": text_color,
            "assistant_bg": assistant_bg,
            "user_bg": user_bg,
            "welcome": welcome_color,
            "input_bg": input_bg,
            "input_fg": input_fg,
            "border": border_color,
            "button_bg": button_bg,
        }

        # 更新主文本区域
        self.text.configure(
            background=bg_color,
            foreground=text_color,
        )

        # 更新标签样式
        self.text.tag_configure(
            "assistant_message",
            background=assistant_bg,
            foreground=assistant_fg,
            lmargincolor=bg_color,
        )
        self.text.tag_configure(
            "user_message", background=user_bg, foreground=user_fg, lmargincolor=bg_color
        )
        self.text.tag_configure("system_message", foreground=system_fg)
        self.text.tag_configure(
            "code_block",
            background="#2d2d4a" if workbench.uses_dark_ui_theme() else "#f5f5f5",
            foreground="#4ecca3" if workbench.uses_dark_ui_theme() else "#2E7D32",
        )

        # 更新查询面板
        if hasattr(self, "query_box"):
            self.query_box.configure(background=bg_color)
            for child in self.query_box.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(background=bg_color, foreground=welcome_color)
                elif isinstance(child, tk.Frame):
                    if hasattr(child, "background"):
                        child.configure(background=bg_color)

        if isinstance(self.text, rst_utils.RstText):
            self.text.on_theme_changed()

    def _handle_toplevel_response(self, msg: ToplevelResponse):
        """处理顶层响应"""
        from thonny.plugins.cpython_frontend import LocalCPythonProxy

        if not isinstance(get_runner().get_backend_proxy(), LocalCPythonProxy):
            return

        if not msg.get("user_exception") and msg.get("command_name") in [
            "execute_system_command",
            "execute_source",
        ]:
            return

        self._cancel_analysis()
        self._cancel_completion()

        key = msg.get("filename", STRING_PSEUDO_FILENAME)
        self._current_snapshot = {
            "timestamp": datetime.datetime.now().isoformat()[:19],
            "main_file_path": key,
        }
        self._snapshots_per_main_file.setdefault(key, []).append(self._current_snapshot)

        self.main_file_path = (
            msg.get("filename") if msg.get("filename") and os.path.exists(msg["filename"]) else None
        )


def load_plugin():
    """加载插件"""
    get_workbench().add_view(ChatView, tr("AI编程助手"), "se", visible_by_default=True)
