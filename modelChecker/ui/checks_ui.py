from PySide6 import QtWidgets, QtCore

from modelChecker.checks import all_checks

from modelChecker.ui.check_widget import CheckWidget
from modelChecker.ui.category_widget import CategoryWidget


class ChecksUI(QtWidgets.QWidget):
    select_error_signal = QtCore.Signal(object)
    run_signal = QtCore.Signal(object)
    fix_signal = QtCore.Signal(object)
    
    def __init__(self):
        super().__init__()
        
        self.categories = {}
        self.checks = {}
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.content_widget = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0) 

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)

        group_box = QtWidgets.QWidget()
        group_box_layout = QtWidgets.QHBoxLayout(group_box)

        combo_box = QtWidgets.QComboBox(self)
        combo_box.addItems(["Character Modelling", "Environment", "Vehicles"])
        
        settings_button = QtWidgets.QPushButton("\u2699")
        settings_button.setMaximumWidth(30)
        
        group_box_layout.addWidget(QtWidgets.QLabel("Preset: "))
        group_box_layout.addWidget(combo_box,1)
        group_box_layout.addWidget(settings_button)

        categories = sorted({ x.category for x in all_checks })
        
        for category in categories:
            category_widget = CategoryWidget(category)
            self.categories[category] = category_widget
            self.content_layout.addWidget(category_widget)
        
        sorted_checks = sorted(all_checks, key=lambda x: x.label)
        
        for check in sorted_checks:
            check_widget = CheckWidget(check)
            self.checks[check.name] = check_widget
            self.categories[check.category].add_check(check_widget)
            check_widget.select_error_signal.connect(self.handle_error_selected)
            check_widget.run_signal.connect(self.handle_run)
            check_widget.fix_signal.connect(self.handle_fix)

            
        self.content_layout.addStretch()
        
        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout(button_widget)
        
        uncheck_button = QtWidgets.QPushButton("Uncheck")
        uncheck_button.clicked.connect(self.uncheck)
        
        invert_button = QtWidgets.QPushButton("Invert")
        invert_button.clicked.connect(self.invert_checks)
        
        uncheck_passed_button = QtWidgets.QPushButton("Uncheck Passed")
        uncheck_passed_button.clicked.connect(self.uncheck_passed)
        
        check_all_button = QtWidgets.QPushButton("Check All")
        check_all_button.clicked.connect(self.check_all)
        
        button_layout.addWidget(uncheck_button)
        button_layout.addWidget(invert_button)
        button_layout.addWidget(uncheck_passed_button)
        button_layout.addWidget(check_all_button)
        
        self.main_layout.addWidget(group_box)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(button_widget)

    def get_all_active_checks(self):
        active_checks = []
        for check_widget in self.checks.values():
            if check_widget.is_checked():
                active_checks.append(check_widget.check)
        return active_checks
    
    def uncheck_passed(self):
        for check_widget in self.checks.values():
            check_widget.set_checked(check_widget.check.has_errors())
    
    def invert_checks(self):
        for check_widget in self.checks.values():
            check_widget.set_checked(not check_widget.is_checked())
            
    def uncheck(self):
        for check_widget in self.checks.values():
            check_widget.set_checked(False)
            
    def check_all(self):
        for check_widget in self.checks.values():
            check_widget.set_checked(True)
            
    def handle_error_selected(self, check):
        """Handle the error_selected_signal from CheckWidget and emit the select_error_signal."""
        self.select_error_signal.emit(check)
        
    def handle_fix(self, check):
        """Handle the error_selected_signal from CheckWidget and emit the select_error_signal."""
        self.fix_signal.emit(check)
        
    def handle_run(self, check):
        """Handle the error_selected_signal from CheckWidget and emit the select_error_signal."""
        self.run_signal.emit(check)