from modelChecker.validation_check_base import ValidationCheckBase
from modelChecker import maya_utility

from maya import cmds

class DefaultShaderCheck(ValidationCheckBase):
    name = "default_shader"
    label = "Default Shader"
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        shaders = []        
        for mesh in runner.get_mesh_shape_iterator():
            shadingGrps = cmds.listConnections(mesh, type='shadingEngine')
            if shadingGrps[0] != 'initialShadingGroup':
                uuid = maya_utility.get_uuid_from_shape(mesh)
                shaders.append(uuid)
        return shaders