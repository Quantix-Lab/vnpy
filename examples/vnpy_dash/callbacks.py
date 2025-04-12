"""
VeighNa Dash - 回调函数定义
"""

from dash import callback, Input, Output, State, no_update, html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
import pandas as pd

from vnpy.trader.constant import Direction, Offset, OrderType, Status
from vnpy.trader.object import SubscribeRequest, OrderRequest, CancelRequest

# 页面模块导入
from pages.home import create_home_page
from pages.market import create_market_page
from pages.trading import create_trading_page
from pages.strategy import create_strategy_page
from pages.data import create_data_page
from pages.backtest import create_backtest_page

def register_callbacks(app, main_engine, event_engine):
    """注册所有回调函数"""

    # 页面导航回调
    @app.callback(
        Output("page-content", "children"),
        Output("current-page", "data"),
        [
            Input("page-home", "n_clicks"),
            Input("page-market", "n_clicks"),
            Input("page-trading", "n_clicks"),
            Input("page-strategy", "n_clicks"),
            Input("page-data", "n_clicks"),
            Input("page-backtest", "n_clicks"),
        ],
        [State("current-page", "data")],
    )
    def render_page_content(home, market, trading, strategy, data, backtest, current):
        """根据导航切换页面内容"""
        ctx = app.callback_context

        if not ctx.triggered:
            # 默认页面
            return create_home_page(main_engine), "home"

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "page-home":
            return create_home_page(main_engine), "home"
        elif button_id == "page-market":
            return create_market_page(main_engine), "market"
        elif button_id == "page-trading":
            return create_trading_page(main_engine), "trading"
        elif button_id == "page-strategy":
            return create_strategy_page(main_engine), "strategy"
        elif button_id == "page-data":
            return create_data_page(main_engine), "data"
        elif button_id == "page-backtest":
            return create_backtest_page(main_engine), "backtest"

        # 默认情况
        return create_home_page(main_engine), "home"

    # 设置模态框回调
    @app.callback(
        Output("modal-settings", "is_open"),
        [Input("btn-settings", "n_clicks"), Input("btn-save-settings", "n_clicks")],
        [State("modal-settings", "is_open")],
    )
    def toggle_settings_modal(n1, n2, is_open):
        """切换设置模态框显示状态"""
        if n1 or n2:
            return not is_open
        return is_open

    # 连接模态框回调
    @app.callback(
        Output("modal-connect", "is_open"),
        [Input("btn-connect", "n_clicks"), Input("btn-submit-connect", "n_clicks")],
        [State("modal-connect", "is_open")],
    )
    def toggle_connect_modal(n1, n2, is_open):
        """切换连接模态框显示状态"""
        if n1 or n2:
            return not is_open
        return is_open

    # 连接富途接口回调
    @app.callback(
        Output("gateway-status", "children"),
        Input("btn-submit-connect", "n_clicks"),
        [
            State("input-api-host", "value"),
            State("input-api-port", "value"),
            State("select-env", "value"),
            State("checklist-market", "value"),
            State("input-account", "value"),
            State("input-password", "value"),
        ],
    )
    def connect_futu_gateway(n_clicks, host, port, env, markets, account, password):
        """连接富途接口"""
        if not n_clicks:
            return "未连接"

        # 检查参数
        if not host or not port or not markets:
            return html.Span("参数不完整", style={"color": "red"})

        # 构建设置字典
        setting = {
            "API地址": host,
            "API端口": port,
            "市场环境": env,
            "交易服务器": markets,
            "牛牛账号": account or "",
            "密码": password or "",
        }

        # 连接接口
        try:
            main_engine.connect(setting, "FUTU")
            return html.Span("富途接口已连接", style={"color": "green"})
        except Exception as e:
            return html.Span(f"连接失败: {str(e)}", style={"color": "red"})

    # 刷新账户状态回调
    @app.callback(
        Output("account-status", "children"),
        Input("interval-trading", "n_intervals"),
    )
    def update_account_status(n):
        """更新账户状态"""
        # 如果没有账户信息，显示未连接
        accounts = main_engine.get_all_accounts()
        if not accounts:
            return html.Div("未连接")

        # 显示账户信息
        account_cards = []
        for account in accounts:
            account_cards.append(
                html.Div(
                    [
                        html.P(f"账户: {account.accountid}"),
                        html.P(f"余额: {account.balance:.2f}"),
                        html.P(f"可用: {account.available:.2f}"),
                    ],
                    className="account-info"
                )
            )

        return html.Div(account_cards)

    # 订阅行情回调
    @app.callback(
        Output("subscribe-status", "children"),
        Input("btn-subscribe", "n_clicks"),
        [
            State("input-symbol", "value"),
            State("select-exchange", "value"),
        ],
    )
    def subscribe_symbol(n_clicks, symbol, exchange):
        """订阅合约行情"""
        if not n_clicks or not symbol or not exchange:
            return no_update

        # 创建订阅请求
        req = SubscribeRequest(
            symbol=symbol,
            exchange=exchange
        )

        # 发送订阅请求
        main_engine.subscribe(req, "FUTU")

        return f"已订阅: {symbol}.{exchange}"