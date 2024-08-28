from modelChecker.constants import Severity
from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker import maya_utility

class TrailingNumberCheck(ValidationCheckBase):
    name = "trailing_number"
    label = "Trailing Number"
    category = "Naming"
    severity = Severity.MODERATE
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        output = []
        for node in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(node)
            if node_name and node_name[-1].isdigit():
                output.append(node)
        return output
    
    def usd_run(self, runner):
        output = []
        for node in runner.get_usd_nodes():
            if node[-1].isdigit():
                output.append(node)
        return output
        