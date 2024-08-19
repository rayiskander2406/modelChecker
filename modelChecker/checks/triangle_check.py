from modelChecker.validation_check_base import ValidationCheckBase
from ..validation_check_base import Severity

class TriangleCheck(ValidationCheckBase):
    name = "triangle_check"
    label = "Triangle Check"
    category = "Topology"
    severity = Severity.MILD
    
    def __init__(self):
        self.errors = { "hello": ""}
        super()
    
    def run(self):
        print("RUN!")
    
    def select_error_nodes(self, context):
        print(context)
    
    def fix(self):
        print("This one, really?")
