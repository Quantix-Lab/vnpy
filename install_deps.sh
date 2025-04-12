#!/bin/bash

# 更新pip
pip install --upgrade pip

# 确保Qt兼容性 (安装PySide6)
pip install PySide6==6.5.0

# 安装主要vnpy包
pip install vnpy

# 只安装富途接口依赖
pip install vnpy_futu
pip install futu-api

# 安装所有App依赖，除了使用PyQt5信号的模块
pip install vnpy_paperaccount vnpy_ctastrategy vnpy_ctabacktester
pip install vnpy_spreadtrading vnpy_algotrading vnpy_optionmaster
pip install vnpy_portfoliostrategy vnpy_scripttrader vnpy_chartwizard
pip install vnpy_rpcservice vnpy_datamanager
pip install vnpy_datarecorder vnpy_riskmanager vnpy_webtrader
pip install vnpy_portfoliomanager

# 安装其他必要依赖
pip install importlib_metadata
pip install vnpy_sqlite

echo "====================================="
echo "安装完成！只安装了富途接口依赖。"
echo "现在可以运行交易平台：cd examples/veighna_trader && python run.py"
echo "====================================="