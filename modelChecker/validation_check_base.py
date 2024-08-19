from abc import ABC, abstractmethod
from modelChecker.constants import Severity

class ValidationCheckBase(ABC):
    name: str
    label: str
    category: str
    severity: Severity = Severity.SEVERE
    enabled: bool = True
    interrupted: bool = False
    settings = None
    error = False
    
    @abstractmethod
    def run(self, nodes):
        """Implemeneted run function."""
        pass
    
    @abstractmethod
    def fix(self):
        """Fix function to be implemented by the extended class."""
        raise NotImplementedError("Fix method not implemented.")
    
    @abstractmethod
    def select_error_nodes(self, context):
        """Fix function to be implemented by the extended class."""
        pass
    
    def has_fix(self) -> bool:
        """Check if the fix method has been implemented."""
        return self.__class__.fix is not ValidationCheckBase.fix
    
    def has_settings(self) -> bool:
        """Check if the implemented class has settings"""
        return self.__class__.settings is not None
    
    def has_errors(self):
        return self.__class__.error
    
    def interrupt(self):
        self.__class__.interrupted = True
        
    def get_name(self):
        return self.__class__.name
        
    def do_run(self, nodes):
        """ Wrapper function to handle user interruption and data collection """
        self.interrupted = False
        error_object = {}
        
        for result in self.run(nodes):
            if self.interrupted:
                break
            
            key, value = result
            error_object[key] = value
            
            yield result
        
        return error_object

