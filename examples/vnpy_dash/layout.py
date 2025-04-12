"""
VeighNa Dash - 布局定义
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

def create_layout():
    """创建主布局"""
    return dbc.Container(
        [
            # 顶部导航栏
            create_navbar(),

            # 主内容区域
            dbc.Row(
                [
                    # 侧边栏
                    dbc.Col(create_sidebar(), md=2, className="sidebar-col"),

                    # 内容区域
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    dcc.Loading(
                                        id="loading-content",
                                        children=[html.Div(id="page-content")],
                                        type="circle",
                                    )
                                ),
                                className="content-card my-3"
                            ),
                        ],
                        md=10,
                        className="content-col"
                    ),
                ],
                className="g-0",
            ),

            # 底部状态栏
            create_footer(),

            # 隐藏元素 - 存储当前页面
            dcc.Store(id="current-page", data="home"),

            # 设置模态框
            create_settings_modal(),

            # 连接模态框
            create_connect_modal(),

            # 交易界面刷新间隔
            dcc.Interval(
                id="interval-trading",
                interval=2*1000,  # 2秒
                n_intervals=0,
                disabled=True
            ),
        ],
        fluid=True,
        className="dash-container"
    )

def create_navbar():
    """创建顶部导航栏"""
    return dbc.Navbar(
        dbc.Container(
            [
                # 品牌和Logo
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="/assets/logo.png", height="30px"), width="auto"),
                            dbc.Col(dbc.NavbarBrand("VeighNa Dash", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="#",
                    style={"textDecoration": "none"},
                ),

                # 右侧工具按钮
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Button(
                                [DashIconify(icon="tabler:plug-connected", width=20), " 连接"],
                                id="btn-connect",
                                color="success",
                                className="me-2",
                            ),
                            width="auto",
                        ),
                        dbc.Col(
                            dbc.Button(
                                [DashIconify(icon="tabler:settings", width=20), " 设置"],
                                id="btn-settings",
                                color="primary",
                                className="me-2",
                            ),
                            width="auto",
                        ),
                    ],
                    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
                    align="center",
                ),
            ],
            fluid=True,
        ),
        color="dark",
        dark=True,
        className="mb-3",
    )

def create_sidebar():
    """创建侧边栏"""
    return html.Div(
        [
            dbc.Nav(
                [
                    dbc.NavLink(
                        [DashIconify(icon="tabler:home", width=20), " 主页"],
                        id="page-home",
                        href="#",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [DashIconify(icon="tabler:chart-line", width=20), " 行情"],
                        id="page-market",
                        href="#",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [DashIconify(icon="tabler:arrows-exchange", width=20), " 交易"],
                        id="page-trading",
                        href="#",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [DashIconify(icon="tabler:chart-candlestick", width=20), " 策略"],
                        id="page-strategy",
                        href="#",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [DashIconify(icon="tabler:database", width=20), " 数据"],
                        id="page-data",
                        href="#",
                        active="exact",
                    ),
                    dbc.NavLink(
                        [DashIconify(icon="tabler:clock", width=20), " 回测"],
                        id="page-backtest",
                        href="#",
                        active="exact",
                    ),
                ],
                vertical=True,
                pills=True,
                className="sidebar-nav"
            ),

            html.Hr(),

            # 交易账户状态卡片
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("账户状态", className="card-title"),
                        html.Div(id="account-status", className="account-status"),
                    ]
                ),
                className="mb-3 account-card"
            ),
        ],
        className="sidebar"
    )

def create_footer():
    """创建底部状态栏"""
    return dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id="gateway-status", className="text-left")),
                                dbc.Col(html.Div("VeighNa Dash v1.0.0", className="text-end"))
                            ]
                        )
                    ],
                    className="p-2"
                ),
                className="footer-card"
            )
        ),
        className="mt-auto"
    )

def create_settings_modal():
    """创建设置模态框"""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("平台设置")),
            dbc.ModalBody(
                [
                    dbc.Form(
                        [
                            dbc.Row(
                                [
                                    dbc.Label("主题", width=2),
                                    dbc.Col(
                                        dbc.Select(
                                            id="select-theme",
                                            options=[
                                                {"label": "深色", "value": "dark"},
                                                {"label": "浅色", "value": "light"},
                                            ],
                                            value="dark",
                                        ),
                                        width=10,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("刷新间隔(秒)", width=2),
                                    dbc.Col(
                                        dbc.Input(
                                            id="input-refresh",
                                            type="number",
                                            value=2,
                                            min=1,
                                            max=10,
                                        ),
                                        width=10,
                                    ),
                                ],
                                className="mb-3",
                            ),
                        ]
                    )
                ]
            ),
            dbc.ModalFooter(
                dbc.Button("保存", id="btn-save-settings", className="ms-auto", color="primary")
            ),
        ],
        id="modal-settings",
        size="lg",
        is_open=False,
    )

def create_connect_modal():
    """创建连接模态框"""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("连接富途接口")),
            dbc.ModalBody(
                [
                    dbc.Form(
                        [
                            dbc.Row(
                                [
                                    dbc.Label("API地址", width=3),
                                    dbc.Col(
                                        dbc.Input(
                                            id="input-api-host",
                                            type="text",
                                            value="127.0.0.1",
                                        ),
                                        width=9,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("API端口", width=3),
                                    dbc.Col(
                                        dbc.Input(
                                            id="input-api-port",
                                            type="number",
                                            value=11111,
                                            min=1,
                                            max=65535,
                                        ),
                                        width=9,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("市场环境", width=3),
                                    dbc.Col(
                                        dbc.Select(
                                            id="select-env",
                                            options=[
                                                {"label": "正式环境", "value": "正式环境"},
                                                {"label": "模拟环境", "value": "模拟环境"},
                                            ],
                                            value="模拟环境",
                                        ),
                                        width=9,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("交易接口", width=3),
                                    dbc.Col(
                                        dbc.Checklist(
                                            id="checklist-market",
                                            options=[
                                                {"label": "港股", "value": "港股"},
                                                {"label": "美股", "value": "美股"},
                                                {"label": "A股", "value": "A股"},
                                            ],
                                            value=["港股"],
                                            inline=True,
                                        ),
                                        width=9,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("账号", width=3),
                                    dbc.Col(
                                        dbc.Input(
                                            id="input-account",
                                            type="text",
                                            placeholder="富途牛牛账号",
                                        ),
                                        width=9,
                                    ),
                                ],
                                className="mb-3",
                            ),
                            dbc.Row(
                                [
                                    dbc.Label("密码", width=3),
                                    dbc.Col(
                                        dbc.Input(
                                            id="input-password",
                                            type="password",
                                            placeholder="交易密码",
                                        ),
                                        width=9,
                                    ),
                                ],
                                className="mb-3",
                            ),
                        ]
                    )
                ]
            ),
            dbc.ModalFooter(
                dbc.Button("连接", id="btn-submit-connect", className="ms-auto", color="success")
            ),
        ],
        id="modal-connect",
        size="lg",
        is_open=False,
    )