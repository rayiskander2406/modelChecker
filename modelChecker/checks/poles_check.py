from collections import defaultdict

import maya.api.OpenMaya as om

from modelChecker.constants import NodeType, Severity
from modelChecker.validation_check_base import ValidationCheckBase

class PolesCheck(ValidationCheckBase):
    name = "poles"
    label = "Poles"
    category = "Topology"
    node_type = NodeType.VERTEX
    severity = Severity.MILD
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        poles = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            vertexIt = om.MItMeshVertex(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
            while not vertexIt.isDone():
                if vertexIt.numConnectedEdges() > 5:
                    poles[uuid].append(vertexIt.index())
                vertexIt.next()
        return poles