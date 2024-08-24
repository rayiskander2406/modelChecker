from enum import Enum, auto

class Severity(Enum):
    MILD = auto()
    MODERATE = auto()
    SEVERE = auto()
    BLOCKING = auto()

class DataType(Enum):
    MAYA = auto()
    USD = auto()
    BOTH = auto()

TITLE = "Model Checker"
OBJ_NAME = "modelChecker"

SEVERITY_COLORS = {
    Severity.MILD: "#444466",        
    Severity.MODERATE: "#666644",    
    Severity.SEVERE: "#664444",      
    Severity.BLOCKING: "#884444",    
}

class NodeType(Enum):
    UV = auto()
    VERTEX = auto()
    EDGE = auto()
    FACE = auto()
    NODE = auto()

PASS_COLOR = "#446644"

EXPANDED_LABEL = '\u2193'
COLLAPSED_LABEL = '\u21B5'