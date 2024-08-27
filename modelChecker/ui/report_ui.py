from PySide6 import QtWidgets, QtCore

from modelChecker import maya_utility

class ReportUI(QtWidgets.QWidget):
    verbosity_signal = QtCore.Signal()
    
    def __init__(self, consolidated_report = False):
        super().__init__()
        self.consolidated_report = consolidated_report
        self.verbosity_level = 0
        self._build_ui()
        
    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        
        report_style_widget = QtWidgets.QWidget()
        report_style_layout = QtWidgets.QHBoxLayout(report_style_widget)
        
        report_style_layout.addWidget(QtWidgets.QLabel("LOG Detail: "))
        
        self.level_combo_box = QtWidgets.QComboBox()
        self.level_combo_box.addItem("Overview")
        self.level_combo_box.addItem("Default")
        self.level_combo_box.addItem("Verbose")
        self.level_combo_box.currentIndexChanged.connect(self.update_verbosity_level)

        
        report_style_layout.addWidget(self.level_combo_box)
        
        self.report_ui = QtWidgets.QTextEdit()
        self.report_ui.setReadOnly(True)
        
        main_layout.addWidget(report_style_widget)
        main_layout.addWidget(self.report_ui)
    
    def update_verbosity_level(self, index):
        self.verbosity_level = index
        self.verbosity_signal.emit()
        
    def render_report(self, result_object, all_check_widgets):
        self.report_ui.clear()
        html = ""

        if result_object["maya_nodes"]:
            html += self._render_section_header(result_object, "Maya")
            maya_error_object = result_object['maya_error_object']
            for check_widget in all_check_widgets:
                check = check_widget.check
                if check.name in maya_error_object:
                    html += check.render_maya_data_html(maya_error_object[check.name], self.verbosity_level)

        if result_object["usd_nodes"]:
            usd_error_object = result_object['usd_error_object']
            html += self._render_section_header(result_object, "USD")
            for check_widget in all_check_widgets:
                check = check_widget.check
                if check.name in usd_error_object:
                    html += check.render_usd_data_html(usd_error_object[check.name], self.verbosity_level) or ""
                    
        self.report_ui.insertHtml(html)

    
    
    def _render_section_header(self, result_object, data_type):        
        html = f"<h2>Current context: {result_object['context'].capitalize()} ({data_type})</h2>"
        print(result_object)
        check_widgets = result_object['check_widgets']
        nodes = result_object['maya_nodes'] if data_type == "Maya" else result_object['usd_nodes']
        error_object = result_object['maya_error_object'] if data_type == "Maya" else result_object['usd_error_object']
        if self.verbosity_level == 0:
            html += f"""
            <table style="margin: 6px; border-spacing: 4px;">
                <tr>
                    <td>Checks Ran:</td>
                    <td style="padding-left: 8px;">{len(error_object)}</td>
                </tr>
                <tr>
                    <td>{data_type} Nodes checked:</td>
                    <td style="padding-left: 8px;">{len(nodes)}</td>
                </tr>
            </table>
            """
        else:
            if data_type == "Maya":
                rendered_nodes = "N/A" if not nodes else "<br>".join(str(maya_utility.get_name_from_uuid(node, long=False)) for node in nodes)
            else:
                rendered_nodes = "N/A" if not nodes else "<br>".join(str(node) for node in nodes)
            rendered_checks = "<br>".join(check_widget.check.label for check_widget in check_widgets)
            
            html += f"""
            <table style="margin: 6px; border-spacing: 4px;">
                <tr>
                    <td>Checks Ran:</td>
                    <td style="padding-left: 8px;">{rendered_checks}</td>
                </tr>
                <tr>
                    <td>{data_type} Nodes checked:</td>
                    <td style="padding-left: 8px;">&nbsp;<br>{rendered_nodes}
                </td>
                </tr>
            </table>
            """
                
        html += "<br>"
        
        return html
    
    def set_error(self, message):
        self.report_ui.clear()
        html = f"<h2>Error: {message}</h2>"
        self.report_ui.insertHtml(html)
    
    def clear(self):
        self.report_ui.clear()
        