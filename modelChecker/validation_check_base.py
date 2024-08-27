from abc import ABC
from modelChecker.constants import Severity, NodeType, DataType, COMPONENT_MAPPING
from modelChecker import maya_utility
from maya import cmds

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
    
    
    def format_usd_data(self, context):
        if not context:
            return []
        return [node for node in context]
            
    
    def format_maya_data(self, context):
        if not context:
            return []
        
        if self.node_type == NodeType.NODE:
            return [maya_utility.get_name_from_uuid(uuid) for uuid in context]
        else:
            maya_nodes = []
            for uuid, components in context.items():
                name = maya_utility.get_name_from_uuid(uuid)
                for component in components:
                    maya_nodes.append(name + COMPONENT_MAPPING[self.node_type].format(component))
            return maya_nodes
                    
    def do_select_error_nodes(self, maya_data, usd_data):
        maya_nodes = self.format_maya_data(maya_data.get(self.name))
        usd_nodes = self.format_usd_data(usd_data.get(self.name))
        
        cmds.select(maya_nodes + usd_nodes)        
    
    def render_usd_data_html(self, context, verbosity_level = 2, last_failed = False):
        html = "<br>" if last_failed and verbosity_level != 0 else ""
        if not context:
            html += f"&#10752; {self.label}<font color=#64a65a> [ SUCCESS ]</font><br>"
        else:
            if verbosity_level == 0:
                word = "issue" if len(context) == 1 else "issues"
                html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] - {len(context)} {word}</font><br>"   
            else:
                html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] </font><br>"   
                for node in context:
                    html += f"&#9492;&#9472; {node}<br>"
        return html
    
    def render_maya_data_html(self, context, verbosity_level=2):
        """Render the output to HTML"""
        
        html = ""

        if not context:
            html += f"&#10752; {self.label}<font color=#64a65a> [ SUCCESS ]</font><br>"
        else:
            html += "<br>"
            if verbosity_level == 0:
                word = "issue" if len(context) == 1 else "issues"
                html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] - {len(context)} {word}</font><br>"
            elif verbosity_level == 1:
                html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] </font><br>"
                if self.node_type == NodeType.NODE:
                    for node in context:
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += f"&#9492;&#9472; <font color=#9c4f4f>{node_name}</font><br>"
                else:
                    for node, components in context.items():
                        word = "issue" if len(components) == 1 else "issues"
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += f"&#9492;&#9472; {node_name} - <font color=#9c4f4f>{len(components)} {word}</font><br>"
            elif verbosity_level == 2:
                html += f"&#10752; {self.label}<font color=#9c4f4f> [ FAILED ] </font><br>"
                if self.node_type == NodeType.NODE:
                    for node in context:
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += f"&#9492;&#9472; <font color=#9c4f4f>{node_name}</font><br>"
                else:
                    for node, components in context.items():
                        node_name = maya_utility.get_name_from_uuid(node)
                        html += f"&#9492;&#9472; <font color=#9c4f4f>{node_name}</font><br>"
                        for component in components:
                            formatted_component = COMPONENT_MAPPING[self.node_type].format(component)
                            html += f"&nbsp;&nbsp;&#9492;&#9472; <font>{node_name}{formatted_component}</font><br>"

            html += "<br>"

        return html



    
    def has_fix(self) -> bool:
        """Check if the fix method has been implemented."""
        return self.__class__.fix is not ValidationCheckBase.fix
    
    
    def has_settings(self) -> bool:
        """Check if the implemented class has settings"""
        return self.__class__.settings is not None
    
    def get_name(self):
        return self.__class__.name
        
    def do_run(self, runner):
        """ Wrapper function - may come in handy. """

        maya_data = self.run(runner)
        usd_data = self.usd_run(runner)
        return maya_data, usd_data

    def get_data_type(self):
        """Check which run method has been implemented and return the corresponding DataType."""
        cls = type(self)
        
        run_overridden = cls.__dict__.get('run', None) is not None
        
        usd_run_overridden = cls.__dict__.get('usd_run', None) is not None
        
        if run_overridden and usd_run_overridden:
            return DataType.BOTH
        
        if run_overridden:
            return DataType.MAYA
        
        if usd_run_overridden:
            return DataType.USD

        return None

    
    def has_usd_run(self) -> bool:
        """Check if the fix method has been implemented."""
        return self.__class__.usd_run is not ValidationCheckBase.usd_run