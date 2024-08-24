from PySide6 import QtWidgets, QtCore
from modelChecker.constants import DataType

PRESETS_EXAMPLES = ["Character Modelling", "Environment", "Vehicles"]

class SettingsUI(QtWidgets.QWidget):
    change_preset_signal = QtCore.Signal(object)
    
    def __init__(self, data_type: DataType):
        super().__init__()
        
        self.selected_data_type = data_type
        self.settings_expanded = False
        self.preset = "Character Modeling"
        
        self._build_preset_ui()
        
        settings_layout = QtWidgets.QVBoxLayout(self)
        
        self.settings_widget = QtWidgets.QWidget()
        self.settings_widget.setVisible(self.settings_expanded)
        expanded_settings_layout = QtWidgets.QVBoxLayout(self.settings_widget)
        
        data_type_settings_widget = QtWidgets.QWidget()
        data_type_settings_layout = QtWidgets.QHBoxLayout(data_type_settings_widget)
        
        self.maya_radio = QtWidgets.QRadioButton("Maya Data")
        self.usd_radio = QtWidgets.QRadioButton("USD Data")
        self.both_radio = QtWidgets.QRadioButton("Both")
        
        self.usd_or_maya_button_group = QtWidgets.QButtonGroup(self)
        self.usd_or_maya_button_group.addButton(self.maya_radio, DataType.MAYA.value)
        self.usd_or_maya_button_group.addButton(self.usd_radio, DataType.USD.value)
        self.usd_or_maya_button_group.addButton(self.both_radio, DataType.BOTH.value)
        
        # Set the initial data type based on the passed enum
        self.set_data_type(data_type)
        
        self.usd_or_maya_button_group.buttonClicked.connect(self.on_data_type_changed)
        
        data_type_settings_layout.addWidget(QtWidgets.QLabel("Run on:"))
        data_type_settings_layout.addWidget(self.maya_radio)
        data_type_settings_layout.addWidget(self.usd_radio)
        data_type_settings_layout.addWidget(self.both_radio)
        
        expanded_settings_layout.addWidget(data_type_settings_widget)
        
        settings_layout.addWidget(self.preset_widget)
        settings_layout.addWidget(self.settings_widget)
    
    def _build_preset_ui(self):
        self.preset_widget = QtWidgets.QWidget()
        
        preset_layout = QtWidgets.QHBoxLayout(self.preset_widget)

        combo_box = QtWidgets.QComboBox(self)
        combo_box.addItems(PRESETS_EXAMPLES)
        
        settings_button = QtWidgets.QPushButton("\u2699")
        settings_button.setMaximumWidth(30)
        settings_button.clicked.connect(self.toggle_settings)
        
        preset_layout.addWidget(QtWidgets.QLabel("Preset: "))
        preset_layout.addWidget(combo_box, 1)
        preset_layout.addWidget(settings_button)
        
    def toggle_settings(self):
        self.settings_expanded = not self.settings_expanded
        self.settings_widget.setVisible(self.settings_expanded)
    
    def set_data_type(self, data_type: DataType):
        self.selected_data_type = data_type
        if data_type == DataType.MAYA:
            self.maya_radio.setChecked(True)
        elif data_type == DataType.USD:
            self.usd_radio.setChecked(True)
        elif data_type == DataType.BOTH:
            self.both_radio.setChecked(True)
    
    def on_data_type_changed(self, button):
        data_type = DataType(self.usd_or_maya_button_group.id(button))
        self.set_data_type(data_type)

    def get_data_type(self):
        return self.selected_data_type