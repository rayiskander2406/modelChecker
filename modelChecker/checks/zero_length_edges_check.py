from collections import defaultdict

import maya.api.OpenMaya as om

from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase


# TODO: Great opportunity for a settings attribute:
EDGE_DISTANCE_TOLERANCE = 0.00001

class ZeroLengthEdgesCheck(ValidationCheckBase):
    name = "zero_length_edges"
    label = "Zero Length Edges"
    category = "Topology"
    node_type = NodeType.EDGE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        zero_length_edges = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            edge_iterator = om.MItMeshEdge(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
            while not edge_iterator.isDone():
                if edge_iterator.length() <= EDGE_DISTANCE_TOLERANCE:
                    zero_length_edges[uuid].append(edge_iterator.index())
                edge_iterator.next()
        return zero_length_edges