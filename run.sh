#!/bin/bash
# 这个脚本用来启动VeighNa交易平台

# 检查Python 3.10是否存在
if command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
else
    PYTHON_CMD="python3"
    echo "警告: 未找到python3.10，使用python3替代"
fi

# 使用Python创建虚拟环境
$PYTHON_CMD -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 设置虚拟环境中的Python命令
VENV_PYTHON=".venv/bin/python"

# 显示Python版本确认激活成功
$VENV_PYTHON --version

# 安装富途网关包（如果目录不存在，这一步会失败，但不会影响后续步骤）
if [ -d "../vnpy_futu" ]; then
    $VENV_PYTHON -m pip install -e ../vnpy_futu
fi

# 运行VeighNa交易平台
echo "启动VeighNa交易平台..."
$VENV_PYTHON examples/veighna_trader/run.py