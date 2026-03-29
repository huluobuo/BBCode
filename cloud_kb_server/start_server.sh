#!/bin/bash

echo ""
echo "============================================"
echo "  BBCode 云知识库服务器（简化版）"
echo "============================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请确保 Python3 已安装"
    exit 1
fi

echo "[信息] Python 版本:"
python3 --version
echo ""

# 检查依赖
echo "[信息] 检查依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "[信息] 正在安装依赖..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[错误] 安装依赖失败"
        exit 1
    fi
fi

echo "[信息] 依赖已安装"
echo ""

echo "[信息] 启动服务器..."
echo "[信息] 支持局域网访问，其他设备可通过局域网IP连接"
echo ""

# 启动服务器（自动显示所有访问地址）
python3 server.py
