import functools
from abc import ABC
from enum import Enum

class AgentName(str, Enum):
    "If the request is not clear, return None"

    NONE = "NONE"
    QA_AGENT = "Technical Q&A Agent"
    DEVELOPER_AGENT = "Developer Agent"
    COMMUNITY_MANAGER_AGENT = "Community Manager Agent"

class Agent(ABC):
    name: AgentName

    def get_node(self) -> functools.partial:
        raise NotImplementedError