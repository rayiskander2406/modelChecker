from collections import defaultdict

import maya.api.OpenMaya as om

from modelChecker.constants import NodeType, Severity
from modelChecker.validation_check_base import ValidationCheckBase

class TriangleCheck(ValidationCheckBase):
    name = "triangle"
    label = "Triangles"
    category = "Topology"
    node_type = NodeType.FACE
    severity = Severity.SEVERE
    
    def __init__(self):
        super().__init__()
    
    def run(self, runner):
        triangles = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            face_iterator = om.MItMeshPolygon(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
            while not face_iterator.isDone():
                edges = face_iterator.getEdges()
                if len(edges) == 3:
                    triangles[uuid].append(face_iterator.index())
                face_iterator.next()
        return triangles