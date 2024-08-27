from modelChecker import maya_utility

from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase

from maya import cmds

EXCLUDED_NODES = ['displayLayer', 'renderLayer', 'objectSet', 'groupId']

class HistoryCheck(ValidationCheckBase):
    name = "history"
    label = "History"
    category = "Naming"
    node_type = NodeType.NODE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        history = []
        for uuid in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(uuid)
            
            shape = cmds.listRelatives(node_name, shapes=True, fullPath = True)
            
            if shape:
                history_items = cmds.listHistory(shape)
                
                for item in history_items:
                    if cmds.nodeType(item) not in EXCLUDED_NODES:
                        history.append(uuid)
                        break
        return history
