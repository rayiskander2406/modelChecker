from collections import defaultdict

import maya.api.OpenMaya as om
from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase

class OpenEdgesCheck(ValidationCheckBase):
    name = "open_edges"
    label = "Open Edges"
    category = "Topology"
    node_type = NodeType.EDGE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        open_edges = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            edgeIt = om.MItMeshEdge(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
            while not edgeIt.isDone():
                if edgeIt.numConnectedFaces() < 2:
                    open_edges[uuid].append(edgeIt.index())
                edgeIt.next()
        return open_edges