from PySide6 import QtWidgets, QtCore
from modelChecker.constants import DataType, Severity, SEVERITY_COLORS

INACTIVE_COLOR = "#666666"
MAYA_COLOR = "#00cc00"
USD_COLOR = "#ddaa00"
DEFAULT_SEVERITY_COLOR = "#ffffff"

class CheckTooltipWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, text="", severity=Severity.MILD, data_type=DataType.BOTH):
        super().__init__(parent, QtCore.Qt.ToolTip)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.ToolTip)
        self.setStyleSheet("background-color: #333; color: white; border-radius: 5px; padding: 8px;")
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.data_type_layout = QtWidgets.QHBoxLayout()

        self.maya_label = QtWidgets.QLabel("Maya")
        self.usd_label = QtWidgets.QLabel("USD")
        
        self.data_type_layout.addWidget(self.maya_label)
        self.data_type_layout.addWidget(self.usd_label)
        
        self.label = QtWidgets.QLabel(text)
        self.layout.addLayout(self.data_type_layout)
        self.layout.addWidget(self.label)
        
        severity_color = SEVERITY_COLORS.get(severity, DEFAULT_SEVERITY_COLOR)
        self.severity_label = QtWidgets.QLabel(severity.name.capitalize())
        self.severity_label.setStyleSheet(f"color: {severity_color}; font-weight: bold;")
        self.layout.addWidget(self.severity_label)
        
        self.set_data_type(data_type)
        self.setVisible(False)
    
    def set_text(self, text):
        self.label.setText(text)
    
    def set_data_type(self, data_type: DataType):
        """Set the visual indication for the data type."""
        if data_type == DataType.MAYA:
            self.maya_label.setStyleSheet(f"color: {MAYA_COLOR}; font-weight: bold;")
            self.usd_label.setStyleSheet(f"color: {INACTIVE_COLOR}; font-weight: bold;")
        elif data_type == DataType.USD:
            self.maya_label.setStyleSheet(f"color: {INACTIVE_COLOR}; font-weight: bold;")
            self.usd_label.setStyleSheet(f"color: {USD_COLOR}; font-weight: bold;")
        elif data_type == DataType.BOTH:
            self.maya_label.setStyleSheet(f"color: {MAYA_COLOR}; font-weight: bold;")
            self.usd_label.setStyleSheet(f"color: {USD_COLOR}; font-weight: bold;")
    
    def set_severity(self, severity: Severity):
        """Update the severity label and its color."""
        severity_color = SEVERITY_COLORS.get(severity, DEFAULT_SEVERITY_COLOR)
        self.severity_label.setText(severity.name.capitalize())
        self.severity_label.setStyleSheet(f"color: {severity_color}; font-weight: bold;")
    
    def show_tooltip(self, position):
        self.move(position)
        self.setVisible(True)
    
    def hide_tooltip(self):
        self.setVisible(False)
