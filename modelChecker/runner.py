""" The Runner is in charge of running all checks"""
from maya import cmds

class Runner():
    def __init__(self):
        self.current_check = None
        self.current_context = "all"
        self.contexts = { "all": { "trailing_numbers": {}}}
        self.interrupt = False
    
    def interrupt(self):
        if self.current_check is not None:
            self.current_check.interrupt()
    
    def run_all(self, checks):
        nodes = self.get_all_nodes()
        context = self.get_context()
        
        if context not in self.contexts:
            self.contexts[context] = {}
            
        for check in checks:
            if self.interrupt:
                break
            self.current_check = check
            name = check.get_name()
            check_result = []
            
            for result in check.do_run(nodes):
                if self.interrupt:
                    break
                check_result.append(result)
            
            self.contexts[name] = check_result
            
        self.current_check = None
        self.interrupt = False
    
    def reset_contexts(self):
        self.contexts = {}
        self.current_context = "all"
    
    def get_current_context(self):
        return self.contexts[self.current_context]
    
    def set_current_context(self, context):
        self.current_context = context

    def run(self, check):
        print(check.run(self.get_all_nodes()))
    
    def fix(self, check):
        print("Fix: ", check)
        
    def select_error_nodes(self, check):
        context = self.contexts[self.current_context]
        
        if check.name in context:
            check.select_error_nodes(context[check.name])
            
    def get_context(self):
        return self.current_context

    def get_all_nodes(self):
        all_nodes = cmds.ls(transforms=True, long=True)
        all_usable_nodes = []
        for node in all_nodes:
            if node not in {'|front', '|persp', '|top', '|side'}:
                uuid = cmds.ls(node, uuid=True)[0]
                all_usable_nodes.append(uuid)
        return all_usable_nodes
    
    def get_node_name(uuid):
        node_name = cmds.ls(uuid, uuid=True)
        if node_name:
            return node_name[0]
        return None