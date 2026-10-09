"""
Custom tab widget for ToriiKanji.
Implements a custom tab bar with a stacked widget for panel switching.
"""

from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from gui.CollectionPanel import CollectionPanel
from gui.components.AnalyticsPanel import AnalyticsPanel
from gui.OverlayPanel import OverlayPanel
from gui.SettingsPanel import SettingsPanel
from gui.theme import tab_button_style


class CustomTabWidget(QWidget):
    def __init__(self, main_window, capture_service, media_service, kanji_service, analytics_service):
        super().__init__()
        self.main_window = main_window
        self.capture_service = capture_service
        self.media_service = media_service
        self.kanji_service = kanji_service
        self.analytics_service = analytics_service

        layout = QVBoxLayout(self)

        # Create panels
        self.overlay_panel = OverlayPanel(self.main_window)
        self.settings_panel = SettingsPanel(self.main_window)
        self.collection_panel = CollectionPanel(
            self.main_window, self.capture_service,
            self.media_service, self.kanji_service
        )
        self.analytics_panel = AnalyticsPanel(
            self.analytics_service, self.kanji_service, parent=self.main_window
        )

        # Connect settings save to overlay UI refresh
        self.settings_panel.settings_saved.connect(self.overlay_panel.update_ui_from_settings)

        # Tab bar
        self.tab_bar = QHBoxLayout()
        self.tab_bar.setContentsMargins(0, 0, 0, 0)
        self.tab_bar.setSpacing(0)
        layout.addLayout(self.tab_bar)

        # Stacked widget for panel switching
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Add tabs
        self.add_tab("Capture", self.overlay_panel)
        self.add_tab("Collections", self.collection_panel)
        self.add_tab("Analytics", self.analytics_panel)
        self.add_tab("Settings", self.settings_panel)

        self.show_tab(0)

    def show_capture(self, result):
        """Show a capture result in the overlay panel."""
        self.overlay_panel.show_capture(result)

    def add_tab(self, title, widget):
        """Add a new tab with the given title and widget."""
        index = self.stack.addWidget(widget)

        button = QPushButton(title)
        button.setStyleSheet(tab_button_style())
        button.setCheckable(True)
        button.clicked.connect(lambda: self.show_tab(index))

        self.tab_bar.addWidget(button)

    def show_tab(self, index):
        """Switch to the specified tab index."""
        self.stack.setCurrentIndex(index)

        # Refresh analytics when its tab is shown
        if index == 2:
            self.analytics_panel.refresh_analytics()

        # Update button checked states
        for i in range(self.tab_bar.count()):
            btn = self.tab_bar.itemAt(i).widget()
            btn.setChecked(i == index)
