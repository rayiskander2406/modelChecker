from PySide6 import QtWidgets, QtCore
from modelChecker.constants import SEVERITY_COLORS, PASS_COLOR

class CheckWidget(QtWidgets.QWidget):
    select_error_signal = QtCore.Signal(object)
    run_signal = QtCore.Signal(object)
    fix_signal = QtCore.Signal(object)
    
    def __init__(self, check):
        super().__init__()
        self.check = check()
        self.show_options = False
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        body_widget = QtWidgets.QWidget()
        self.body_layout = QtWidgets.QHBoxLayout(body_widget)
        
        self.main_layout.setSpacing(4)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(
            "padding: 0px; margin: 0px;")
        
        self.check_label = QtWidgets.QLabel(self.check.label)
        self.check_label.setMinimumWidth(180)
        
        self.settings_widget = QtWidgets.QWidget()
        self.settings_widget.setVisible(False)
        
        self.settings_layout = QtWidgets.QVBoxLayout(self.settings_widget)
        self.settings_layout.addWidget(QtWidgets.QLabel("This is here for sure!!"))
        
        self.enabled = QtWidgets.QCheckBox()
        self.enabled.setMaximumWidth(20)
        
        run_button = QtWidgets.QPushButton("Run")
        run_button.clicked.connect(self.run)
        run_button.setMaximumWidth(40)
        
        fix_button = QtWidgets.QPushButton("Fix")
        fix_button.clicked.connect(self.fix)
        fix_button.setEnabled(self.check.has_fix())
        fix_button.setMaximumWidth(40)
        
        select_error_nodes_button = QtWidgets.QPushButton("Select Error Nodes")
        select_error_nodes_button.clicked.connect(self.select_error)
        select_error_nodes_button.setMaximumWidth(150)
        
        settings_enabled = self.check.has_settings()
        
        label = "\u2699" if settings_enabled else "\u2716"
        settings_button = QtWidgets.QPushButton(label)
        settings_button.setMaximumWidth(40)

        if settings_enabled:
            settings_button.clicked.connect(self._toggle_settings)
        else:
            settings_button.setEnabled(False)
        
        self.body_layout.addWidget(self.check_label)
        self.body_layout.addWidget(self.enabled)
        self.body_layout.addWidget(run_button)
        self.body_layout.addWidget(fix_button)
        self.body_layout.addWidget(select_error_nodes_button)
        self.body_layout.addWidget(settings_button)
        self.main_layout.addWidget(body_widget)
        self.main_layout.addWidget(self.settings_widget)
    
    def _toggle_settings(self):
        self.settings_widget.setVisible(not self.settings_widget.isVisible())
        
    def _update_ui(self):
        if self.check.has_errors():
            color = SEVERITY_COLORS.get(self.check.severity, "#000000")
            self.check_label.setStyleSheet(f'background-color: {color}')
        else:
            self.check_label.setStyleSheet(f'background-color: {PASS_COLOR}')
            
    def is_checked(self) -> bool:
        return self.enabled.isChecked()
    
    def set_checked(self, check: bool):
        self.enabled.setChecked(check)
    
    def select_error(self):
        """Signal to the runner, to perform the errors"""
        self.select_error_signal.emit(self.check)
    
    def fix(self):
        self.fix_signal.emit(self.check)
    
    def run(self):
        self.run_signal.emit(self.check)
        
        