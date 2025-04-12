"""
VeighNa Dash - Web版本VeighNa交易平台
"""

import os
import sys
from pathlib import Path

# 添加vnpy路径
ROOT_PATH = str(Path(__file__).parent.parent.parent)
sys.path.append(ROOT_PATH)

import dash
from dash import html, dcc, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy_futu import FutuGateway
from vnpy_ctastrategy import CtaStrategyApp
from vnpy_ctabacktester import CtaBacktesterApp
from vnpy_datamanager import DataManagerApp

# 初始化交易引擎
event_engine = EventEngine()
main_engine = MainEngine(event_engine)

# 添加交易接口和应用
main_engine.add_gateway(FutuGateway)
main_engine.add_app(CtaStrategyApp)
main_engine.add_app(CtaBacktesterApp)
main_engine.add_app(DataManagerApp)

# 初始化Dash应用
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "VeighNa Dash"
server = app.server

# 导入应用模块
from layout import create_layout
from callbacks import register_callbacks

# 创建布局
app.layout = create_layout()

# 注册回调
register_callbacks(app, main_engine, event_engine)

# 主程序入口
if __name__ == "__main__":
    app.run_server(debug=True)