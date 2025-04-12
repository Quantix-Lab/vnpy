import ctypes
import platform
import sys
import traceback
import webbrowser
import types
import threading
import os
from pathlib import Path

import qdarkstyle  # type: ignore
from PySide6 import QtGui, QtWidgets, QtCore
from loguru import logger

from ..setting import SETTINGS
from ..utility import get_icon_path
from ..locale import _


Qt = QtCore.Qt


def create_qapp(app_name: str = "VeighNa Trader") -> QtWidgets.QApplication:
    """
    Create Qt Application with modern UI and customization options.
    """
    # Set up application
    qapp: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)

    # Get theme setting
    theme = SETTINGS.get("ui.theme", "dark")
    use_custom_style = SETTINGS.get("ui.custom_style", True)

    # Apply theme
    if theme == "dark":
        if use_custom_style:
            # Apply modern dark theme with blue accents
            apply_modern_dark_theme(qapp)
        else:
            # Use qdarkstyle as fallback
            qapp.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))
    else:
        # Light theme (system default with some enhancements)
        apply_light_theme(qapp)

    # Set up font
    font_family = SETTINGS.get("font.family", "Segoe UI" if sys.platform == "win32" else "SF Pro Display" if sys.platform == "darwin" else "Noto Sans")
    font_size = SETTINGS.get("font.size", 10)
    font: QtGui.QFont = QtGui.QFont(font_family, font_size)
    qapp.setFont(font)

    # Set up icon
    icon_path = SETTINGS.get("ui.icon_path", get_icon_path(__file__, "vnpy.ico"))
    icon: QtGui.QIcon = QtGui.QIcon(icon_path)
    qapp.setWindowIcon(icon)

    # Set up effects
    if SETTINGS.get("ui.animations", True):
        enable_animations()

    # Set up HiDPI support
    if SETTINGS.get("ui.hidpi", True):
        enable_hidpi_support()

    # Set up windows process ID
    if "Windows" in platform.uname():
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            app_name
        )

    # Exception Handling
    exception_widget: ExceptionWidget = ExceptionWidget()

    def excepthook(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: types.TracebackType | None
    ) -> None:
        """Show exception detail with QMessageBox."""
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).error("Main thread exception")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

        msg: str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        exception_widget.signal.emit(msg)

    sys.excepthook = excepthook

    def threading_excepthook(args: threading.ExceptHookArgs) -> None:
        """Show exception detail from background threads with QMessageBox."""
        if args.exc_value and args.exc_traceback:
            logger.opt(exception=(args.exc_type, args.exc_value, args.exc_traceback)).error("Background thread exception")
            sys.__excepthook__(args.exc_type, args.exc_value, args.exc_traceback)

        msg: str = "".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
        exception_widget.signal.emit(msg)

    threading.excepthook = threading_excepthook

    return qapp


def apply_modern_dark_theme(app: QtWidgets.QApplication) -> None:
    """Apply a modern dark theme with blue accents"""
    palette = QtGui.QPalette()

    # Base colors
    dark_color = QtGui.QColor(30, 30, 46)      # Background
    darker_color = QtGui.QColor(24, 24, 37)    # Alternate background
    text_color = QtGui.QColor(205, 214, 244)   # Text
    highlight_color = QtGui.QColor(137, 180, 250)  # Blue highlight
    button_color = QtGui.QColor(69, 71, 90)    # Button

    # Set up the palette
    palette.setColor(QtGui.QPalette.Window, dark_color)
    palette.setColor(QtGui.QPalette.WindowText, text_color)
    palette.setColor(QtGui.QPalette.Base, darker_color)
    palette.setColor(QtGui.QPalette.AlternateBase, dark_color)
    palette.setColor(QtGui.QPalette.ToolTipBase, dark_color)
    palette.setColor(QtGui.QPalette.ToolTipText, text_color)
    palette.setColor(QtGui.QPalette.Text, text_color)
    palette.setColor(QtGui.QPalette.Button, button_color)
    palette.setColor(QtGui.QPalette.ButtonText, text_color)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Link, highlight_color)
    palette.setColor(QtGui.QPalette.Highlight, highlight_color)
    palette.setColor(QtGui.QPalette.HighlightedText, darker_color)

    app.setPalette(palette)

    # Try to load custom stylesheet
    style_file = Path(__file__).parent.parent.parent.parent / "examples" / "veighna_trader" / "custom_style.qss"
    if style_file.exists():
        with open(style_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        # Fallback to qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))


def apply_light_theme(app: QtWidgets.QApplication) -> None:
    """Apply a modern light theme"""
    palette = QtGui.QPalette()

    # Base colors
    light_color = QtGui.QColor(245, 245, 245)     # Background
    lighter_color = QtGui.QColor(252, 252, 252)   # Alternate background
    text_color = QtGui.QColor(50, 50, 50)         # Text
    highlight_color = QtGui.QColor(57, 142, 231)  # Blue highlight
    button_color = QtGui.QColor(230, 230, 230)    # Button

    # Set up the palette
    palette.setColor(QtGui.QPalette.Window, light_color)
    palette.setColor(QtGui.QPalette.WindowText, text_color)
    palette.setColor(QtGui.QPalette.Base, lighter_color)
    palette.setColor(QtGui.QPalette.AlternateBase, light_color)
    palette.setColor(QtGui.QPalette.ToolTipBase, lighter_color)
    palette.setColor(QtGui.QPalette.ToolTipText, text_color)
    palette.setColor(QtGui.QPalette.Text, text_color)
    palette.setColor(QtGui.QPalette.Button, button_color)
    palette.setColor(QtGui.QPalette.ButtonText, text_color)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Link, highlight_color)
    palette.setColor(QtGui.QPalette.Highlight, highlight_color)
    palette.setColor(QtGui.QPalette.HighlightedText, lighter_color)

    app.setPalette(palette)


def enable_animations() -> None:
    """Enable Qt animations for smoother UI"""
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)


def enable_hidpi_support() -> None:
    """Enable HiDPI support for better display on high resolution screens"""
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class ExceptionWidget(QtWidgets.QWidget):
    """"""
    signal: QtCore.Signal = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """"""
        super().__init__(parent)

        self.init_ui()
        self.signal.connect(self.show_exception)

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle(_("触发异常"))
        self.setFixedSize(600, 600)

        self.msg_edit: QtWidgets.QTextEdit = QtWidgets.QTextEdit()
        self.msg_edit.setReadOnly(True)

        copy_button: QtWidgets.QPushButton = QtWidgets.QPushButton(_("复制"))
        copy_button.setIcon(QtGui.QIcon(get_icon_path(__file__, "copy.ico")))
        copy_button.clicked.connect(self._copy_text)

        community_button: QtWidgets.QPushButton = QtWidgets.QPushButton(_("求助"))
        community_button.setIcon(QtGui.QIcon(get_icon_path(__file__, "help.ico")))
        community_button.clicked.connect(self._open_community)

        close_button: QtWidgets.QPushButton = QtWidgets.QPushButton(_("关闭"))
        close_button.setIcon(QtGui.QIcon(get_icon_path(__file__, "close.ico")))
        close_button.clicked.connect(self.close)

        hbox: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()
        hbox.addWidget(copy_button)
        hbox.addWidget(community_button)
        hbox.addWidget(close_button)

        vbox: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.msg_edit)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

    def show_exception(self, msg: str) -> None:
        """"""
        self.msg_edit.setText(msg)
        self.show()

    def _copy_text(self) -> None:
        """"""
        self.msg_edit.selectAll()
        self.msg_edit.copy()

    def _open_community(self) -> None:
        """"""
        webbrowser.open("https://www.vnpy.com/forum/forum/2-ti-wen-qiu-zhu")
