from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker import maya_utility

from maya import cmds

class EmptyGroupsCheck(ValidationCheckBase):
    name = "empty_groups"
    label = "Empty Groups"
    category = "General"
    node_type = NodeType.NODE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        empty_groups = []
        for uuid in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(uuid)
            if not cmds.listRelatives(node_name, allDescendents=True):
                empty_groups.append(uuid)
        return empty_groups