from collections import defaultdict

from maya import cmds

from modelChecker import maya_utility
from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase

class SelfPenetratingUVsCheck(ValidationCheckBase):
    name = "self_penetrating_uvs"
    label = "Self Penetrating UVs"
    category = "UVs"
    node_type = NodeType.UV
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        self_penetrating_uvs = defaultdict(list)
        for mesh in runner.get_mesh_shape_iterator():
            overlapping = cmds.polyUVOverlap(f"{mesh}.f[*]", overlappingComponents=True)
            if overlapping:
                uuid = maya_utility.get_uuid_from_shape(mesh)
                formatted = [ overlap.split(".f[")[1][:-1] for overlap in overlapping ]
                self_penetrating_uvs[uuid].extend(formatted)
        return self_penetrating_uvs
                
    
