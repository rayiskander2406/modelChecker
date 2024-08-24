from collections import defaultdict
from modelChecker import maya_utility

from modelChecker.constants import NodeType
from modelChecker.validation_check_base import ValidationCheckBase

class DuplicatedNamesCheck(ValidationCheckBase):
    name = "duplicated_names"
    label = "Duplicated Names"
    category = "Naming"
    node_type = NodeType.NODE
    
    def __init__(self):
        super().__init__()
        
    def run(self, runner):
        nodes_by_short_name = defaultdict(list)
        for uuid in runner.get_maya_nodes():
            node_name = maya_utility.get_name_from_uuid(uuid)
            name = node_name.rsplit('|', 1)[-1]
            nodes_by_short_name[name].append(uuid)
            
        invalid = []
        for uuids in nodes_by_short_name.values():
            if len(uuids) > 1:
                invalid.extend(uuids)
        return invalid
        
