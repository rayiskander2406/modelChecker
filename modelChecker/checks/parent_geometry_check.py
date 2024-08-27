from maya import cmds

from modelChecker import maya_utility

from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase

class ParentGeometryCheck(ValidationCheckBase):
    name = "parent_geometry"
    label = "Parent Geometry"
    node_type = NodeType.NODE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        parent_geometry = []
        for uuid in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(uuid)
            parents = cmds.listRelatives(node_name, p=True, fullPath=True) or []
            for parent in parents:
                children = cmds.listRelatives(parent, fullPath=True, type="mesh") or []
                if children:
                    parent_geometry.append(uuid)
                    
        return parent_geometry
    
    
    