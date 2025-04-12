#!/bin/bash

# 更新pip
pip install --upgrade pip

# 安装核心依赖
pip install vnpy
pip install vnpy_sqlite
pip install importlib_metadata

# 安装富途接口
pip install vnpy_futu
pip install futu-api

# 安装最常用的应用模块
pip install vnpy_ctastrategy
pip install vnpy_ctabacktester
pip install vnpy_datamanager

echo "============================================"
echo "最小化安装完成！"
echo "您已安装了以下组件："
echo "- vnpy核心"
echo "- vnpy_sqlite (数据库)"
echo "- vnpy_futu (富途接口)"
echo "- futu-api (富途API)"
echo "- vnpy_ctastrategy (CTA策略模块)"
echo "- vnpy_ctabacktester (CTA回测模块)"
echo "- vnpy_datamanager (数据管理模块)"
echo ""
echo "运行交易平台: cd examples/veighna_trader && python run.py"
echo "============================================"