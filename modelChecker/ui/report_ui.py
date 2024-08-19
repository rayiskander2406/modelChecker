from PySide6 import QtWidgets

class ReportUI(QtWidgets.QWidget):
    
    def __init__(self, consolidated_report = False):
        super().__init__()
        
        self.consolidated_report = consolidated_report
        self.build_ui()
        
        
    def build_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        
        report_settings_widget = QtWidgets.QWidget()
        report_settings_layout = QtWidgets.QHBoxLayout(report_settings_widget)
        report_settings_layout.addWidget(QtWidgets.QLabel("Report:"))

        self.report_ui = QtWidgets.QTextEdit()
        
        
        progress_widget = QtWidgets.QWidget()
        progress_layout = QtWidgets.QVBoxLayout(progress_widget)
        
        progress_current_check = QtWidgets.QProgressBar()
        progress_all_checks = QtWidgets.QProgressBar()
        
        progress_layout.addWidget(progress_current_check)
        progress_layout.addWidget(progress_all_checks)
        
        self.main_layout.addWidget(report_settings_widget)
        self.main_layout.addWidget(progress_widget)
        self.main_layout.addWidget(self.report_ui)
    
    def render_report(self, error_object):
        pass
    
    def clear(self):
        self.report_ui.setText("")
        