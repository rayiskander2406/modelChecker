from maya import cmds

from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker import maya_utility

class ShapeNamesCheck(ValidationCheckBase):
    name = "shape_names"
    label = "Shape Names"
    category = "Naming"
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        shape_names = []
        for node in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(node)
            if node_name:
                shape = cmds.listRelatives(node_name, shapes=True)
                if shape:
                    node_name_start = node_name.split('|')[-1]
                    expected_shape_name = node_name_start + "Shape"
                    if shape[0] != expected_shape_name:
                        shape_names.append(node)
        return shape_names