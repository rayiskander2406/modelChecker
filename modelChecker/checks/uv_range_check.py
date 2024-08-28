from collections import defaultdict

import maya.api.OpenMaya as om
from modelChecker.constants import NodeType, Severity
from modelChecker.validation_check_base import ValidationCheckBase

class UVRangeCheck(ValidationCheckBase):
    name = "uv_range"
    label = "UV Range"
    category = "UVs"
    node_type = NodeType.UV
    severity = Severity.BLOCKING
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        uv_range = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            mesh = om.MFnMesh(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
            Us, Vs = mesh.getUVs()
            for i in range(len(Us)):
                if Us[i] < 0 or Us[i] > 10 or Vs[i] < 0:
                    uv_range[uuid].append(i)
        return uv_range
    
    def usd_run(self, runner):
        return []