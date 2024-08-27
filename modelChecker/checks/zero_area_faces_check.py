from collections import defaultdict

import maya.api.OpenMaya as om

from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase


ZERO_AREA_FACE_TOLERANCE = 0.00001

class ZeroAreaFacesCheck(ValidationCheckBase):
    name = "zero_area_faces"
    label = "Zero Area Faces"
    category = "Topology"
    node_type = NodeType.FACE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        zero_area_faces = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            face_iterator = om.MItMeshPolygon(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
            while not face_iterator.isDone():
                face_area = face_iterator.getArea()
                if face_area <= ZERO_AREA_FACE_TOLERANCE:
                    zero_area_faces[uuid].append(face_iterator.index())
                face_iterator.next()
        return zero_area_faces