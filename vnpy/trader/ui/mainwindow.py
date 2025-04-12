"""
Implements main window of the trading platform.
"""

from types import ModuleType
import webbrowser
from functools import partial
from importlib import import_module
from typing import TypeVar, Dict
from collections.abc import Callable
import platform
import sys
from datetime import datetime

import vnpy
from vnpy.event import EventEngine

from .qt import QtCore, QtGui, QtWidgets
from .widget import (
    BaseMonitor,
    TickMonitor,
    OrderMonitor,
    TradeMonitor,
    PositionMonitor,
    AccountMonitor,
    LogMonitor,
    ActiveOrderMonitor,
    ConnectDialog,
    ContractManager,
    TradingWidget,
    AboutDialog,
    GlobalDialog
)
from ..engine import MainEngine, BaseApp
from ..utility import get_icon_path, TRADER_DIR
from ..locale import _


WidgetType = TypeVar("WidgetType", bound="QtWidgets.QWidget")


class MainWindow(QtWidgets.QMainWindow):
    """
    Main window of the trading platform.
    """

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine) -> None:
        """"""
        super().__init__()

        self.main_engine: MainEngine = main_engine
        self.event_engine: EventEngine = event_engine

        self.connect_status: Dict[str, bool] = {}

        self.window_title: str = _("VeighNa量化交易平台")

        self.widgets: Dict[str, QtWidgets.QWidget] = {}
        self.monitors: Dict[str, BaseMonitor] = {}

        self.init_ui()
        self.init_shortcut()

        # 定时器更新状态栏
        self.statusTimer = QtCore.QTimer()
        self.statusTimer.timeout.connect(self.update_status)
        self.statusTimer.start(1000)  # 每秒更新一次

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle(self.window_title)

        # 设置图标
        icon = QtGui.QIcon(get_icon_path(__file__, "vnpy.ico"))
        self.setWindowIcon(icon)

        # 设置应用样式
        self.setStyleSheet("""
            QStatusBar {
                min-height: 25px;
                background-color: #181825;
                border-top: 1px solid #313244;
            }

            QToolBar {
                background-color: #181825;
                border-bottom: 1px solid #313244;
                spacing: 5px;
            }

            QToolButton {
                padding: 5px;
                border: none;
                border-radius: 2px;
            }

            QToolButton:hover {
                background-color: #313244;
            }

            QDockWidget {
                font-weight: bold;
            }

            QDockWidget::title {
                background-color: #1e1e2e;
                padding: 6px;
                border: none;
            }

            QTabBar::tab {
                min-width: 100px;
                padding: 8px 12px;
            }
        """)

        # 创建中央组件
        self.init_central_widget()

        # 创建工具栏
        self.init_toolbar()

        # 创建菜单栏
        self.init_menu()

        # 创建停靠组件
        self.init_dock()

        # 设置状态栏
        self.statusBar().showMessage(_("交易平台启动完成，欢迎使用！"))

        # 添加状态图标
        self.connectStatus = QtWidgets.QLabel()
        self.connectStatus.setPixmap(
            QtGui.QIcon(get_icon_path(__file__, "connect.ico")).pixmap(18, 18)
        )
        self.connectStatus.setDisabled(True)  # 灰色
        self.statusBar().addPermanentWidget(self.connectStatus)

        # 添加服务器时间
        self.timeLabel = QtWidgets.QLabel()
        self.statusBar().addPermanentWidget(self.timeLabel)

        # 窗口设置
        self.resize(1100, 700)
        self.setMinimumWidth(1000)
        self.setMinimumHeight(700)

        # 设置启动方式
        if sys.platform == "darwin":  # macOS
            self.setUnifiedTitleAndToolBarOnMac(True)

        # 设置位置为屏幕中央
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.move(
            int(screen.width() / 2 - self.width() / 2),
            int(screen.height() / 2 - self.height() / 2)
        )

    def init_central_widget(self) -> None:
        """创建中央组件，显示欢迎页面和系统信息"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        # 欢迎标题
        title_label = QtWidgets.QLabel(_("VeighNa量化交易平台"))
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
            color: #89b4fa;
        """)

        # 添加logo
        logo_label = QtWidgets.QLabel()
        logo_pixmap = QtGui.QPixmap(get_icon_path(__file__, "vnpy.ico"))
        if not logo_pixmap.isNull():
            logo_scaled = logo_pixmap.scaled(
                128, 128,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            logo_label.setPixmap(logo_scaled)
            logo_label.setAlignment(QtCore.Qt.AlignCenter)

        # 添加系统信息面板
        info_groupbox = QtWidgets.QGroupBox(_("系统信息"))
        info_layout = QtWidgets.QFormLayout()

        # 获取系统信息
        cpuLabel = QtWidgets.QLabel(platform.processor())
        osLabel = QtWidgets.QLabel(f"{platform.system()} {platform.release()}")
        pythonLabel = QtWidgets.QLabel(platform.python_version())
        qtLabel = QtWidgets.QLabel(f"PySide6 {QtCore.__version__}")

        # 添加到布局
        info_layout.addRow(_("处理器:"), cpuLabel)
        info_layout.addRow(_("操作系统:"), osLabel)
        info_layout.addRow(_("Python版本:"), pythonLabel)
        info_layout.addRow(_("Qt版本:"), qtLabel)

        # 添加VeighNa版本
        try:
            from vnpy import __version__ as vnpy_version
            vnpyLabel = QtWidgets.QLabel(vnpy_version)
            info_layout.addRow(_("VeighNa版本:"), vnpyLabel)
        except:
            pass

        info_groupbox.setLayout(info_layout)

        # 快速启动区
        start_groupbox = QtWidgets.QGroupBox(_("快速启动"))
        start_layout = QtWidgets.QHBoxLayout()

        # 创建快速启动按钮
        connect_button = self.create_action_button(
            icon_name="connect.ico",
            text=_("连接接口"),
            function=self.open_connect_dialog
        )

        market_button = self.create_action_button(
            icon_name="database.ico",
            text=_("行情监控"),
            function=self.open_widget_market
        )

        trade_button = self.create_action_button(
            icon_name="contract.ico",
            text=_("交易监控"),
            function=self.open_widget_trading
        )

        # 添加按钮到布局
        start_layout.addWidget(connect_button)
        start_layout.addWidget(market_button)
        start_layout.addWidget(trade_button)

        start_groupbox.setLayout(start_layout)

        # 组合所有元素
        layout.addWidget(title_label)
        layout.addWidget(logo_label)
        layout.addWidget(info_groupbox)
        layout.addWidget(start_groupbox)
        layout.addStretch()

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_action_button(self, icon_name: str, text: str, function) -> QtWidgets.QPushButton:
        """创建快速操作按钮"""
        button = QtWidgets.QPushButton(text)
        button.setIcon(QtGui.QIcon(get_icon_path(__file__, icon_name)))
        button.setIconSize(QtCore.QSize(32, 32))
        button.clicked.connect(function)
        button.setMinimumHeight(64)
        button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px 16px;
                text-align: center;
                border-radius: 4px;
                border: 1px solid #313244;
            }
            QPushButton:hover {
                background-color: #313244;
            }
        """)
        return button

    def init_shortcut(self) -> None:
        """"""
        # Add any necessary shortcut initialization
        pass

    def init_dock(self) -> None:
        """"""
        self.trading_widget, trading_dock = self.create_dock(
            TradingWidget, _("交易"), QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
        )
        tick_widget, tick_dock = self.create_dock(
            TickMonitor, _("行情"), QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        order_widget, order_dock = self.create_dock(
            OrderMonitor, _("委托"), QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        active_widget, active_dock = self.create_dock(
            ActiveOrderMonitor, _("活动"), QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        trade_widget, trade_dock = self.create_dock(
            TradeMonitor, _("成交"), QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        log_widget, log_dock = self.create_dock(
            LogMonitor, _("日志"), QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
        )
        account_widget, account_dock = self.create_dock(
            AccountMonitor, _("资金"), QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
        )
        position_widget, position_dock = self.create_dock(
            PositionMonitor, _("持仓"), QtCore.Qt.DockWidgetArea.BottomDockWidgetArea
        )

        self.tabifyDockWidget(active_dock, order_dock)

        self.save_window_setting("default")

        tick_widget.itemDoubleClicked.connect(self.trading_widget.update_with_cell)
        position_widget.itemDoubleClicked.connect(self.trading_widget.update_with_cell)

    def init_menu(self) -> None:
        """"""
        bar: QtWidgets.QMenuBar = self.menuBar()
        bar.setNativeMenuBar(False)     # for mac and linux

        # System menu
        sys_menu: QtWidgets.QMenu = bar.addMenu(_("系统"))

        gateway_names: list = self.main_engine.get_all_gateway_names()
        for name in gateway_names:
            func: Callable = partial(self.connect_gateway, name)
            self.add_action(
                sys_menu,
                _("连接{}").format(name),
                get_icon_path(__file__, "connect.ico"),
                func
            )

        sys_menu.addSeparator()

        self.add_action(
            sys_menu,
            _("退出"),
            get_icon_path(__file__, "exit.ico"),
            self.close
        )

        # App menu
        app_menu: QtWidgets.QMenu = bar.addMenu(_("功能"))

        all_apps: list[BaseApp] = self.main_engine.get_all_apps()
        for app in all_apps:
            ui_module: ModuleType = import_module(app.app_module + ".ui")
            widget_class: type[QtWidgets.QWidget] = getattr(ui_module, app.widget_name)

            func = partial(self.open_widget, widget_class, app.app_name)

            self.add_action(app_menu, app.display_name, app.icon_name, func, True)

        # Global setting editor
        action: QtGui.QAction = QtGui.QAction(_("配置"), self)
        action.triggered.connect(self.edit_global_setting)
        bar.addAction(action)

        # Help menu
        help_menu: QtWidgets.QMenu = bar.addMenu(_("帮助"))

        self.add_action(
            help_menu,
            _("查询合约"),
            get_icon_path(__file__, "contract.ico"),
            partial(self.open_widget, ContractManager, "contract"),
            True
        )

        self.add_action(
            help_menu,
            _("还原窗口"),
            get_icon_path(__file__, "restore.ico"),
            self.restore_window_setting
        )

        self.add_action(
            help_menu,
            _("测试邮件"),
            get_icon_path(__file__, "email.ico"),
            self.send_test_email
        )

        self.add_action(
            help_menu,
            _("社区论坛"),
            get_icon_path(__file__, "forum.ico"),
            self.open_forum,
            True
        )

        self.add_action(
            help_menu,
            _("关于"),
            get_icon_path(__file__, "about.ico"),
            partial(self.open_widget, AboutDialog, "about"),
        )

    def init_toolbar(self) -> None:
        """"""
        self.toolbar: QtWidgets.QToolBar = QtWidgets.QToolBar(self)
        self.toolbar.setObjectName(_("工具栏"))
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)

        # Set button size
        w: int = 40
        size = QtCore.QSize(w, w)
        self.toolbar.setIconSize(size)

        # Set button spacing
        layout: QtWidgets.QLayout | None = self.toolbar.layout()
        if layout:
            layout.setSpacing(10)

        self.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

    def add_action(
        self,
        menu: QtWidgets.QMenu,
        action_name: str,
        icon_name: str,
        func: Callable,
        toolbar: bool = False
    ) -> None:
        """"""
        icon: QtGui.QIcon = QtGui.QIcon(icon_name)

        action: QtGui.QAction = QtGui.QAction(action_name, self)
        action.triggered.connect(func)
        action.setIcon(icon)

        menu.addAction(action)

        if toolbar:
            self.toolbar.addAction(action)

    def create_dock(self, widget_class: QtWidgets.QWidget, name: str, direction: QtCore.Qt.DockWidgetArea = None) -> QtWidgets.QDockWidget:
        """创建停靠组件，增加现代感"""
        widget = widget_class(self.main_engine, self.event_engine)

        dock = QtWidgets.QDockWidget(name)
        dock.setWidget(widget)
        dock.setObjectName(name)
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)

        # 添加图标
        if "市场" in name:
            icon_name = "database.ico"
        elif "持仓" in name:
            icon_name = "test.ico"
        elif "成交" in name:
            icon_name = "contract.ico"
        elif "委托" in name:
            icon_name = "editor.ico"
        elif "日志" in name:
            icon_name = "forum.ico"
        else:
            icon_name = "about.ico"

        # 设置标题栏样式
        title_bar = dock.titleBarWidget()
        if title_bar:
            title_layout = QtWidgets.QHBoxLayout(title_bar)
            title_layout.setContentsMargins(5, 0, 5, 0)

            icon_label = QtWidgets.QLabel()
            icon_label.setPixmap(QtGui.QIcon(get_icon_path(__file__, icon_name)).pixmap(16, 16))
            title_layout.addWidget(icon_label)

            name_label = QtWidgets.QLabel(name)
            name_label.setStyleSheet("font-weight: bold;")
            title_layout.addWidget(name_label)
            title_layout.addStretch()

        if direction:
            self.addDockWidget(direction, dock)
        else:
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)

        return dock

    def connect_gateway(self, gateway_name: str) -> None:
        """
        Open connect dialog for gateway connection.
        """
        dialog: ConnectDialog = ConnectDialog(self.main_engine, gateway_name)
        dialog.exec()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Call main engine close function before exit.
        """
        reply = QtWidgets.QMessageBox.question(
            self,
            _("退出"),
            _("确认退出？"),
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            for widget in self.widgets.values():
                widget.close()

            for monitor in self.monitors.values():
                monitor.save_setting()

            self.save_window_setting("custom")

            self.main_engine.close()

            event.accept()
        else:
            event.ignore()

    def open_widget(self, widget_class: type[QtWidgets.QWidget], name: str) -> None:
        """
        Open contract manager.
        """
        widget: QtWidgets.QWidget | None = self.widgets.get(name, None)
        if not widget:
            widget = widget_class(self.main_engine, self.event_engine)      # type: ignore
            self.widgets[name] = widget

        if isinstance(widget, QtWidgets.QDialog):
            widget.exec()
        else:
            widget.show()

    def save_window_setting(self, name: str) -> None:
        """
        Save current window size and state by trader path and setting name.
        """
        settings: QtCore.QSettings = QtCore.QSettings(self.window_title, name)
        settings.setValue("state", self.saveState())
        settings.setValue("geometry", self.saveGeometry())

    def load_window_setting(self, name: str) -> None:
        """
        Load previous window size and state by trader path and setting name.
        """
        settings: QtCore.QSettings = QtCore.QSettings(self.window_title, name)
        state = settings.value("state")
        geometry = settings.value("geometry")

        if isinstance(state, QtCore.QByteArray):
            self.restoreState(state)
            self.restoreGeometry(geometry)

    def restore_window_setting(self) -> None:
        """
        Restore window to default setting.
        """
        self.load_window_setting("default")
        self.showMaximized()

    def send_test_email(self) -> None:
        """
        Sending a test email.
        """
        self.main_engine.send_email("VeighNa Trader", "testing", None)

    def open_forum(self) -> None:
        """
        """
        webbrowser.open("https://www.vnpy.com/forum/")

    def edit_global_setting(self) -> None:
        """
        """
        dialog: GlobalDialog = GlobalDialog()
        dialog.exec()

    def update_status(self) -> None:
        """更新状态栏信息"""
        # 更新时间
        time_now = datetime.now().strftime("%H:%M:%S")
        self.timeLabel.setText(f"{_('系统时间')}: {time_now}")

        # 更新连接状态
        connected = False
        for gateway_name in self.main_engine.get_all_gateway_names():
            status = self.main_engine.get_gateway(gateway_name).status
            if status:  # 任何一个接口连接，就显示为已连接
                connected = True
                break

        if connected:
            self.connectStatus.setDisabled(False)  # 正常显示
        else:
            self.connectStatus.setDisabled(True)   # 灰色显示
