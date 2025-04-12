import os
import sys
from pathlib import Path

# 添加vnpy路径
current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
sys.path.append(str(root_dir))

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

# 只保留富途接口，注释掉其他所有接口
# from vnpy_ctp import CtpGateway
# from vnpy_ctptest import CtptestGateway
# from vnpy_mini import MiniGateway
# from vnpy_femas import FemasGateway
# from vnpy_sopt import SoptGateway
# from vnpy_sec import SecGateway
# from vnpy_uft import UftGateway
# from vnpy_esunny import EsunnyGateway
# from vnpy_xtp import XtpGateway
# from vnpy_tora import ToraStockGateway
# from vnpy_tora import ToraOptionGateway
# from vnpy_comstar import ComstarGateway
# from vnpy_ib import IbGateway
# from vnpy_tap import TapGateway
# from vnpy_da import DaGateway
# from vnpy_rohon import RohonGateway
# from vnpy_tts import TtsGateway
# from vnpy_ost import OstGateway
# from vnpy_hft import GtjaGateway
from vnpy_futu import FutuGateway

# 启用所有应用模块
from vnpy_paperaccount import PaperAccountApp
from vnpy_ctastrategy import CtaStrategyApp
from vnpy_ctabacktester import CtaBacktesterApp
from vnpy_spreadtrading import SpreadTradingApp
from vnpy_algotrading import AlgoTradingApp
from vnpy_optionmaster import OptionMasterApp
from vnpy_portfoliostrategy import PortfolioStrategyApp
from vnpy_scripttrader import ScriptTraderApp
from vnpy_chartwizard import ChartWizardApp
from vnpy_rpcservice import RpcServiceApp
# 注释掉ExcelRtd模块，因为它使用了PyQt5信号，与PySide6不兼容
# from vnpy_excelrtd import ExcelRtdApp
from vnpy_datamanager import DataManagerApp
from vnpy_datarecorder import DataRecorderApp
from vnpy_riskmanager import RiskManagerApp
from vnpy_webtrader import WebTraderApp
from vnpy_portfoliomanager import PortfolioManagerApp

# Qt模块
from PySide6 import QtWidgets, QtCore, QtGui

# 设置UI相关常量
TITLE = "VeighNa量化交易平台 [优化版]"
ICON_PATH = str(current_dir.joinpath("assets/logo.png"))
STYLE_FILE = current_dir.joinpath("custom_style.qss")

# 配置UI设置
UI_SETTINGS = {
    "font.family": "Segoe UI" if sys.platform == "win32" else "SF Pro Display" if sys.platform == "darwin" else "Noto Sans",
    "font.size": 10,
    "ui.theme": "dark",
    "ui.custom_style": True,
    "ui.animations": True,
    "ui.hidpi": True
}


def load_stylesheet():
    """加载自定义样式表"""
    if STYLE_FILE.exists():
        with open(STYLE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def customize_ui(qapp):
    """自定义UI样式和字体"""
    # 设置应用图标
    if Path(ICON_PATH).exists():
        app_icon = QtGui.QIcon(ICON_PATH)
    else:
        # 使用默认图标
        app_icon = QtGui.QIcon(str(current_dir.joinpath("vnpy.ico")))
    qapp.setWindowIcon(app_icon)

    # 应用自定义样式表
    style = load_stylesheet()
    if style:
        qapp.setStyleSheet(style)

    # 设置更现代化的字体
    font = QtGui.QFont(UI_SETTINGS["font.family"], UI_SETTINGS["font.size"])
    qapp.setFont(font)

    # 设置调色板
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(30, 30, 46))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(205, 214, 244))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(24, 24, 37))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(30, 30, 46))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(205, 214, 244))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(69, 71, 90))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(205, 214, 244))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(137, 180, 250))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(24, 24, 37))
    qapp.setPalette(palette)

    # 启用高DPI支持
    if UI_SETTINGS["ui.hidpi"]:
        if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


def check_environment():
    """检查运行环境并提供相关提示"""
    # 检测Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print(f"警告: 当前Python版本 {python_version.major}.{python_version.minor}.{python_version.micro}, "
              f"推荐使用Python 3.7或更高版本")

    # 检测操作系统
    if sys.platform == "win32":
        # Windows特定检查
        pass
    elif sys.platform == "darwin":
        # macOS特定检查
        if not os.environ.get("QT_MAC_WANTS_LAYER", ""):
            print("提示: 在macOS上运行时, 设置环境变量QT_MAC_WANTS_LAYER=1可能会提高UI性能")

    # 检测是否在虚拟环境中运行
    in_venv = sys.prefix != sys.base_prefix
    if not in_venv:
        print("提示: 建议在虚拟环境中运行以避免依赖冲突")

    # 检测显示器分辨率 - 修复QApplication单例问题
    try:
        # 使用非UI的方式检测DPI
        if sys.platform == "win32":
            import ctypes
            user32 = ctypes.windll.user32
            dpi = user32.GetDpiForSystem()
            if dpi > 96:  # 标准DPI是96
                print(f"检测到高DPI显示器 ({dpi} DPI), 已启用高DPI支持")
        elif sys.platform == "darwin":
            # macOS默认都支持高DPI，无需检测
            pass
        elif sys.platform == "linux":
            # 可以通过xrandr检测，但是需要额外依赖，这里简化处理
            pass
    except:
        # 如果检测失败，不影响程序运行
        pass


def main():
    """启动VeighNa交易平台"""
    # 环境检查
    check_environment()

    # 创建Qt应用
    qapp = create_qapp(TITLE)

    # 自定义UI样式
    customize_ui(qapp)

    # 创建事件引擎
    event_engine = EventEngine()

    # 创建主引擎
    main_engine = MainEngine(event_engine)

    # 添加交易接口 - 仅富途
    main_engine.add_gateway(FutuGateway)

    # 添加应用模块
    main_engine.add_app(PaperAccountApp)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(CtaBacktesterApp)
    main_engine.add_app(SpreadTradingApp)
    main_engine.add_app(AlgoTradingApp)
    main_engine.add_app(OptionMasterApp)
    main_engine.add_app(PortfolioStrategyApp)
    main_engine.add_app(ScriptTraderApp)
    main_engine.add_app(ChartWizardApp)
    main_engine.add_app(RpcServiceApp)
    # 不加载有PyQt兼容性问题的模块
    # main_engine.add_app(ExcelRtdApp)
    main_engine.add_app(DataManagerApp)
    main_engine.add_app(DataRecorderApp)
    main_engine.add_app(RiskManagerApp)
    main_engine.add_app(WebTraderApp)
    main_engine.add_app(PortfolioManagerApp)

    # 创建主窗口
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    # 在macOS上设置标题栏风格
    if sys.platform == "darwin":  # macOS
        main_window.setUnifiedTitleAndToolBarOnMac(True)

    # 显示启动信息
    print(f"启动成功: {TITLE}")
    print(f"版本信息: VeighNa {getattr(sys.modules.get('vnpy', None), '__version__', '未知')}")
    print(f"Python版本: {sys.version}")
    print(f"Qt版本: PySide6 {QtCore.__version__}")
    print(f"系统平台: {sys.platform}")

    # 执行应用
    qapp.exec()


if __name__ == "__main__":
    main()
