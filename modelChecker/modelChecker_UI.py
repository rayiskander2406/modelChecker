import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
from PySide6 import QtCore, QtWidgets, QtGui
from shiboken6 import wrapInstance
from modelChecker.constants import TITLE, OBJ_NAME
from modelChecker.__version__ import __version__
from modelChecker.ui.report_ui import ReportUI
from modelChecker.ui.checks_ui import ChecksUI
from modelChecker.runner import Runner

def getMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    mainWindow = wrapInstance(int(mainWindowPtr), QtWidgets.QWidget)
    return mainWindow        

class UI(QtWidgets.QMainWindow):
    qmwInstance = None
    
    @classmethod
    def show_UI(cls):
        if not cls.qmwInstance:
            cls.qmwInstance = UI()
        if cls.qmwInstance.isHidden():
            cls.qmwInstance.show()
        else:
            cls.qmwInstance.raise_()
            cls.qmwInstance.activateWindow()

    def __init__(self, parent=getMainWindow()):
        super().__init__(parent)
        
        self.current_check = None
        
        self.setObjectName(OBJ_NAME)
        self.setWindowTitle(f"{TITLE} - {__version__}")
        self.extend_ui_classes() 
        self.build_ui()
    
    def extend_ui_classes(self):
        self.checks_ui = ChecksUI()
        self.report_ui = ReportUI()
        self.runner = Runner()
        
        self.checks_ui.select_error_signal.connect(self.handle_error_selected)
        self.checks_ui.fix_signal.connect(self.handle_fix)
        self.checks_ui.run_signal.connect(self.handle_run)
        
    
    def build_ui(self):
        main_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        splitter = QtWidgets.QSplitter()
        
        
        report_buttons_widget = QtWidgets.QWidget()
        report_buttons_layout = QtWidgets.QHBoxLayout(report_buttons_widget)
        report_buttons_layout.addStretch()
        report_buttons_layout.addWidget(QtWidgets.QPushButton("Clear"))
        run_all_button = QtWidgets.QPushButton("Run Checks on Selected / All")
        run_all_button.clicked.connect(self.run_all)
        report_buttons_layout.addWidget(run_all_button)
        
        left_widget = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left_widget)
        
        left_layout.addWidget(self.report_ui)
        left_layout.addWidget(report_buttons_widget)
        
        splitter.addWidget(self.checks_ui)
        splitter.addWidget(left_widget)
        main_layout.addWidget(splitter)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.runner.interrupt() 
        else:
            super().keyPressEvent(event)
    
    # individual widgets handles
    def handle_error_selected(self, check):
        """Handle the check selection and update the UI accordingly."""
        self.runner.select_error_nodes(check)
        
        
    def handle_fix(self, check):
        """Handle the check selection and update the UI accordingly."""
        self.runner.fix(check)
        
        
    def handle_run(self, check):
        """Handle the check selection and update the UI accordingly."""
        self.runner.run(check)
        
    
    def run_all(self):
        active_checks = self.checks_ui.get_all_active_checks()
        self.runner.run_all(active_checks)