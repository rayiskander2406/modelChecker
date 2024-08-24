from collections import defaultdict

import maya.api.OpenMaya as om
from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase

class LaminaCheck(ValidationCheckBase):
    name = "lamina"
    label = "Lamina"
    category = "Topology"
    node_type = NodeType.FACE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        lamina = defaultdict(list)
        for dag_path in runner.get_mesh_iterator():
            face_iterator = om.MItMeshPolygon(dag_path)
            fn = om.MFnDependencyNode(dag_path.node())
            uuid = fn.uuid().asString()
            while not face_iterator.isDone():
                laminaFaces = face_iterator.isLamina()
                if laminaFaces is True:
                    lamina[uuid].append(face_iterator.index())
                face_iterator.next()
        return lamina