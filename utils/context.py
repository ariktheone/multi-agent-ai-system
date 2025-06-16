from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class AgentContext:
    goal: str
    start_time: float
    entities: List[str] = field(default_factory=list)
    entity_key: str = "general"
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    agent_chain: List[str] = field(default_factory=list)
    processing_time: float = 0.0

    def update(self, updates: dict):
        self.data.update(updates)