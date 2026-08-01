from enum import Enum

class Task(str, Enum):
    GENERATE = "generate"
    TRANSLATE = "translate"
    EXPLAIN = "explain"    
    UNKNOWN = "unknown"