import functools
from abc import ABC
from enum import Enum

class AgentName(str, Enum):
    "If the request is not clear, return None"

    NONE = "NONE"
    QA_AGENT = "QA AGENT"
    DEVELOPER_AGENT = "DEVELOPER AGENT"
    COMMUNITY_MANAGER_AGENT = "COMMUNITY MANAGER AGENT"

class Agent(ABC):
    name: AgentName

    def get_node(self) -> functools.partial:
        raise NotImplementedError