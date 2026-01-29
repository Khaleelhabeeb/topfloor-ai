"""
Agent Collaboration - Patterns for agent-to-agent communication
"""

from typing import Dict, Any, Optional, List
from enum import Enum


class CollaborationPattern(str, Enum):
    """Types of collaboration patterns between agents"""
    SEQUENTIAL = "sequential"  # One agent after another
    PARALLEL = "parallel"      # Multiple agents simultaneously
    HIERARCHICAL = "hierarchical"  # Parent delegates to children
    PEER_TO_PEER = "peer_to_peer"  # Agents communicate directly


class AgentTransfer:
    """
    Represents a transfer from one agent to another.
    
    Used for tracking agent delegation and routing decisions.
    """
    
    def __init__(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize agent transfer.
        
        Args:
            from_agent: Name of agent initiating transfer
            to_agent: Name of target agent
            reason: Reason for transfer
            context: Optional context to pass to target agent
        """
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.reason = reason
        self.context = context or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "reason": self.reason,
            "context": self.context
        }


class CollaborationContext:
    """
    Manages context sharing between agents during collaboration.
    
    Ensures agents have access to relevant information from previous
    agent interactions without exposing everything.
    """
    
    def __init__(self):
        """Initialize collaboration context"""
        self.transfers: List[AgentTransfer] = []
        self.shared_data: Dict[str, Any] = {}
        self.agent_outputs: Dict[str, Any] = {}  # agent_name -> output
    
    def add_transfer(self, transfer: AgentTransfer):
        """
        Record an agent transfer.
        
        Args:
            transfer: AgentTransfer instance
        """
        self.transfers.append(transfer)
    
    def get_transfer_chain(self) -> List[str]:
        """
        Get the chain of agent transfers.
        
        Returns:
            List of agent names in transfer order
        """
        chain = []
        for transfer in self.transfers:
            if not chain or chain[-1] != transfer.from_agent:
                chain.append(transfer.from_agent)
            chain.append(transfer.to_agent)
        return chain
    
    def set_shared_data(self, key: str, value: Any):
        """
        Set shared data accessible to all agents.
        
        Args:
            key: Data key
            value: Data value
        """
        self.shared_data[key] = value
    
    def get_shared_data(self, key: str, default: Any = None) -> Any:
        """
        Get shared data.
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Data value or default
        """
        return self.shared_data.get(key, default)
    
    def set_agent_output(self, agent_name: str, output: Any):
        """
        Store output from an agent.
        
        Args:
            agent_name: Name of agent
            output: Agent's output
        """
        self.agent_outputs[agent_name] = output
    
    def get_agent_output(self, agent_name: str) -> Optional[Any]:
        """
        Get output from a specific agent.
        
        Args:
            agent_name: Name of agent
            
        Returns:
            Agent output or None if not found
        """
        return self.agent_outputs.get(agent_name)
    
    def get_all_agent_outputs(self) -> Dict[str, Any]:
        """
        Get outputs from all agents.
        
        Returns:
            Dictionary of agent_name -> output
        """
        return self.agent_outputs.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "transfers": [t.to_dict() for t in self.transfers],
            "transfer_chain": self.get_transfer_chain(),
            "shared_data": self.shared_data,
            "agent_outputs": self.agent_outputs
        }


class WorkflowCoordinator:
    """
    Coordinates multi-agent workflows.
    
    Handles different collaboration patterns and ensures proper
    context passing between agents.
    """
    
    @staticmethod
    def create_sequential_workflow(
        agents: List[str],
        initial_context: Optional[Dict[str, Any]] = None
    ) -> CollaborationContext:
        """
        Create a sequential workflow where agents execute one after another.
        
        Args:
            agents: List of agent names in execution order
            initial_context: Optional initial context
            
        Returns:
            CollaborationContext for the workflow
        """
        context = CollaborationContext()
        
        if initial_context:
            for key, value in initial_context.items():
                context.set_shared_data(key, value)
        
        # Set up transfer chain
        for i in range(len(agents) - 1):
            transfer = AgentTransfer(
                from_agent=agents[i],
                to_agent=agents[i + 1],
                reason="sequential_workflow"
            )
            context.add_transfer(transfer)
        
        return context
    
    @staticmethod
    def create_parallel_workflow(
        agents: List[str],
        coordinator: str = "orchestrator",
        initial_context: Optional[Dict[str, Any]] = None
    ) -> CollaborationContext:
        """
        Create a parallel workflow where multiple agents execute simultaneously.
        
        Args:
            agents: List of agent names to execute in parallel
            coordinator: Name of coordinating agent
            initial_context: Optional initial context
            
        Returns:
            CollaborationContext for the workflow
        """
        context = CollaborationContext()
        
        if initial_context:
            for key, value in initial_context.items():
                context.set_shared_data(key, value)
        
        # Set up parallel transfers from coordinator
        for agent in agents:
            transfer = AgentTransfer(
                from_agent=coordinator,
                to_agent=agent,
                reason="parallel_workflow"
            )
            context.add_transfer(transfer)
        
        return context
    
    @staticmethod
    def merge_agent_results(
        context: CollaborationContext,
        merge_strategy: str = "combine"
    ) -> Dict[str, Any]:
        """
        Merge results from multiple agents.
        
        Args:
            context: CollaborationContext with agent outputs
            merge_strategy: Strategy for merging ("combine", "prioritize_first", "prioritize_last")
            
        Returns:
            Merged results dictionary
        """
        outputs = context.get_all_agent_outputs()
        
        if merge_strategy == "combine":
            # Combine all outputs
            merged = {
                "agents": list(outputs.keys()),
                "results": outputs,
                "transfer_chain": context.get_transfer_chain()
            }
        elif merge_strategy == "prioritize_first":
            # Use first agent's output as primary
            chain = context.get_transfer_chain()
            if chain:
                first_agent = chain[0]
                merged = {
                    "primary_agent": first_agent,
                    "primary_result": outputs.get(first_agent),
                    "supporting_results": {k: v for k, v in outputs.items() if k != first_agent}
                }
            else:
                merged = {"results": outputs}
        elif merge_strategy == "prioritize_last":
            # Use last agent's output as primary
            chain = context.get_transfer_chain()
            if chain:
                last_agent = chain[-1]
                merged = {
                    "primary_agent": last_agent,
                    "primary_result": outputs.get(last_agent),
                    "supporting_results": {k: v for k, v in outputs.items() if k != last_agent}
                }
            else:
                merged = {"results": outputs}
        else:
            merged = {"results": outputs}
        
        return merged
