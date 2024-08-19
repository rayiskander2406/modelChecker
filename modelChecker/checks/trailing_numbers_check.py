from modelChecker.validation_check_base import ValidationCheckBase
from ..validation_check_base import Severity

from maya import cmds 

class TrailingNumbersCheck(ValidationCheckBase):
    name = "trailing_numbers"
    label = "Trailing Numbers"
    category = "Naming"
    settings = {}
    severity = Severity.BLOCKING
    
    def __init__(self):
        super()
    
    def select_error_nodes(self, context):
        print(context)
    
    def run(self, nodes):
        for node in nodes:
            nodeName = self._get_node_name(node)
            if nodeName and nodeName[-1].isdigit():
                yield "nodes", node
    
    def fix(self):
        print("This one, really?")

    def _get_node_name(self, uuid):
        node_name = cmds.ls(uuid, uuid=True)
        if node_name:
            return node_name[0]
        return None