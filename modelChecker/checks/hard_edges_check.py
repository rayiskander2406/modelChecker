from collections import defaultdict

import maya.api.OpenMaya as om

from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase

class HardEdgesCheck(ValidationCheckBase):
    name = "hard_edges"
    label = "Hard Edges"
    category = "Topology"
    node_type = NodeType.EDGE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        hard_edges = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            edge_iterator = om.MItMeshEdge(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
            while not edge_iterator.isDone():
                if edge_iterator.isSmooth is False and edge_iterator.onBoundary() is False:
                    hard_edges[uuid].append(edge_iterator.index())
                edge_iterator.next()
        return hard_edges