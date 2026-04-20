import os

from qtpy.QtGui import QIcon
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.plugin_registration.decorators import on_plugin_available

from .widgets import AutoJudgeWidget


class AutoJudgePlugin(SpyderDockablePlugin):
    """A Spyder dockable pane that auto-tests Python files on save."""

    NAME = "spyder_autojudge"
    REQUIRES = []
    OPTIONAL = [Plugins.Projects]
    TABIFY = [Plugins.Help]
    WIDGET_CLASS = AutoJudgeWidget
    CONF_SECTION = NAME
    CONF_FILE = False

    @staticmethod
    def get_name():
        return "AutoJudge"

    @staticmethod
    def get_description():
        return "Run input/expected test cases whenever Python files change."

    @classmethod
    def get_icon(cls):
        return QIcon()

    def on_initialize(self):
        self.get_widget().set_working_directory(self._get_default_working_directory())

    @on_plugin_available(plugin=Plugins.Projects)
    def on_projects_available(self):
        self.get_widget().set_working_directory(self._get_default_working_directory())

    def _get_default_working_directory(self):
        projects = self.get_plugin(Plugins.Projects)
        if projects:
            project_path = projects.get_active_project_path()
            if project_path:
                return project_path

        return os.getcwd()
