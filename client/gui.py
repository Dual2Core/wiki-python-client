import logging
import os
import subprocess
import sys

from PyQt5.Qt import QSize
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QWidget

import client.gui_conf as gc
import utils
from client.client import DWClient

LOG = logging.getLogger('gui')


def create_file_if_not_exists(path):
    open(path, 'a').close()


def get_prefix_path():
    if os.name == 'nt':
        prefix_path = os.getenv("APPDATA")
        path = os.path.join(prefix_path, "DistributedWiki")
    else:
        username = os.getenv("USER")
        path = os.path.join("/home", username, ".DistributedWiki")

    if not os.path.exists(path):
        os.makedirs(path)

    return path


class GUI(QWidget):
    """
    GUI for Distributed Wikipedia Client
    """
    def __init__(self):
        super().__init__()

        self.resize(gc.FRAME_WIDTH, gc.FRAME_HEIGHT)
        self.move(
            gc.FHD_W/2 - gc.FRAME_WIDTH/2, gc.FHD_H/2 - gc.FRAME_HEIGHT/2
        )
        self.setWindowTitle(gc.WINDOW_TITLE)

        self._constructUI()
        self.client = DWClient()

        os.chdir(get_prefix_path())

    def _constructUI(self):
        status_title = QLabel("FullNode:", self)
        status_title.move(50, 25)

        status_variable = QLabel("active", self)
        status_variable.setStyleSheet("QLabel {color: green;}")
        status_variable.move(100, 25)

        self.title_edit = QTextEdit(
            self,
            placeholderText='Put unique article title here'
        )
        self.title_edit.resize(QSize(250, 25))
        self.title_edit.move(50, 50)

        btn_add_article = QPushButton('Add article', self)
        btn_add_article.resize(btn_add_article.sizeHint())
        btn_add_article.move(50, 100)
        btn_add_article.clicked.connect(self._add_article_action)

        btn_search_article = QPushButton('Search article', self)
        btn_search_article.resize(btn_search_article.sizeHint())
        btn_search_article.move(225, 100)
        btn_search_article.clicked.connect(self._search_article_action)

    def _open_file(self, filename):
        """
        Opens file with provided filename in default system editor.
        Creates file if it doesn't exists.
        """
        path = os.path.join(get_prefix_path(), filename)
        create_file_if_not_exists(path)

        print(path)

        if os.name == 'nt':
            subprocess.call(('notepad.exe', path))  # XXX: select editor...
        elif os.name == 'posix':
            subprocess.call(('xdg-open', path))

        return path

    def _add_article_action(self):
        LOG.debug('_add_article_action called')
        title = self.title_edit.toPlainText()
        path = self._open_file(title)
        self.client.add_article(title, path)

    def _search_article_action(self):
        title = self.title_edit.toPlainText()
        self.client.get_article(title)
        self._open_file(title)

    def start(self, app):
        self.show()
        sys.exit(app.exec_())

    def closeEvent(self, QCloseEvent):
        utils.kill_ipfsd_processes()
        # Delete GUI session
        self.deleteLater()
