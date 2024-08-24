from abc import ABC, abstractmethod
from modelChecker.constants import Severity, NodeType
from modelChecker import maya_utility

class ValidationCheckBase(ABC):
    name: str
    label: str
    category: str = "General"
    severity: Severity = Severity.SEVERE
    enabled: bool = True
    settings = None
    description = "Common description"
    node_type = NodeType.NODE
    
    def run(self, runner):
        """Implemeneted run function."""
        return []
    
    def usd_run(self, runner):
        return []
        
    
    def fix(self):
        """Fix function to be implemented by the extended class."""
        raise NotImplementedError("Fix method not implemented.")
    
    def select_error_nodes(self, context):
        """Fix function to be implemented by the extended class."""
        pass
    
    def render_html(self, context, verbosity_level = 2, last_failed = False):
        """Render the output to HTML"""
        
        html = "<br>" if last_failed and verbosity_level != 0 else ""
        
        if not context:
            html += f"&#10752; {self.label}<font color=#64a65a> [ SUCCESS ]</font><br>"
        else:
            if self.node_type == NodeType.NODE:
                if verbosity_level == 0:
                    word = "issue" if len(context) == 1 else "issues"
                    html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] - {len(context)} {word}</font><br>"   
                else:
                    html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] </font><br>"   
                    for node in context:
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += "&#9492;&#9472; {}<br>".format(node_name)
            else:                
                if verbosity_level == 0:
                    word = "issue" if len(context) == 1 else "issues"
                    html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] - {len(context)} {word}</font><br>"   

                if verbosity_level == 1:
                    html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] </font><br>"   
                    for node in context:
                        word = "issue" if len(context[node]) == 1 else "issues"
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += "&#9492;&#9472; {} - <font color=#9c4f4f>{} {}</font><br>".format(node_name, len(context[node]), word)
                
                if  verbosity_level == 2:
                    html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] </font><br>"   
                    for node in context:
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += "&#9492;&#9472; <font color=#9c4f4f>{}</font><br>".format(node_name)
                        for component in context[node]:
                            html += f"&nbsp;&nbsp;&#9492;&#9472; <font>{node_name} - {component}</font><br>".format(node_name, component)
        return html
    
    def has_fix(self) -> bool:
        """Check if the fix method has been implemented."""
        return self.__class__.fix is not ValidationCheckBase.fix
    
    def has_maya_run(self) -> bool:
        """Check if the fix method has been implemented."""
        return self.__class__.run is not ValidationCheckBase.run
    
    def has_usd_run(self) -> bool:
        """Check if the fix method has been implemented."""
        return self.__class__.usd_run is not ValidationCheckBase.usd_run
    
    def has_settings(self) -> bool:
        """Check if the implemented class has settings"""
        return self.__class__.settings is not None
    
    def get_name(self):
        return self.__class__.name
        
    def do_run(self, runner):
        """ Wrapper function - may come in handy. """

        maya_data = self.run(runner)
        # usd_data = self.usd_run(runner)
        return maya_data

