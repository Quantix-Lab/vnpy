#!/bin/bash

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: Python 3未安装，请先安装Python 3.10或更高版本"
    exit 1
fi

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "正在创建Python虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate || { echo "无法激活虚拟环境，请检查.venv目录"; exit 1; }

# 更新pip
echo "更新pip..."
pip install --upgrade pip

# 安装必要依赖
echo "安装核心依赖..."
pip install vnpy
pip install vnpy_sqlite
pip install importlib_metadata

# 安装富途接口及API
echo "安装富途接口..."
pip install vnpy_futu
pip install futu-api

# 安装常用应用模块
echo "安装应用模块..."
pip install vnpy_ctastrategy
pip install vnpy_ctabacktester
pip install vnpy_datamanager

# 启动交易平台
echo "===================================="
echo "依赖安装完成！启动VeighNa交易平台..."
echo "===================================="
cd examples/veighna_trader && python run.py