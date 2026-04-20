import os

from qtpy.QtCore import Qt
from qtpy.QtGui import QFontDatabase
from qtpy.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QStyle,
    QTextEdit,
    QVBoxLayout,
)
from spyder.api.widgets.main_widget import PluginMainWidget
from spyder.api.widgets.menus import OptionsMenuSections

from .test_runner import TestRunner

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except Exception:
    FigureCanvas = None
    Figure = None
    MATPLOTLIB_AVAILABLE = False


class AutoJudgeWidget(PluginMainWidget):
    """Dockable UI for running and visualizing test results."""

    def __init__(self, name, plugin, parent=None):
        super().__init__(name, plugin, parent=parent)
        self.runner = None
        self._working_dir = self._get_initial_working_directory(plugin)
        self._build_ui()
        self._reset_runner()
        self._setup_options_menu()

    def _get_initial_working_directory(self, plugin):
        getter = getattr(plugin, "_get_default_working_directory", None)
        if callable(getter):
            folder = getter()
            if folder and os.path.isdir(folder):
                return os.fspath(folder)
        return os.getcwd()

    def setup(self):
        """Required by Spyder's PluginMainWidget API."""

    def get_title(self):
        """Return the title displayed on the dockwidget."""
        return "AutoJudge"

    def get_focus_widget(self):
        """Give keyboard focus to the output pane when switching to plugin."""
        return self.output

    def update_actions(self):
        """No custom actions for now."""

    def set_working_directory(self, folder):
        if folder and os.path.isdir(folder):
            self._working_dir = folder
            self.folder_edit.setText(folder)
            if self.runner is not None:
                self.runner.set_watch_dir(folder)

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        controls_row = QHBoxLayout()
        controls_row.addWidget(QLabel("Folder Directory:"))

        self.folder_edit = QLineEdit(self._working_dir)
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setMinimumWidth(80)
        controls_row.addWidget(self.folder_edit, 1)

        self.run_button = QPushButton("Run Latest")
        self.run_button.setMinimumHeight(28)
        self.run_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.run_button.clicked.connect(self._on_run_clicked)
        controls_row.addWidget(self.run_button)

        layout.addLayout(controls_row)
        self.setLayout(layout)

        summary_row = QHBoxLayout()
        self.summary_label = QLabel("Summary: total=0, success=0, wrong=0, error=0")
        self.summary_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.summary_label.setMinimumHeight(24)
        summary_row.addWidget(self.summary_label)
        layout.addLayout(summary_row)

        splitter = QSplitter(Qt.Vertical, self)
        splitter.setChildrenCollapsible(False)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QTextEdit.NoWrap)
        self.output.setPlaceholderText("Click 'Run Latest' to test the newest modified Python file...")
        self.output.setMinimumHeight(140)
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        self.output.setFont(fixed_font)
        splitter.addWidget(self.output)

        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(5, 3), tight_layout=True)
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setMinimumHeight(120)
            splitter.addWidget(self.canvas)
        else:
            self.figure = None
            self.canvas = None
            fallback = QLabel("Install matplotlib in Spyder's Python env to enable the pie chart.")
            fallback.setWordWrap(True)
            fallback.setAlignment(Qt.AlignCenter)
            fallback.setMinimumHeight(100)
            splitter.addWidget(fallback)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([300, 180])
        layout.addWidget(splitter, 1)

        self._draw_pie(0, 0, 0)

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder", self._working_dir)
        if folder:
            self.set_working_directory(folder)
            self._append_log(f"📁 Working folder set to: {folder}")

    def _on_run_clicked(self):
        folder = self._working_dir
        if not os.path.isdir(folder):
            self._append_log("⚠️ Invalid folder selected.")
            return

        self._append_log("")
        self.runner.run_latest_file()

    def _on_status(self, status):
        if status == "running":
            self.run_button.setEnabled(False)
            return

        self.run_button.setEnabled(True)

    def _setup_options_menu(self):
        options_menu = self.get_options_menu()
        options_menu.setMinimumWidth(180)

        browse_action = self.create_action(
            "browse_folder_action",
            text="Browse Folder",
            triggered=self._on_browse,
            icon=None,
            register_action=False,
        )
        clear_action = self.create_action(
            "clear_log_action",
            text="Clear Logs",
            triggered=self._clear_output,
            icon=None,
            register_action=False,
        )

        self.add_item_to_menu(
            browse_action,
            menu=options_menu,
            section=OptionsMenuSections.Top,
        )
        self.add_item_to_menu(
            clear_action,
            menu=options_menu,
            section=OptionsMenuSections.Top,
        )

    def _on_summary(self, summary):
        total = summary.get("total", 0)
        success = summary.get("success", 0)
        wrong = summary.get("wrong", 0)
        error = summary.get("error", 0)
        file_name = summary.get("file", "")

        if file_name:
            self._append_log(f"✅ Completed run for: {file_name}")

        self.summary_label.setText(
            f"Summary: total={total}, success={success}, wrong={wrong}, error={error}"
        )
        self._draw_pie(success, wrong, error)

    def _draw_pie(self, success, wrong, error):
        if not MATPLOTLIB_AVAILABLE or self.figure is None or self.canvas is None:
            return

        labels = ["Success", "Wrong", "Error"]
        sizes = [success, wrong, error]
        colors = ["#4CAF50", "#FF9800", "#F44336"]

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        total = sum(sizes)
        if total == 0:
            ax.text(0.5, 0.5, "No test data yet", ha="center", va="center", fontsize=12)
            ax.set_axis_off()
            self.canvas.draw_idle()
            return

        display_labels = []
        for label, count in zip(labels, sizes):
            display_labels.append(f"{label} ({count})" if count > 0 else "")

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=display_labels,
            colors=colors,
            startangle=140,
            autopct=lambda p: f"{p:.1f}%" if p > 0 else "",
            pctdistance=0.72,
            labeldistance=1.05,
            textprops={"fontsize": 10},
        )

        for text in texts:
            text.set_fontsize(10)
        for auto in autotexts:
            auto.set_fontsize(10)
            auto.set_weight("bold")

        ax.set_title("Test Case Results", fontsize=12, weight="bold")
        ax.axis("equal")
        self.canvas.draw_idle()

    def _append_log(self, text):
        if text == "":
            self.output.append("")
            return

        self.output.append(text)

    def _clear_output(self):
        self.output.clear()

    def _reset_runner(self):
        self.runner = TestRunner(watch_dir=self._working_dir)
        self.runner.sig_log.connect(self._append_log)
        self.runner.sig_summary.connect(self._on_summary)
        self.runner.sig_status.connect(self._on_status)

    def closeEvent(self, event):
        super().closeEvent(event)
