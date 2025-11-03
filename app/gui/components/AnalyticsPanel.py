import os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QListWidget, QListWidgetItem, QApplication
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QFont, QColor, QPainter, QBrush, QPen, QPainterPath, QRegion
)
from PyQt6.QtCore import Qt, QDateTime, QTimer, QRectF
from PyQt6.QtCharts import (
    QChart, QChartView, QBarSeries, QBarSet, QLineSeries,
    QValueAxis, QBarCategoryAxis, QDateTimeAxis,
    QAbstractAxis
)

from gui.components.KanjiCard import KanjiCard

from utils.paths import BOOK_OPEN_ICON, TARGET_ICON, TRENDING_UP_ICON

PRIMARY_COLOR = QColor("#C24338") 
BG_COLOR_DARK = QColor("#2c2c2c")
BORDER_COLOR = QColor("#333333")
TEXT_COLOR_NORMAL = QColor("#FFFFFF")
TEXT_COLOR_MUTED = QColor("#AAAAAA")
TEXT_COLOR_HEADER = QColor("#FFFFFF")
GRID_LINE_COLOR = QColor("#2A2A35")

class BaseCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("baseCard")
        # Basic styling, can be overridden or extended
        self.setStyleSheet(f"""
            QFrame#baseCard {{
                background-color: {BG_COLOR_DARK.name()};
                border-radius: 12px;
                border: 1px solid {BORDER_COLOR.name()};
                padding: 10px;
            }}
        """)
        
def get_icon(path, size=24):
    if os.path.exists(path):
        pixmap = QPixmap(str(path)).scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        return QIcon(pixmap)
    return None

# --- Summary Card Widget ---
class SummaryCard(BaseCard):
    def __init__(self, icon_path, title, value, subtitle, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 10, 10, 10)

        # Icon and Title Row
        title_row_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {TEXT_COLOR_MUTED.name()}; font-size: 11px;")
        
        icon = get_icon(icon_path, 20)
        icon_label = QLabel()
        if icon:
            icon_label.setPixmap(icon.pixmap(20, 20))

        icon_label.setStyleSheet(f"color: {PRIMARY_COLOR.name()};")
        
        title_row_layout.addWidget(icon_label)
        title_row_layout.addWidget(title_label)
        title_row_layout.addStretch()
        layout.addLayout(title_row_layout)

        # Value
        self.value_label = QLabel(str(value))
        font = self.value_label.font()
        font.setPointSize(22)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setStyleSheet(f"color: {TEXT_COLOR_NORMAL.name()}; margin-top: 4px; margin-bottom: 0px;")
        layout.addWidget(self.value_label)

        # Subtitle
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setStyleSheet(f"color: {TEXT_COLOR_MUTED.name()}; font-size: 10px; margin-top: -2px;")
        layout.addWidget(self.subtitle_label)

    def set_value(self, value):
        self.value_label.setText(str(value))

# --- Kanji List Item Widget ---
class KanjiListItemWidget(BaseCard):
    def __init__(self, kanji, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame#baseCard {{
                background-color: {BG_COLOR_DARK.name()}; /* Slightly darker bg */
                border-radius: 8px;
                border: 1px solid {BORDER_COLOR.name()};
                padding: 8px 12px;
            }}
             QFrame#baseCard:hover {{
                background-color: {BG_COLOR_DARK.name()}; /* Lighter on hover */
             }}
        """)
        layout = QHBoxLayout(self)
        
        self._balloon = None  # Balloon widget for KanjiCard

        self._balloon_timer = None  # QTimer for delayed balloon
        
        
        self.kanji = kanji
        jlpt = self.kanji.get('jlpt')
        strokes = self.kanji.get('strokes', '-')
        count = self.kanji.get('cnt')
        
        
        # Left side: Kanji + Info
        left_layout = QHBoxLayout()
        kanji_label = QLabel(self.kanji.get('kanji'))
        font = kanji_label.font()
        font.setPointSize(18)
        font.setBold(True)
        kanji_label.setFont(font)
        kanji_label.setStyleSheet(f"color: {PRIMARY_COLOR.name()}; margin-right: 10px;")

        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)
        jlpt_text = f"JLPT: N{jlpt}" if jlpt != "None" else "JLPT: -"
        info_label1 = QLabel(jlpt_text)
        info_label1.setStyleSheet(f"color: {TEXT_COLOR_MUTED.name()}; font-size: 9px;")
        info_label2 = QLabel(f"{strokes} strokes")
        info_label2.setStyleSheet(f"color: {TEXT_COLOR_MUTED.name()}; font-size: 9px;")
        info_layout.addWidget(info_label1)
        info_layout.addWidget(info_label2)

        left_layout.addWidget(kanji_label)
        left_layout.addLayout(info_layout)
        left_layout.addStretch()

        # Right side: Count
        right_layout = QVBoxLayout()
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
        count_label = QLabel(str(count))
        font = count_label.font()
        font.setPointSize(14)
        font.setBold(True)
        count_label.setFont(font)
        count_label.setStyleSheet(f"color: {TEXT_COLOR_NORMAL.name()};")

        times_label = QLabel("times")
        times_label.setStyleSheet(f"color: {TEXT_COLOR_MUTED.name()}; font-size: 9px;")

        right_layout.addWidget(count_label)
        right_layout.addWidget(times_label)


        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        
    def enterEvent(self, event):
        self._show_balloon()

        super().enterEvent(event)

    def _show_balloon(self):
        if self._balloon is not None:
            return
        
        # Truncate long texts for balloon
        def elide(text, maxlen=32):
            if text and len(text) > maxlen:
                return text[:maxlen-3] + '...'
            return text

        card = KanjiCard(
            kanji=self.kanji.get('kanji', ''),
            kunyomi=elide(self.kanji.get('kunyomi', ''), 24),
            onyomi=elide(self.kanji.get('onyomi', ''), 24),
            meaning=elide(self.kanji.get('meaning', ''), 32),
            jlpt=None,
            strokes=None
        )
        card.setWindowFlags(Qt.WindowType.ToolTip)
        card.setFixedSize(300, 170)
        # Add a soft rounded border for the balloon only
        card.setStyleSheet(card.styleSheet() + "\nQFrame#kanjiCard { border: 2px solid #555; background-color: #2b2b2b; }")
        # Apply a rounded mask to the card (balloon) only
        
        path = QPainterPath()
        rect = QRectF(0, 0, card.width(), card.height())
        path.addRoundedRect(rect, 8, 8)
        region = QRegion(path.toFillPolygon().toPolygon())
        card.setMask(region)
        # Enable word wrap for value labels
        for child in card.findChildren(QLabel):
            if child.property("role") is None:
                child.setWordWrap(True)
        self._balloon = card
        
        # Always show left, centered vertically to KanjiList Item
        global_pos = self.mapToGlobal(self.rect().topLeft())
        center_y = global_pos.y() + (self.height() // 2) - (card.height() // 2)
        left_x = global_pos.x() - card.width() - 10  # 10px de margem
        self._balloon.move(left_x, center_y)
        self._balloon.show()

    def leaveEvent(self, event):
        # Hide and delete balloon
        if self._balloon is not None:
            self._balloon.hide()
            self._balloon.deleteLater()
            self._balloon = None

        super().leaveEvent(event)


# --- Main Analytics Panel ---
class AnalyticsPanel(QWidget):
    def __init__(self, analitycs_service, kanji_service, parent=None ):
        super().__init__(parent)
        self.analitycs_service = analitycs_service
        self.kanji_service = kanji_service
        
        self.setStyleSheet(f"background-color: {BG_COLOR_DARK.name()};")

        # Detect screen size for responsive sizing
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        
        # Responsive dimensions based on screen width
        if screen_width < 2000:
            # Smaller screens: compact layout
            self.card_min_height = 160
            self.chart_min_height = 140  # Increased to prevent Y-axis label truncation
            main_spacing = 10
            main_margins = (10, 10, 10, 10)
            self.kanji_list_max_height = 150
        else:
            # Larger screens: normal layout
            self.card_min_height = 220
            self.chart_min_height = 180
            main_spacing = 15
            main_margins = (15, 15, 15, 15)
            self.kanji_list_max_height = 200

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(main_spacing)
        main_layout.setContentsMargins(*main_margins)

        # --- Summary Cards ---
        summary_grid = QGridLayout()
        summary_grid.setSpacing(12)
        
        self.card_unique = SummaryCard(BOOK_OPEN_ICON, "Unique", "—", "kanji")
        self.card_total = SummaryCard(TRENDING_UP_ICON, "Total", "—", "occurrences")
        self.card_avg = SummaryCard(TARGET_ICON, "Avg", "—", "Jltp")
        
        summary_grid.addWidget(self.card_unique, 0, 0)
        summary_grid.addWidget(self.card_total, 0, 1)
        summary_grid.addWidget(self.card_avg, 0, 2)
        main_layout.addLayout(summary_grid)
        
        
        # --- Top Kanji List ---
        kanji_list_card = self._create_chart_card("Most Captured Kanji", None)
        self.top_kanji_list_widget = QListWidget()
        # Styling List Widget
        self.top_kanji_list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                padding-right: 5px; /* Space for scrollbar */
            }}
            QListWidget::item {{
                border: none;
                margin-bottom: 6px;
                border-radius: 0px; /* Override any inherited radius */
            }}
            /* Scrollbar Styling */
            QScrollBar:vertical {{
                border: none;
                background: {BG_COLOR_DARK.name()};
                width: 8px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER_COLOR.darker(110).name()};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
             QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        self.top_kanji_list_widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.top_kanji_list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.top_kanji_list_widget.setMaximumHeight(self.kanji_list_max_height) # Limit height further
        kanji_list_card.layout().addWidget(self.top_kanji_list_widget)
        main_layout.addWidget(kanji_list_card)
        
        # --- Charts ---
        self.jlpt_chart = QChart()
        self.jlpt_chart_view = QChartView(self.jlpt_chart)
        jlpt_card = self._create_chart_card("JLPT Distribution", self.jlpt_chart_view)
        main_layout.addWidget(jlpt_card)

        self.media_chart = QChart()
        self.media_chart_view = QChartView(self.media_chart)
        media_card = self._create_chart_card("Top Media Sources", self.media_chart_view)
        main_layout.addWidget(media_card)

        self.trend_chart = QChart()
        self.trend_chart_view = QChartView(self.trend_chart)
        trend_card = self._create_chart_card("Capture Trends", self.trend_chart_view)
        main_layout.addWidget(trend_card)

        

        main_layout.addStretch()
        self.refresh_analytics()

    def _create_chart_card(self, title, chart_view_widget):
        card = BaseCard()
        card.setMinimumHeight(self.card_min_height)  # Ensures card and chart have enough height for axis labels
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 8, 12, 12)
        title_label = QLabel(title)
        font = title_label.font()
        font.setPointSize(10)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setStyleSheet(f"color: {TEXT_COLOR_HEADER.name()}; margin-bottom: 5px;")
        layout.addWidget(title_label)
        if chart_view_widget:
            chart_view_widget.setRenderHint(QPainter.RenderHint.Antialiasing)
            chart_view_widget.setMinimumHeight(self.chart_min_height)  # Slightly larger for chart area
            layout.addWidget(chart_view_widget)
        return card

    def _apply_dark_chart_theme(self, chart: QChart, axis_x: QAbstractAxis, axis_y: QAbstractAxis):
        chart.setBackgroundBrush(QBrush(BG_COLOR_DARK))
        chart.legend().hide()

        axis_pen = QPen(BORDER_COLOR)
        grid_pen = QPen(GRID_LINE_COLOR)
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        label_brush = QBrush(TEXT_COLOR_MUTED)

        axis_x.setLabelsBrush(label_brush)
        axis_x.setLinePen(axis_pen)
        axis_x.setGridLinePen(grid_pen)
        axis_x.setLabelsFont(QFont("Arial", 8)) # Smaller font for axes

        axis_y.setLabelsBrush(label_brush)
        axis_y.setLinePen(axis_pen)
        axis_y.setGridLinePen(grid_pen)
        axis_y.setLabelsFont(QFont("Arial", 8))

    def refresh_analytics(self):
        # --- Get real data from repositories ---
        kanji_rows = self.kanji_service.get_all_user_kanji_with_count(order='COUNT')
        total_kanjis = len([r for r in kanji_rows if r.get('cnt', 0) > 0])
        total_occurrences = sum(r.get('cnt', 0) for r in kanji_rows)
        avg_strokes = np.mean([r.get('strokes',0) for r in kanji_rows if r.get('strokes')]) if kanji_rows else 0
        avg_JLPT = np.mean([r.get('jlpt',0) for r in kanji_rows if r.get('jlpt')]) if kanji_rows else 0
        avg_grade = np.mean([r.get('grade',0) for r in kanji_rows if r.get('grade')]) if kanji_rows else 0

        self.card_unique.set_value(total_kanjis)
        self.card_total.set_value(total_occurrences)
        self.card_avg.set_value(f"{avg_JLPT:.0f}")

        # --- JLPT Chart ---
        jlpt_counts = {}
        for r in kanji_rows:
            jlpt = r.get('jlpt')
            if jlpt:
                key = f"N{jlpt}"
                jlpt_counts[key] = jlpt_counts.get(key, 0) + 1
        categories = sorted(jlpt_counts.keys())
        max_jlpt_count = max(jlpt_counts.values()) if jlpt_counts else 0
        jlpt_set = QBarSet("JLPT")
        for cat in categories:
            jlpt_set.append(jlpt_counts[cat])
        jlpt_set.setColor(PRIMARY_COLOR)
        jlpt_series = QBarSeries()
        jlpt_series.append(jlpt_set)

        

        self.jlpt_chart.removeAllSeries()
        for axis in self.jlpt_chart.axes():
            self.jlpt_chart.removeAxis(axis)
        self.jlpt_chart.addSeries(jlpt_series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self.jlpt_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        jlpt_series.attachAxis(axis_x)
        axis_y = QValueAxis()
        axis_y.setRange(0, max_jlpt_count + 1)
        axis_y.setTickCount(min(max_jlpt_count + 2, 6))
        axis_y.setLabelFormat("%d")  # Show only integer values
        self.jlpt_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        jlpt_series.attachAxis(axis_y)
        self._apply_dark_chart_theme(self.jlpt_chart, axis_x, axis_y)
        self.jlpt_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # --- Media Chart ---
        media_counts = self.analitycs_service.count_by_media()
        media_categories = []
        media_values = []
        max_media_count = 0
        for m in media_counts:
            media_categories.append(m['media'] if m['media'] else 'N/A')
            media_values.append(m['count'])
            if m['count'] > max_media_count:
                max_media_count = m['count']
        media_series = QBarSeries()
        media_set = QBarSet("Media Counts")
        for v in media_values:
            media_set.append(v)
        media_set.setColor(PRIMARY_COLOR)
        media_series.append(media_set)
        media_series.setBarWidth(0.6)
        self.media_chart.removeAllSeries()
        for axis in self.media_chart.axes():
            self.media_chart.removeAxis(axis)
        self.media_chart.addSeries(media_series)
        media_axis_x = QBarCategoryAxis()
        media_axis_x.append(media_categories)
        self.media_chart.addAxis(media_axis_x, Qt.AlignmentFlag.AlignBottom)
        media_series.attachAxis(media_axis_x)
        media_axis_y = QValueAxis()
        media_axis_y.setRange(0, max_media_count + 1)
        media_axis_y.setTickCount(min(max_media_count + 2, 6))
        media_axis_y.setLabelFormat("%d")  # Show only integer values
        self.media_chart.addAxis(media_axis_y, Qt.AlignmentFlag.AlignLeft)
        media_series.attachAxis(media_axis_y)
        self._apply_dark_chart_theme(self.media_chart, media_axis_x, media_axis_y)
        self.media_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # --- Trend Chart ---
        captures = self.analitycs_service.get_captures_with_dates()
        from collections import Counter
        dates = [c['date'][:7] for c in captures if 'date' in c]  # YYYY-MM
        date_counts = Counter(dates)
        sorted_dates = sorted(date_counts.keys())
        max_captures = max(date_counts.values()) if date_counts else 0
        trend_series = QLineSeries()
        min_date, max_date = QDateTime(), QDateTime()
        first_point = True
        for d in sorted_dates:
            dt = QDateTime.fromString(d, "yyyy-MM")
            trend_series.append(dt.toMSecsSinceEpoch(), date_counts[d])
            if first_point or dt < min_date: min_date = dt
            if first_point or dt > max_date: max_date = dt
            first_point = False
        pen = QPen(PRIMARY_COLOR)
        pen.setWidth(2)
        trend_series.setPen(pen)
        trend_series.setPointsVisible(True)
        trend_series.setMarkerSize(7)
        trend_series.setColor(PRIMARY_COLOR)
        self.trend_chart.removeAllSeries()
        for axis in self.trend_chart.axes():
            self.trend_chart.removeAxis(axis)
        self.trend_chart.addSeries(trend_series)
        axis_x = QDateTimeAxis()
        axis_x.setFormat("yyyy-MM")
        if min_date.isValid() and max_date.isValid():
            axis_x.setMin(min_date)
            axis_x.setMax(max_date)
        axis_x.setTickCount(min(len(sorted_dates), 7))
        self.trend_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        trend_series.attachAxis(axis_x)
        axis_y = QValueAxis()
        axis_y.setRange(0, max_captures + 1)
        axis_y.setTickCount(min(max_captures + 2, 6))
        axis_y.setLabelFormat("%d")  # Show only integer values
        self.trend_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        trend_series.attachAxis(axis_y)
        self._apply_dark_chart_theme(self.trend_chart, axis_x, axis_y)
        self.trend_chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        # --- Top Kanji List ---
        self.top_kanji_list_widget.clear()
        for r in kanji_rows[:10]:
            list_item_widget = KanjiListItemWidget(
                r
            )
            list_item = QListWidgetItem()
            list_item.setSizeHint(list_item_widget.sizeHint())
            self.top_kanji_list_widget.addItem(list_item)
            self.top_kanji_list_widget.setItemWidget(list_item, list_item_widget)