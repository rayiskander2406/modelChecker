from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker import maya_utility

class NamespacesCheck(ValidationCheckBase):
    name = "namespaces"
    label = "Namespaces"
    category = "Naming"
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        output = []
        for uuid in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(uuid)
            if node_name and ":" in node_name:
                output.append(uuid)
        
        return output