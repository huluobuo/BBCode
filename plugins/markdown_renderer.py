"""
Markdown渲染器 - 将Markdown文本转换为Tkinter文本标签
"""

import re
from typing import List, Optional, Tuple

from thonny.ui_utils import ems_to_pixels

# 正则表达式模式
HEADING_PATTERN = re.compile(r"^(#{1,6})\s*(.*)$")
LIST_ITEM_PATTERN = re.compile(r"^[\s]*([-*+•◦▪▫]|\d+[.\)])\s+(.*)$")
INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
BOLD_PATTERN = re.compile(r"\*\*(.*?)\*\*")
ITALIC_PATTERN = re.compile(r"\*(.*?)\*")
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")


class MarkdownRenderer:
    """Markdown渲染器"""

    def __init__(self, text_widget):
        self.text = text_widget
        self._setup_tags()

    def _setup_tags(self):
        """设置文本标签样式"""
        # 标题样式
        for i, size in enumerate([16, 14, 12, 11, 10, 10], 1):
            self.text.tag_configure(f"md_h{i}", font=("Segoe UI", size, "bold"), spacing3=10 - i)

        # 文本样式
        self.text.tag_configure("md_bold", font=("Segoe UI", 10, "bold"))
        self.text.tag_configure("md_italic", font=("Segoe UI", 10, "italic"))
        self.text.tag_configure("md_code", font=("Consolas", 9), background="#F5F5F5")
        self.text.tag_configure(
            "md_code_block", font=("Consolas", 9), background="#F5F5F5", spacing1=5, spacing3=5
        )
        self.text.tag_configure(
            "md_code_block_header", font=("Segoe UI", 9, "italic"), foreground="#666666", spacing1=3
        )
        self.text.tag_configure("md_link", foreground="#3498DB", underline=True)

        # 布局样式 - 列表无缩进
        self.text.tag_configure("md_list", lmargin1=0, lmargin2=0, spacing1=0, spacing3=0)
        self.text.tag_configure(
            "md_quote",
            lmargin1=ems_to_pixels(2),
            foreground="#666666",
            font=("Segoe UI", 10, "italic"),
        )
        self.text.tag_configure("md_hr", spacing1=10, spacing3=10)

        # 代码检查样式
        self.text.tag_configure("code_error", background="#FFEBEE", foreground="#C62828")
        self.text.tag_configure("code_warning", background="#FFF3E0", foreground="#EF6C00")
        self.text.tag_configure("code_ok", background="#E8F5E9", foreground="#2E7D32")

    def render(self, markdown_text: str, base_tags: Tuple[str, ...] = ()):
        """渲染Markdown文本"""
        lines = markdown_text.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # 代码块
            if line.strip().startswith("```"):
                i = self._render_code_block(lines, i, base_tags)
                continue

            # 标题
            if self._is_heading(line):
                self._render_heading(line, base_tags)
                i += 1
                continue

            # 引用
            if line.strip().startswith(">"):
                self._render_quote(line, base_tags)
                i += 1
                continue

            # 列表
            if self._is_list_item(line):
                i = self._render_list(lines, i, base_tags)
                continue

            # 分隔线
            if self._is_horizontal_rule(line):
                self._render_horizontal_rule(base_tags)
                i += 1
                continue

            # 普通段落
            if line.strip():
                self._render_paragraph(line, base_tags)
            else:
                self.text.direct_insert("end", "\n", base_tags)

            i += 1

    def _is_heading(self, line: str) -> bool:
        return bool(HEADING_PATTERN.match(line.strip()))

    def _render_heading(self, line: str, base_tags: Tuple[str, ...]):
        match = HEADING_PATTERN.match(line.strip())
        if match:
            level = len(match.group(1))
            content = match.group(2)
            tag = f"md_h{min(level, 6)}"
            self._render_inline(content, base_tags + (tag,))
            self.text.direct_insert("end", "\n", base_tags + (tag,))

    def _is_list_item(self, line: str) -> bool:
        return bool(LIST_ITEM_PATTERN.match(line))

    def _render_list(self, lines: List[str], start_idx: int, base_tags: Tuple[str, ...]) -> int:
        i = start_idx
        while i < len(lines):
            line = lines[i]

            if not line.strip():
                i += 1
                continue

            if not self._is_list_item(line) and not line.strip().startswith(" "):
                break

            match = LIST_ITEM_PATTERN.match(line)
            if match:
                content = match.group(2)
                self.text.direct_insert("end", "• ", base_tags + ("md_list",))
                self._render_inline(content, base_tags + ("md_list",))
                self.text.direct_insert("end", "\n", base_tags + ("md_list",))
            i += 1
        return i

    def _is_horizontal_rule(self, line: str) -> bool:
        stripped = line.strip()
        return stripped in ("---", "***", "___")

    def _render_horizontal_rule(self, base_tags: Tuple[str, ...]):
        self.text.direct_insert("end", "─" * 50 + "\n", base_tags + ("md_hr",))

    def _render_quote(self, line: str, base_tags: Tuple[str, ...]):
        content = line.strip()[1:].strip()
        self._render_inline(content, base_tags + ("md_quote",))
        self.text.direct_insert("end", "\n", base_tags + ("md_quote",))

    def _render_code_block(
        self, lines: List[str], start_idx: int, base_tags: Tuple[str, ...]
    ) -> int:
        first_line = lines[start_idx].strip()
        language = first_line[3:].strip() if len(first_line) > 3 else ""

        i = start_idx + 1
        code_lines = []

        while i < len(lines) and not lines[i].strip().startswith("```"):
            code_lines.append(lines[i])
            i += 1

        if code_lines:
            code_text = "\n".join(code_lines)

            # 代码检查已禁用
            # if language.lower() in ('python', 'py', ''):
            #     result = self._check_python_code(code_text)
            #     if result:
            #         self._render_code_check_result(result, base_tags)

            # 插入代码块标记（可点击复制）
            self.text.direct_insert(
                "end",
                f"📋 点击复制代码 ({language or 'text'})\n",
                base_tags + ("md_code_block_header",),
            )

            # 插入代码内容 - 使用 code_block 标签以便点击复制
            self.text.direct_insert(
                "end", code_text + "\n", base_tags + ("md_code_block", "code_block")
            )

        return i + 1 if i < len(lines) else i

    def _render_paragraph(self, line: str, base_tags: Tuple[str, ...]):
        self._render_inline(line, base_tags)
        self.text.direct_insert("end", "\n", base_tags)

    def _render_inline(self, text: str, base_tags: Tuple[str, ...]):
        """渲染行内元素"""
        segments = self._parse_inline(text)

        for seg_type, content in segments:
            tag_map = {
                "code": "md_code",
                "bold": "md_bold",
                "italic": "md_italic",
                "link": "md_link",
            }
            tag = base_tags + (tag_map.get(seg_type),) if seg_type != "normal" else base_tags
            self.text.direct_insert("end", content, tag)

    def _parse_inline(self, text: str) -> List[Tuple[str, str]]:
        """解析行内元素"""
        if not text:
            return [("normal", "")]

        segments = []
        pos = 0

        while pos < len(text):
            # 代码 `code`
            if text[pos] == "`":
                end = text.find("`", pos + 1)
                if end != -1:
                    if pos > 0:
                        segments.append(("normal", text[:pos]))
                    segments.append(("code", text[pos + 1 : end]))
                    text = text[end + 1 :]
                    pos = 0
                    continue

            # 粗体 **text**
            if text[pos : pos + 2] == "**":
                end = text.find("**", pos + 2)
                if end != -1:
                    if pos > 0:
                        segments.append(("normal", text[:pos]))
                    segments.append(("bold", text[pos + 2 : end]))
                    text = text[end + 2 :]
                    pos = 0
                    continue

            # 斜体 *text* (非**)
            if text[pos] == "*" and (pos + 1 >= len(text) or text[pos + 1] != "*"):
                end = text.find("*", pos + 1)
                if end != -1:
                    if pos > 0:
                        segments.append(("normal", text[:pos]))
                    segments.append(("italic", text[pos + 1 : end]))
                    text = text[end + 1 :]
                    pos = 0
                    continue

            # 链接 [text](url)
            if text[pos] == "[":
                link_end = text.find("]", pos)
                if link_end != -1 and link_end + 1 < len(text) and text[link_end + 1] == "(":
                    url_end = text.find(")", link_end + 2)
                    if url_end != -1:
                        if pos > 0:
                            segments.append(("normal", text[:pos]))
                        segments.append(("link", text[pos + 1 : link_end]))
                        text = text[url_end + 1 :]
                        pos = 0
                        continue

            pos += 1

        if text:
            segments.append(("normal", text))

        return segments if segments else [("normal", "")]

    def _check_python_code(self, code: str) -> Optional[dict]:
        """检查Python代码"""
        try:
            import ast

            result = {"syntax_ok": True, "errors": [], "warnings": [], "suggestions": []}

            # 语法检查
            try:
                ast.parse(code)
            except SyntaxError as e:
                result["syntax_ok"] = False
                result["errors"].append(f"语法错误 (第{e.lineno}行): {e.msg}")
                return result

            # 代码规范检查
            lines = code.split("\n")
            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                if len(line) > 120:
                    result["warnings"].append(f"第{i}行: 行长度超过120字符")

                if line != line.rstrip():
                    result["warnings"].append(f"第{i}行: 存在尾随空格")

                if line.startswith("\t"):
                    result["warnings"].append(f"第{i}行: 使用Tab缩进")

                if "==" in stripped and re.search(r"==\s*(True|False)", stripped):
                    result["suggestions"].append(f"第{i}行: 可用'is'代替'=='比较布尔值")

                if re.match(r"^print\s*\(", stripped):
                    result["suggestions"].append(f"第{i}行: 发现print语句")

                if re.match(r"^except\s*:", stripped):
                    result["warnings"].append(f"第{i}行: 使用裸except")

            if not code.strip():
                result["warnings"].append("代码块为空")

            return result if any(result.values()) else None

        except Exception:
            return None

    def _render_code_check_result(self, result: dict, base_tags: Tuple[str, ...]):
        """渲染代码检查结果"""
        if not result or not any([result["errors"], result["warnings"], result["suggestions"]]):
            return

        if result["errors"]:
            self.text.direct_insert(
                "end", f"❌ 发现 {len(result['errors'])} 个错误\n", base_tags + ("code_error",)
            )
        if result["warnings"]:
            self.text.direct_insert(
                "end", f"⚠️ 发现 {len(result['warnings'])} 个警告\n", base_tags + ("code_warning",)
            )
        if result["suggestions"]:
            self.text.direct_insert(
                "end", f"💡 发现 {len(result['suggestions'])} 个建议\n", base_tags + ("code_ok",)
            )

        for error in result["errors"][:3]:
            self.text.direct_insert("end", f"  • {error}\n", base_tags + ("code_error",))
        for warning in result["warnings"][:2]:
            self.text.direct_insert("end", f"  • {warning}\n", base_tags + ("code_warning",))
        for suggestion in result["suggestions"][:2]:
            self.text.direct_insert("end", f"  • {suggestion}\n", base_tags + ("code_ok",))

        self.text.direct_insert("end", "\n", base_tags)


def render_markdown(text_widget, markdown_text: str, base_tags: Tuple[str, ...] = ()):
    """便捷的Markdown渲染函数"""
    renderer = MarkdownRenderer(text_widget)
    renderer.render(markdown_text, base_tags)
