from develyn.agent.base import AgentName
from develyn.agent.community_manager_agent.agent import CommunityManagerAgent
from develyn.agent.qa_agent.agent import QAAgent
from develyn.agent.devrel_agent.devrel import DevrelAgent
from develyn.agent.developer_agent.agent import DeveloperAgent
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledGraph
from develyn.state import InboxState

def devrel_agent_fn(state: InboxState) -> AgentName:
    return state.next_step or AgentName.NONE

def get_graph() -> CompiledGraph:
    devrel_agent = DevrelAgent()
    communication_agent = CommunityManagerAgent()
    qa_agent = QAAgent()
    developer_agent = DeveloperAgent()
    graph = StateGraph(InboxState)
    graph.add_node(devrel_agent.name, devrel_agent.get_node())
    graph.add_node(communication_agent.name, communication_agent.get_node())
    graph.add_node(qa_agent.name, qa_agent.get_node())
    graph.add_node(developer_agent.name, developer_agent.get_node())

    graph.add_edge(START, devrel_agent.name)
    graph.add_conditional_edges(
        devrel_agent.name,
        devrel_agent_fn,
        {m.value: m.value if m!=AgentName.NONE else END for m in AgentName}
    )
    graph.add_edge(communication_agent.name, END)
    graph.add_edge(qa_agent.name, END)
    graph.add_edge(developer_agent.name, END)

    return graph.compile()