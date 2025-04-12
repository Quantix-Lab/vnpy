from datetime import datetime
import sys

import pyqtgraph as pg      # type: ignore
import matplotlib.pyplot as plt

from vnpy.trader.ui import QtGui, QtWidgets, QtCore
from vnpy.trader.object import BarData

from .manager import BarManager
from .base import (
    GREY_COLOR, WHITE_COLOR, CURSOR_COLOR, BLACK_COLOR,
    to_int, NORMAL_FONT
)
from .axis import DatetimeAxis
from .item import ChartItem


pg.setConfigOptions(antialias=True)


class ChartWidget(QtWidgets.QWidget):
    """
    Chart widget for showing candle bar data.
    """

    signal_new_bar = QtCore.Signal(ObjectDict)

    def __init__(self, parent: QtWidgets.QWidget = None) -> None:
        super().__init__(parent)

        self.init_ui()

        self.manager: ChartManager = ChartManager(self)
        self.manager.get_chart("main").add_plot("candle", get_default_settings("candle"))
        self.manager.get_chart("volume").add_plot("volume", get_default_settings("volume"))

    def init_ui(self) -> None:
        """"""
        self.setWindowTitle(_("K线图表"))

        canvas = FigureCanvas(Figure())

        # 增加高DPI支持
        canvas.figure.set_dpi(100)

        # 使用亚克力效果背景 (仅在支持的平台)
        if sys.platform == "win32":
            try:
                from win32mica import ApplyMica, MICAMODE
                ApplyMica(int(self.winId()), MICAMODE.DARK)
            except:
                pass

        # 改进图表的整体外观
        canvas.figure.subplots_adjust(
            left=0.08,
            right=0.92,
            top=0.95,
            bottom=0.15,
            hspace=0.05
        )

        # 使用更现代的配色方案
        plt.style.use("dark_background")
        canvas.figure.patch.set_facecolor("#1e1e2e")  # 设置整体背景色

        # 改进图表控件区域
        chart_toolbar = NavigationToolbar(canvas, canvas)
        chart_toolbar.setStyleSheet("""
            QToolBar {
                background-color: rgba(30, 30, 46, 180);
                border-top: 1px solid #313244;
                spacing: 5px;
            }

            QToolBar QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 2px;
                padding: 5px;
            }

            QToolBar QToolButton:hover {
                background-color: rgba(80, 80, 100, 100);
            }
        """)

        self.canvas: FigureCanvas = canvas
        self.toolbar: NavigationToolbar = chart_toolbar

        # 添加交互控件
        self.symbol_line: QtWidgets.QLineEdit = QtWidgets.QLineEdit()
        self.symbol_line.setPlaceholderText(_("输入合约代码"))
        self.symbol_line.returnPressed.connect(self.on_symbol_changed)

        self.exchange_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.exchange_combo.addItems([
            Exchange.CFFEX.value,
            Exchange.SHFE.value,
            Exchange.DCE.value,
            Exchange.CZCE.value,
            Exchange.INE.value,
            Exchange.SSE.value,
            Exchange.SZSE.value,
        ])

        self.period_combo: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.period_combo.addItems([
            Interval.MINUTE.value,
            Interval.HOUR.value,
            Interval.DAILY.value,
            Interval.WEEKLY.value,
        ])

        self.start_date_edit: QtWidgets.QDateEdit = QtWidgets.QDateEdit()
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(
            QtCore.QDate.currentDate().addMonths(-1)
        )

        self.end_date_edit: QtWidgets.QDateEdit = QtWidgets.QDateEdit()
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QtCore.QDate.currentDate())

        self.load_button: QtWidgets.QPushButton = QtWidgets.QPushButton(_("加载"))
        self.load_button.setFixedWidth(100)
        self.load_button.clicked.connect(self.on_load)

        self.refresh_button: QtWidgets.QPushButton = QtWidgets.QPushButton(_("刷新"))
        self.refresh_button.setFixedWidth(100)
        self.refresh_button.clicked.connect(self.on_refresh)

        # 美化控件样式
        self.symbol_line.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #313244;
                background-color: #1e1e2e;
            }
            QLineEdit:focus {
                border: 1px solid #585b70;
            }
        """)

        combox_style = """
            QComboBox {
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #313244;
                background-color: #1e1e2e;
            }
            QComboBox::drop-down {
                width: 20px;
                border: none;
            }
            QComboBox::down-arrow {
                width: 8px;
                height: 8px;
                background: #585b70;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                selection-background-color: #585b70;
            }
        """

        self.exchange_combo.setStyleSheet(combox_style)
        self.period_combo.setStyleSheet(combox_style)

        date_style = """
            QDateEdit {
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #313244;
                background-color: #1e1e2e;
            }
            QDateEdit::drop-down {
                width: 20px;
                border: none;
            }
            QDateEdit::down-arrow {
                width: 8px;
                height: 8px;
                background: #585b70;
            }
            QCalendarWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QCalendarWidget QToolButton {
                color: #cdd6f4;
                background-color: #313244;
                border: 1px solid #585b70;
            }
            QCalendarWidget QMenu {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QCalendarWidget QSpinBox {
                background-color: #1e1e2e;
                color: #cdd6f4;
                selection-background-color: #313244;
            }
        """

        self.start_date_edit.setStyleSheet(date_style)
        self.end_date_edit.setStyleSheet(date_style)

        button_style = """
            QPushButton {
                padding: 5px 10px;
                border-radius: 3px;
                background-color: #45475a;
                color: #cdd6f4;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #585b70;
            }
            QPushButton:pressed {
                background-color: #313244;
            }
        """

        self.load_button.setStyleSheet(button_style)
        self.refresh_button.setStyleSheet(button_style)

        # 创建表单布局
        form = QtWidgets.QFormLayout()
        form.addRow(_("合约代码"), self.symbol_line)
        form.addRow(_("交易所"), self.exchange_combo)
        form.addRow(_("周期"), self.period_combo)
        form.addRow(_("开始时间"), self.start_date_edit)
        form.addRow(_("结束时间"), self.end_date_edit)

        # 创建按钮布局
        button_hbox = QtWidgets.QHBoxLayout()
        button_hbox.addWidget(self.load_button)
        button_hbox.addWidget(self.refresh_button)
        button_hbox.addStretch()

        # 创建参数栏布局
        control_hbox = QtWidgets.QHBoxLayout()

        # 左侧参数表单
        form_widget = QtWidgets.QWidget()
        form_widget.setLayout(form)
        form_widget.setFixedWidth(240)
        control_hbox.addWidget(form_widget)

        # 右侧按钮区域
        button_widget = QtWidgets.QWidget()
        button_widget.setLayout(button_hbox)
        control_hbox.addWidget(button_widget)

        # 创建垂直主布局
        vbox = QtWidgets.QVBoxLayout()

        # 添加图表区域
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.toolbar)

        # 添加控制区域
        control_widget = QtWidgets.QWidget()
        control_widget.setLayout(control_hbox)
        control_widget.setStyleSheet("""
            background-color: #181825;
            border-top: 1px solid #313244;
        """)
        vbox.addWidget(control_widget)

        self.setLayout(vbox)

    def _get_new_x_axis(self) -> DatetimeAxis:
        return DatetimeAxis(self._manager, orientation="bottom")

    def add_cursor(self) -> None:
        """"""
        if not self._cursor:
            self._cursor = ChartCursor(
                self, self._manager, self._plots, self._item_plot_map)

    def add_plot(
        self,
        plot_name: str,
        minimum_height: int = 80,
        maximum_height: int | None = None,
        hide_x_axis: bool = False
    ) -> None:
        """
        Add plot area.
        """
        # Create plot object
        plot: pg.PlotItem = pg.PlotItem(axisItems={"bottom": self._get_new_x_axis()})
        plot.setMenuEnabled(False)
        plot.setClipToView(True)
        plot.hideAxis("left")
        plot.showAxis("right")
        plot.setDownsampling(mode="peak")
        plot.setRange(xRange=(0, 1), yRange=(0, 1))
        plot.hideButtons()
        plot.setMinimumHeight(minimum_height)

        if maximum_height:
            plot.setMaximumHeight(maximum_height)

        if hide_x_axis:
            plot.hideAxis("bottom")

        if not self._first_plot:
            self._first_plot = plot

        # Connect view change signal to update y range function
        view: pg.ViewBox = plot.getViewBox()
        view.sigXRangeChanged.connect(self._update_y_range)
        view.setMouseEnabled(x=True, y=False)

        # Set right axis
        right_axis: pg.AxisItem = plot.getAxis("right")
        right_axis.setWidth(60)
        right_axis.tickFont = NORMAL_FONT

        # Connect x-axis link
        if self._plots:
            first_plot: pg.PlotItem = list(self._plots.values())[0]
            plot.setXLink(first_plot)

        # Store plot object in dict
        self._plots[plot_name] = plot

        # Add plot onto the layout
        self._layout.nextRow()
        self._layout.addItem(plot)

    def add_item(
        self,
        item_class: type[ChartItem],
        item_name: str,
        plot_name: str
    ) -> None:
        """
        Add chart item.
        """
        item: ChartItem = item_class(self._manager)
        self._items[item_name] = item

        plot: pg.PlotItem = self._plots.get(plot_name)
        plot.addItem(item)

        self._item_plot_map[item] = plot

    def get_plot(self, plot_name: str) -> pg.PlotItem:
        """
        Get specific plot with its name.
        """
        return self._plots.get(plot_name, None)

    def get_all_plots(self) -> list[pg.PlotItem]:
        """
        Get all plot objects.
        """
        return list(self._plots.values())

    def clear_all(self) -> None:
        """
        Clear all data.
        """
        self._manager.clear_all()

        for item in self._items.values():
            item.clear_all()

        if self._cursor:
            self._cursor.clear_all()

    def update_history(self, history: list[BarData]) -> None:
        """
        Update a list of bar data.
        """
        self._manager.update_history(history)

        for item in self._items.values():
            item.update_history(history)

        self._update_plot_limits()

        self.move_to_right()

    def update_bar(self, bar: BarData) -> None:
        """
        Update single bar data.
        """
        self._manager.update_bar(bar)

        for item in self._items.values():
            item.update_bar(bar)

        self._update_plot_limits()

        if self._right_ix >= (self._manager.get_count() - self._bar_count / 2):
            self.move_to_right()

    def _update_plot_limits(self) -> None:
        """
        Update the limit of plots.
        """
        for item, plot in self._item_plot_map.items():
            min_value, max_value = item.get_y_range()

            plot.setLimits(
                xMin=-1,
                xMax=self._manager.get_count(),
                yMin=min_value,
                yMax=max_value
            )

    def _update_x_range(self) -> None:
        """
        Update the x-axis range of plots.
        """
        max_ix: int = self._right_ix
        min_ix: int = self._right_ix - self._bar_count

        for plot in self._plots.values():
            plot.setRange(xRange=(min_ix, max_ix), padding=0)

    def _update_y_range(self) -> None:
        """
        Update the y-axis range of plots.
        """
        if not self._first_plot:
            return

        view: pg.ViewBox = self._first_plot.getViewBox()
        view_range: list = view.viewRange()

        min_ix: int = max(0, int(view_range[0][0]))
        max_ix: int = min(self._manager.get_count(), int(view_range[0][1]))

        # Update limit for y-axis
        for item, plot in self._item_plot_map.items():
            y_range: tuple = item.get_y_range(min_ix, max_ix)
            plot.setRange(yRange=y_range)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """
        Reimplement this method of parent to update current max_ix value.
        """
        if not self._first_plot:
            return

        view: pg.ViewBox = self._first_plot.getViewBox()
        view_range: list = view.viewRange()
        self._right_ix = max(0, view_range[0][1])

        super().paintEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """
        Reimplement this method of parent to move chart horizontally and zoom in/out.
        """
        Key = QtCore.Qt.Key

        if event.key() == Key.Key_Left:
            self._on_key_left()
        elif event.key() == Key.Key_Right:
            self._on_key_right()
        elif event.key() == Key.Key_Up:
            self._on_key_up()
        elif event.key() == Key.Key_Down:
            self._on_key_down()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """
        Reimplement this method of parent to zoom in/out.
        """
        delta: QtCore.QPoint = event.angleDelta()

        if delta.y() > 0:
            self._on_key_up()
        elif delta.y() < 0:
            self._on_key_down()

    def _on_key_left(self) -> None:
        """
        Move chart to left.
        """
        self._right_ix -= 1
        self._right_ix = max(self._right_ix, self._bar_count)

        self._update_x_range()

        if self._cursor:
            self._cursor.move_left()
            self._cursor.update_info()

    def _on_key_right(self) -> None:
        """
        Move chart to right.
        """
        self._right_ix += 1
        self._right_ix = min(self._right_ix, self._manager.get_count())

        self._update_x_range()

        if self._cursor:
            self._cursor.move_right()
            self._cursor.update_info()

    def _on_key_down(self) -> None:
        """
        Zoom out the chart.
        """
        self._bar_count = int(self._bar_count * 1.2)
        self._bar_count = min(int(self._bar_count), self._manager.get_count())

        self._update_x_range()

        if self._cursor:
            self._cursor.update_info()

    def _on_key_up(self) -> None:
        """
        Zoom in the chart.
        """
        self._bar_count = int(self._bar_count / 1.2)
        self._bar_count = max(int(self._bar_count), self.MIN_BAR_COUNT)

        self._update_x_range()

        if self._cursor:
            self._cursor.update_info()

    def move_to_right(self) -> None:
        """
        Move chart to the most right.
        """
        self._right_ix = self._manager.get_count()
        self._update_x_range()

        if self._cursor:
            self._cursor.update_info()

    def refresh(self, data: List[ObjectDict]) -> None:
        """
        Update chart data.
        """
        self.updated = True
        self.manager.set_data(data)

        # 更新窗口标题显示更多信息
        symbol = self.symbol_line.text()
        exchange = self.exchange_combo.currentText()
        interval = self.period_combo.currentText()
        last_bar = data[-1] if data else None

        title = f"{symbol} - {exchange} - {interval}"
        if last_bar:
            # 添加最新价格信息到标题
            close_price = last_bar.get("close_price", "")
            open_price = last_bar.get("open_price", "")

            if close_price and open_price:
                change = close_price - open_price
                change_pct = change / open_price * 100 if open_price else 0

                # 根据涨跌设置不同颜色
                if change > 0:
                    title += f" | 价格: <font color='#a6e3a1'>{close_price:.2f}</font>"
                    title += f" | 涨跌: <font color='#a6e3a1'>+{change:.2f} (+{change_pct:.2f}%)</font>"
                elif change < 0:
                    title += f" | 价格: <font color='#f38ba8'>{close_price:.2f}</font>"
                    title += f" | 涨跌: <font color='#f38ba8'>{change:.2f} ({change_pct:.2f}%)</font>"
                else:
                    title += f" | 价格: {close_price:.2f} | 涨跌: 0.00 (0.00%)"

        self.setWindowTitle(title)


class ChartCursor(QtCore.QObject):
    """"""

    def __init__(
        self,
        widget: ChartWidget,
        manager: BarManager,
        plots: dict[str, pg.GraphicsObject],
        item_plot_map: dict[ChartItem, pg.GraphicsObject]
    ) -> None:
        """"""
        super().__init__()

        self._widget: ChartWidget = widget
        self._manager: BarManager = manager
        self._plots: dict[str, pg.GraphicsObject] = plots
        self._item_plot_map: dict[ChartItem, pg.GraphicsObject] = item_plot_map

        self._x: int = 0
        self._y: float = 0
        self._plot_name: str = ""

        self._init_ui()
        self._connect_signal()

    def _init_ui(self) -> None:
        """"""
        self._init_line()
        self._init_label()
        self._init_info()

    def _init_line(self) -> None:
        """
        Create line objects.
        """
        self._v_lines: dict[str, pg.InfiniteLine] = {}
        self._h_lines: dict[str, pg.InfiniteLine] = {}
        self._views: dict[str, pg.ViewBox] = {}

        pen: QtGui.QPen = pg.mkPen(WHITE_COLOR)

        for plot_name, plot in self._plots.items():
            v_line: pg.InfiniteLine = pg.InfiniteLine(angle=90, movable=False, pen=pen)
            h_line: pg.InfiniteLine = pg.InfiniteLine(angle=0, movable=False, pen=pen)
            view: pg.ViewBox = plot.getViewBox()

            for line in [v_line, h_line]:
                line.setZValue(0)
                line.hide()
                view.addItem(line)

            self._v_lines[plot_name] = v_line
            self._h_lines[plot_name] = h_line
            self._views[plot_name] = view

    def _init_label(self) -> None:
        """
        Create label objects on axis.
        """
        self._y_labels: dict[str, pg.TextItem] = {}
        for plot_name, plot in self._plots.items():
            label: pg.TextItem = pg.TextItem(
                plot_name, fill=CURSOR_COLOR, color=BLACK_COLOR)
            label.hide()
            label.setZValue(2)
            label.setFont(NORMAL_FONT)
            plot.addItem(label, ignoreBounds=True)
            self._y_labels[plot_name] = label

        self._x_label: pg.TextItem = pg.TextItem(
            "datetime", fill=CURSOR_COLOR, color=BLACK_COLOR)
        self._x_label.hide()
        self._x_label.setZValue(2)
        self._x_label.setFont(NORMAL_FONT)
        plot.addItem(self._x_label, ignoreBounds=True)

    def _init_info(self) -> None:
        """
        """
        self._infos: dict[str, pg.TextItem] = {}
        for plot_name, plot in self._plots.items():
            info: pg.TextItem = pg.TextItem(
                "info",
                color=CURSOR_COLOR,
                border=CURSOR_COLOR,
                fill=BLACK_COLOR
            )
            info.hide()
            info.setZValue(2)
            info.setFont(NORMAL_FONT)
            plot.addItem(info)  # , ignoreBounds=True)
            self._infos[plot_name] = info

    def _connect_signal(self) -> None:
        """
        Connect mouse move signal to update function.
        """
        self._widget.scene().sigMouseMoved.connect(self._mouse_moved)

    def _mouse_moved(self, evt: tuple) -> None:
        """
        Callback function when mouse is moved.
        """
        if not self._manager.get_count():
            return

        # First get current mouse point
        pos: tuple = evt

        for plot_name, view in self._views.items():
            rect = view.sceneBoundingRect()

            if rect.contains(pos):
                mouse_point = view.mapSceneToView(pos)
                self._x = to_int(mouse_point.x())
                self._y = mouse_point.y()
                self._plot_name = plot_name
                break

        # Then update cursor component
        self._update_line()
        self._update_label()
        self.update_info()

    def _update_line(self) -> None:
        """"""
        for v_line in self._v_lines.values():
            v_line.setPos(self._x)
            v_line.show()

        for plot_name, h_line in self._h_lines.items():
            if plot_name == self._plot_name:
                h_line.setPos(self._y)
                h_line.show()
            else:
                h_line.hide()

    def _update_label(self) -> None:
        """"""
        bottom_plot: pg.PlotItem = list(self._plots.values())[-1]
        axis_width = bottom_plot.getAxis("right").width()
        axis_height = bottom_plot.getAxis("bottom").height()
        axis_offset: QtCore.QPointF = QtCore.QPointF(axis_width, axis_height)

        bottom_view: pg.ViewBox = list(self._views.values())[-1]
        bottom_right = bottom_view.mapSceneToView(
            bottom_view.sceneBoundingRect().bottomRight() - axis_offset
        )

        for plot_name, label in self._y_labels.items():
            if plot_name == self._plot_name:
                label.setText(str(self._y))
                label.show()
                label.setPos(bottom_right.x(), self._y)
            else:
                label.hide()

        dt: datetime | None = self._manager.get_datetime(self._x)
        if dt:
            self._x_label.setText(dt.strftime("%Y-%m-%d %H:%M:%S"))
            self._x_label.show()
            self._x_label.setPos(self._x, bottom_right.y())
            self._x_label.setAnchor((0, 0))

    def update_info(self) -> None:
        """"""
        buf: dict = {}

        for item, plot in self._item_plot_map.items():
            item_info_text: str = item.get_info_text(self._x)

            if plot not in buf:
                buf[plot] = item_info_text
            else:
                if item_info_text:
                    buf[plot] += ("\n\n" + item_info_text)

        for plot_name, plot in self._plots.items():
            plot_info_text: str = buf[plot]
            info: pg.TextItem = self._infos[plot_name]
            info.setText(plot_info_text)
            info.show()

            view: pg.ViewBox = self._views[plot_name]
            top_left = view.mapSceneToView(view.sceneBoundingRect().topLeft())
            info.setPos(top_left)

    def move_right(self) -> None:
        """
        Move cursor index to right by 1.
        """
        if self._x == self._manager.get_count() - 1:
            return
        self._x += 1

        self._update_after_move()

    def move_left(self) -> None:
        """
        Move cursor index to left by 1.
        """
        if self._x == 0:
            return
        self._x -= 1

        self._update_after_move()

    def _update_after_move(self) -> None:
        """
        Update cursor after moved by left/right.
        """
        bar: BarData | None = self._manager.get_bar(self._x)
        if bar is None:
            return

        self._y = bar.close_price

        self._update_line()
        self._update_label()

    def clear_all(self) -> None:
        """
        Clear all data.
        """
        self._x = 0
        self._y = 0
        self._plot_name = ""

        for line in list(self._v_lines.values()) + list(self._h_lines.values()):
            line.hide()

        for label in list(self._y_labels.values()) + [self._x_label]:
            label.hide()
