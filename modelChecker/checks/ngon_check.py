from modelChecker.validation_check_base import ValidationCheckBase

class NgonCheck(ValidationCheckBase):
    name = "ngons"
    label = "Ngons"
    category = "Topology"
    settings = {}
    
    def __init__(self):
        self.errors = { "hello": ""}
        super()
    
    def select_error_nodes(self, context):
        print(context)
    
    def run(self, hello):
        print(hello)
    
    def fix(self):
        print("This one, really?")
