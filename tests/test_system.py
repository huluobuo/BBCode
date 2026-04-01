"""
BBCode 系统测试套件
对整个项目进行系统性逻辑审查，建立全面的测试用例
"""

import unittest
import sys
import os
import time
import threading
from pathlib import Path
from typing import Any, Dict, List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestOllamaClient(unittest.TestCase):
    """Ollama客户端测试"""
    
    def setUp(self):
        """测试准备"""
        try:
            from plugins.ollama_client import OllamaAPI
            self.api = OllamaAPI()
        except ImportError:
            self.skipTest("Ollama客户端模块未找到")
    
    def test_host_normalization(self):
        """测试主机地址规范化"""
        from plugins.ollama_client import OllamaAPI
        
        # 测试带协议的主机地址
        api1 = OllamaAPI(host="http://192.168.1.100")
        self.assertEqual(api1.host, "192.168.1.100")
        
        # 测试带端口的主机地址
        api2 = OllamaAPI(host="192.168.1.100:8080")
        self.assertEqual(api2.host, "192.168.1.100")
        self.assertEqual(api2.port, 8080)
        
        # 测试带斜杠的主机地址
        api3 = OllamaAPI(host="192.168.1.100/")
        self.assertEqual(api3.host, "192.168.1.100")
    
    def test_base_url_construction(self):
        """测试基础URL构建"""
        from plugins.ollama_client import OllamaAPI
        
        api = OllamaAPI(host="192.168.1.100", port=11434)
        self.assertEqual(api.get_base_url(), "http://192.168.1.100:11434")
    
    def test_connection_info(self):
        """测试连接信息获取"""
        from plugins.ollama_client import OllamaAPI
        
        api = OllamaAPI(host="test-host", port=12345, model="test-model")
        info = api.get_connection_info()
        
        self.assertEqual(info["host"], "test-host")
        self.assertEqual(info["port"], 12345)
        self.assertEqual(info["model"], "test-model")
        self.assertIn("base_url", info)
    
    def test_invalid_port(self):
        """测试无效端口处理"""
        from plugins.ollama_client import OllamaAPI
        
        # 测试负数端口
        api = OllamaAPI(port=-1)
        self.assertEqual(api.port, 11434)  # 应该使用默认端口
        
        # 测试超大端口
        api2 = OllamaAPI(port=999999)
        self.assertEqual(api2.port, 11434)  # 应该使用默认端口


class TestKnowledgeBase(unittest.TestCase):
    """知识库系统测试"""
    
    def setUp(self):
        """测试准备"""
        try:
            from plugins.knowledge_base import KnowledgeItem, KnowledgeBase
            self.KnowledgeItem = KnowledgeItem
            self.KnowledgeBase = KnowledgeBase
        except ImportError:
            self.skipTest("知识库模块未找到")
    
    def test_knowledge_item_creation(self):
        """测试知识条目创建"""
        item = self.KnowledgeItem(
            title="测试标题",
            content="测试内容",
            source_file="test.md",
            keywords=["测试", "关键词"]
        )
        
        self.assertEqual(item.title, "测试标题")
        self.assertEqual(item.content, "测试内容")
        self.assertEqual(item.source_file, "test.md")
        self.assertEqual(item.keywords, ["测试", "关键词"])
        self.assertIsNotNone(item.id)
    
    def test_similarity_calculation(self):
        """测试相似度计算"""
        item1 = self.KnowledgeItem(
            title="Python基础",
            content="Python是一种编程语言",
            source_file="test1.md"
        )
        
        item2 = self.KnowledgeItem(
            title="Python基础",
            content="Python是一种编程语言",
            source_file="test2.md"
        )
        
        item3 = self.KnowledgeItem(
            title="Java基础",
            content="Java是一种编程语言",
            source_file="test3.md"
        )
        
        # 相同内容应该有高相似度
        sim1 = item1.calculate_similarity(item2)
        self.assertGreaterEqual(sim1, 0.9)
        
        # 不同内容应该有低相似度
        sim2 = item1.calculate_similarity(item3)
        self.assertLess(sim2, 0.8)
    
    def test_duplicate_detection(self):
        """测试重复检测"""
        item1 = self.KnowledgeItem(
            title="重复测试",
            content="这是重复内容",
            source_file="test1.md"
        )
        
        item2 = self.KnowledgeItem(
            title="重复测试",
            content="这是重复内容",
            source_file="test2.md"
        )
        
        # 应该被认为是重复的
        similarity = item1.calculate_similarity(item2)
        self.assertGreaterEqual(similarity, 0.85)
    
    def test_text_normalization(self):
        """测试文本规范化"""
        item = self.KnowledgeItem(
            title="测试",
            content="测试内容",
            source_file="test.md"
        )
        
        # 测试多余空白移除
        normalized1 = item._normalize_text("Hello   World")
        self.assertEqual(normalized1, "hello world")
        
        # 测试标点符号移除
        normalized2 = item._normalize_text("Hello, World!")
        self.assertEqual(normalized2, "hello world")
        
        # 测试大小写转换
        normalized3 = item._normalize_text("HELLO World")
        self.assertEqual(normalized3, "hello world")


class TestConfigManager(unittest.TestCase):
    """配置管理器测试"""
    
    def setUp(self):
        """测试准备"""
        try:
            from plugins.config_manager import UnifiedConfigManager, ConfigValidator
            self.manager = UnifiedConfigManager()
            self.validator = ConfigValidator()
        except ImportError:
            self.skipTest("配置管理模块未找到")
    
    def test_config_singleton(self):
        """测试配置管理器单例模式"""
        from plugins.config_manager import UnifiedConfigManager
        
        manager1 = UnifiedConfigManager()
        manager2 = UnifiedConfigManager()
        
        self.assertIs(manager1, manager2)
    
    def test_type_validation(self):
        """测试类型验证"""
        # 整数验证
        self.assertTrue(self.validator.validate_type(123, int))
        self.assertFalse(self.validator.validate_type("123", int))
        self.assertFalse(self.validator.validate_type(True, int))  # bool不是int
        
        # 字符串验证
        self.assertTrue(self.validator.validate_type("test", str))
        self.assertFalse(self.validator.validate_type(123, str))
        
        # 布尔验证
        self.assertTrue(self.validator.validate_type(True, bool))
        self.assertTrue(self.validator.validate_type(False, bool))
        self.assertFalse(self.validator.validate_type(1, bool))
    
    def test_range_validation(self):
        """测试范围验证"""
        self.assertTrue(self.validator.validate_range(50, 0, 100))
        self.assertFalse(self.validator.validate_range(150, 0, 100))
        self.assertFalse(self.validator.validate_range(-10, 0, 100))
        self.assertTrue(self.validator.validate_range(50, None, 100))
        self.assertTrue(self.validator.validate_range(50, 0, None))
    
    def test_config_get_set(self):
        """测试配置读写"""
        # 测试设置和获取
        self.manager.set("test.key", "test_value", validate=False)
        value = self.manager.get("test.key")
        self.assertEqual(value, "test_value")
        
        # 测试默认值
        default_value = self.manager.get("nonexistent.key", "default")
        self.assertEqual(default_value, "default")
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试有效值
        result = self.manager.set("ollama.port", 11434)
        self.assertTrue(result)
        
        # 测试无效值（超出范围）
        result = self.manager.set("ollama.port", 999999)
        self.assertFalse(result)
        
        # 测试无效值（错误类型）
        result = self.manager.set("ollama.port", "not_a_number")
        self.assertFalse(result)


class TestTerminal(unittest.TestCase):
    """终端组件测试"""
    
    def setUp(self):
        """测试准备"""
        try:
            from bbcode.terminal import OutputBuffer
            self.OutputBuffer = OutputBuffer
        except ImportError:
            self.skipTest("终端模块未找到")
    
    def test_output_buffer(self):
        """测试输出缓冲区"""
        buffer = self.OutputBuffer(max_lines=100)
        
        # 测试追加
        buffer.append("Line 1\n")
        buffer.append("Line 2\n")
        
        # 测试刷新
        text = buffer.flush()
        self.assertIn("Line 1", text)
        self.assertIn("Line 2", text)
        
        # 测试清空
        buffer.clear()
        self.assertEqual(buffer.get_all(), "")
    
    def test_buffer_max_lines(self):
        """测试缓冲区最大行数限制"""
        buffer = self.OutputBuffer(max_lines=5)
        
        # 添加超过最大行数的内容
        for i in range(10):
            buffer.append(f"Line {i}\n")
            buffer.flush()
        
        all_text = buffer.get_all()
        lines = all_text.strip().split('\n')
        
        # 应该只保留最后5行
        self.assertLessEqual(len(lines), 5)


class TestCustomThemes(unittest.TestCase):
    """自定义主题测试"""
    
    def setUp(self):
        """测试准备"""
        try:
            from plugins.custom_themes import ThemeConfig, PREDEFINED_THEMES
            self.ThemeConfig = ThemeConfig
            self.PREDEFINED_THEMES = PREDEFINED_THEMES
        except ImportError:
            self.skipTest("自定义主题模块未找到")
    
    def test_theme_config_creation(self):
        """测试主题配置创建"""
        config = self.ThemeConfig("Test Theme", is_dark=False)
        
        self.assertEqual(config.name, "Test Theme")
        self.assertFalse(config.is_dark)
        self.assertIn("bg_primary", config.colors)
        self.assertIn("text_primary", config.colors)
    
    def test_theme_serialization(self):
        """测试主题序列化"""
        config = self.ThemeConfig("Test Theme", is_dark=True)
        config.colors["bg_primary"] = "#123456"
        
        # 转换为字典
        data = config.to_dict()
        
        # 从字典创建
        config2 = self.ThemeConfig.from_dict(data)
        
        self.assertEqual(config2.name, "Test Theme")
        self.assertTrue(config2.is_dark)
        self.assertEqual(config2.colors["bg_primary"], "#123456")
    
    def test_predefined_themes(self):
        """测试预定义主题"""
        self.assertGreater(len(self.PREDEFINED_THEMES), 0)
        
        for key, theme_data in self.PREDEFINED_THEMES.items():
            self.assertIn("name", theme_data)
            self.assertIn("is_dark", theme_data)
            self.assertIn("colors", theme_data)
            
            # 验证必需的颜色键
            colors = theme_data["colors"]
            required_keys = ["bg_primary", "text_primary", "accent_primary"]
            for key in required_keys:
                self.assertIn(key, colors)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_module_imports(self):
        """测试模块导入"""
        # 检查PyQt6是否可用
        try:
            import PyQt6
            has_pyqt6 = True
        except ImportError:
            has_pyqt6 = False
        
        modules_to_test = [
            "plugins.ollama_client",
            "plugins.knowledge_base",
            "plugins.config_manager",
        ]
        
        # 如果PyQt6可用，添加依赖PyQt6的模块
        if has_pyqt6:
            modules_to_test.extend([
                "plugins.custom_themes",
                "bbcode.terminal",
            ])
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"无法导入模块 {module_name}: {e}")
    
    def test_thread_safety(self):
        """测试线程安全性"""
        try:
            from plugins.config_manager import UnifiedConfigManager
            manager = UnifiedConfigManager()
            
            results = []
            errors = []
            
            def writer_thread(thread_id: int):
                try:
                    for i in range(10):
                        manager.set(f"thread_test.{thread_id}", i, validate=False)
                        time.sleep(0.01)
                        value = manager.get(f"thread_test.{thread_id}")
                        results.append((thread_id, value))
                except Exception as e:
                    errors.append(e)
            
            # 创建多个线程同时读写
            threads = []
            for i in range(3):
                t = threading.Thread(target=writer_thread, args=(i,))
                threads.append(t)
                t.start()
            
            # 等待所有线程完成
            for t in threads:
                t.join()
            
            # 检查是否有错误
            self.assertEqual(len(errors), 0, f"线程安全测试出现错误: {errors}")
            
        except ImportError:
            self.skipTest("配置管理模块未找到")


class TestEdgeCases(unittest.TestCase):
    """边界条件测试"""
    
    def test_empty_strings(self):
        """测试空字符串处理"""
        try:
            from plugins.knowledge_base import KnowledgeItem
            
            item = KnowledgeItem(
                title="",
                content="",
                source_file="test.md"
            )
            
            self.assertEqual(item.title, "")
            self.assertEqual(item.content, "")
            self.assertIsNotNone(item.id)
            
        except ImportError:
            self.skipTest("知识库模块未找到")
    
    def test_unicode_content(self):
        """测试Unicode内容处理"""
        try:
            from plugins.knowledge_base import KnowledgeItem
            
            item = KnowledgeItem(
                title="中文标题 🎉",
                content="中文内容 with emojis 🚀",
                source_file="test.md",
                keywords=["中文", "emoji"]
            )
            
            self.assertEqual(item.title, "中文标题 🎉")
            self.assertEqual(item.content, "中文内容 with emojis 🚀")
            
        except ImportError:
            self.skipTest("知识库模块未找到")
    
    def test_very_long_content(self):
        """测试超长内容处理"""
        try:
            from plugins.knowledge_base import KnowledgeItem
            
            long_content = "A" * 100000  # 10万字符
            
            item = KnowledgeItem(
                title="Long Content Test",
                content=long_content,
                source_file="test.md"
            )
            
            self.assertEqual(len(item.content), 100000)
            self.assertIsNotNone(item.id)
            
        except ImportError:
            self.skipTest("知识库模块未找到")
    
    def test_special_characters(self):
        """测试特殊字符处理"""
        try:
            from plugins.knowledge_base import KnowledgeItem
            
            special_title = "Test <script>alert('xss')</script>"
            special_content = "Content with \"quotes\" and 'apostrophes' and \\backslashes\\"
            
            item = KnowledgeItem(
                title=special_title,
                content=special_content,
                source_file="test.md"
            )
            
            self.assertEqual(item.title, special_title)
            self.assertEqual(item.content, special_content)
            
        except ImportError:
            self.skipTest("知识库模块未找到")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestOllamaClient))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeBase))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTerminal))
    suite.addTests(loader.loadTestsFromTestCase(TestCustomThemes))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
