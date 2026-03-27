import sys
import os

# Add the script's directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# 先初始化日志系统
from bbcode.logger import logger

logger.info("=" * 50)
logger.info("BBCode 启动")
logger.info(f"Python 版本: {sys.version}")
logger.info(f"工作目录: {os.getcwd()}")
logger.info("=" * 50)

# Now import and run BBCode
try:
    from bbcode.main_window import main
    
    if __name__ == "__main__":
        main()
except Exception as e:
    logger.exception(f"应用程序异常: {e}")
    raise
