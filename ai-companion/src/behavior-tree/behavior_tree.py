"""
Behavior Tree State Machine for AI Companion.
Implements dynamic behavior trees with LLM-driven state modification.
"""

import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path

from ..core.logging import get_logger, time_operation
from ..core.exceptions import BehaviorTreeError, ValidationError


class StateType(Enum):
    """Types of behavior tree states."""
    ACTION = "action"
    CONDITION = "condition" 
    COMPOSITE = "composite"
    ROOT = "root"


class StateStatus(Enum):
    """Status of state execution."""
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    IDLE = "idle"


@dataclass
class StateMetadata:
    """Metadata for behavior tree states."""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    average_duration: float = 0.0
    tags: List[str] = field(default_factory=list)


@dataclass
class StateDefinition:
    """Definition of a behavior tree state."""
    id: str
    name: str
    type: StateType
    priority: int = 5
    conditions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    metadata: StateMetadata = field(default_factory=StateMetadata)
    timeout_seconds: int = 300
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "priority": self.priority,
            "conditions": self.conditions,
            "actions": self.actions,
            "children": self.children,
            "timeout_seconds": self.timeout_seconds,
            "metadata": {
                "created_at": self.metadata.created_at.isoformat(),
                "modified_at": self.metadata.modified_at.isoformat(),
                "created_by": self.metadata.created_by,
                "execution_count": self.metadata.execution_count,
                "last_execution": self.metadata.last_execution.isoformat() if self.metadata.last_execution else None,
                "average_duration": self.metadata.average_duration,
                "tags": self.metadata.tags
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StateDefinition':
        """Create from dictionary."""
        metadata_data = data.get("metadata", {})
        metadata = StateMetadata(
            created_at=datetime.fromisoformat(metadata_data.get("created_at", datetime.now().isoformat())),
            modified_at=datetime.fromisoformat(metadata_data.get("modified_at", datetime.now().isoformat())),
            created_by=metadata_data.get("created_by", "system"),
            execution_count=metadata_data.get("execution_count", 0),
            last_execution=datetime.fromisoformat(metadata_data["last_execution"]) if metadata_data.get("last_execution") else None,
            average_duration=metadata_data.get("average_duration", 0.0),
            tags=metadata_data.get("tags", [])
        )
        
        return cls(
            id=data["id"],
            name=data["name"],
            type=StateType(data["type"]),
            priority=data.get("priority", 5),
            conditions=data.get("conditions", []),
            actions=data.get("actions", []),
            children=data.get("children", []),
            metadata=metadata,
            timeout_seconds=data.get("timeout_seconds", 300)
        )


class BehaviorState(ABC):
    """Abstract base class for behavior tree states."""
    
    def __init__(self, definition: StateDefinition):
        self.definition = definition
        self.status = StateStatus.IDLE
        self.start_time: Optional[datetime] = None
        self.children: List['BehaviorState'] = []
        self.logger = get_logger()
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> StateStatus:
        """Execute the state logic."""
        pass
    
    def can_execute(self, context: Dict[str, Any]) -> bool:
        """Check if state can execute based on conditions."""
        for condition in self.definition.conditions:
            if not self._evaluate_condition(condition, context):
                return False
        return True
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition string."""
        # Simple condition evaluation - can be enhanced with proper parser
        try:
            # Replace context variables in condition
            for key, value in context.items():
                condition = condition.replace(f"{{{key}}}", str(value))
            
            # Evaluate as Python expression (be careful in production!)
            return eval(condition)
        except Exception as e:
            self.logger.warning(f"Failed to evaluate condition '{condition}': {e}")
            return False
    
    def add_child(self, child: 'BehaviorState'):
        """Add a child state."""
        self.children.append(child)
    
    def remove_child(self, child_id: str):
        """Remove a child state by ID."""
        self.children = [child for child in self.children if child.definition.id != child_id]
    
    def is_timed_out(self) -> bool:
        """Check if state execution has timed out."""
        if not self.start_time:
            return False
        
        elapsed = datetime.now() - self.start_time
        return elapsed.total_seconds() > self.definition.timeout_seconds


class ActionState(BehaviorState):
    """State that performs actions."""
    
    async def execute(self, context: Dict[str, Any]) -> StateStatus:
        """Execute actions."""
        if not self.can_execute(context):
            return StateStatus.FAILURE
        
        self.status = StateStatus.RUNNING
        self.start_time = datetime.now()
        
        try:
            # Execute each action
            for action in self.definition.actions:
                success = await self._execute_action(action, context)
                if not success:
                    self.status = StateStatus.FAILURE
                    return self.status
                
                # Check for timeout
                if self.is_timed_out():
                    self.status = StateStatus.FAILURE
                    return self.status
            
            self.status = StateStatus.SUCCESS
            return self.status
            
        except Exception as e:
            self.logger.error(f"Action execution failed: {e}", state_id=self.definition.id)
            self.status = StateStatus.FAILURE
            return self.status
    
    async def _execute_action(self, action: str, context: Dict[str, Any]) -> bool:
        """Execute a single action."""
        # Action execution logic - integrate with tool system
        self.logger.debug(f"Executing action: {action}", state_id=self.definition.id)
        return True  # Placeholder


class ConditionState(BehaviorState):
    """State that checks conditions."""
    
    async def execute(self, context: Dict[str, Any]) -> StateStatus:
        """Check conditions."""
        self.status = StateStatus.RUNNING
        self.start_time = datetime.now()
        
        if self.can_execute(context):
            self.status = StateStatus.SUCCESS
        else:
            self.status = StateStatus.FAILURE
        
        return self.status


class CompositeState(BehaviorState):
    """State that manages child states."""
    
    async def execute(self, context: Dict[str, Any]) -> StateStatus:
        """Execute child states based on composite logic."""
        if not self.can_execute(context):
            return StateStatus.FAILURE
        
        self.status = StateStatus.RUNNING
        self.start_time = datetime.now()
        
        # Sort children by priority
        sorted_children = sorted(self.children, key=lambda x: x.definition.priority, reverse=True)
        
        # Execute children (sequence behavior by default)
        for child in sorted_children:
            if self.is_timed_out():
                self.status = StateStatus.FAILURE
                return self.status
            
            child_status = await child.execute(context)
            
            if child_status == StateStatus.FAILURE:
                self.status = StateStatus.FAILURE
                return self.status
            elif child_status == StateStatus.RUNNING:
                self.status = StateStatus.RUNNING
                return self.status
        
        self.status = StateStatus.SUCCESS
        return self.status


class RootState(CompositeState):
    """Special root state that cannot be removed."""
    
    def __init__(self):
        definition = StateDefinition(
            id="root",
            name="Root State",
            type=StateType.ROOT,
            priority=10
        )
        super().__init__(definition)


class StateFactory:
    """Factory for creating behavior states."""
    
    @staticmethod
    def create_state(definition: StateDefinition) -> BehaviorState:
        """Create a state based on its definition."""
        if definition.type == StateType.ACTION:
            return ActionState(definition)
        elif definition.type == StateType.CONDITION:
            return ConditionState(definition)
        elif definition.type == StateType.COMPOSITE:
            return CompositeState(definition)
        elif definition.type == StateType.ROOT:
            return RootState()
        else:
            raise BehaviorTreeError(f"Unknown state type: {definition.type}")


class BehaviorTreeManager:
    """Manages the dynamic behavior tree."""
    
    def __init__(self, data_directory: str = "./data"):
        self.data_dir = Path(data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.states_file = self.data_dir / "behavior_states.json"
        
        self.states: Dict[str, BehaviorState] = {}
        self.root_state = RootState()
        self.states["root"] = self.root_state
        
        self.logger = get_logger()
        self.modification_cooldown = timedelta(seconds=60)
        self.last_modification = datetime.min
        
        # Load existing states
        self.load_states()
    
    def add_state(self, definition: StateDefinition, parent_id: str = "root") -> bool:
        """Add a new state to the tree."""
        if definition.id in self.states:
            raise BehaviorTreeError(f"State with ID '{definition.id}' already exists")
        
        if parent_id not in self.states:
            raise BehaviorTreeError(f"Parent state '{parent_id}' not found")
        
        # Create and add state
        state = StateFactory.create_state(definition)
        self.states[definition.id] = state
        
        # Add to parent
        parent_state = self.states[parent_id]
        parent_state.add_child(state)
        
        # Update parent's children list
        if definition.id not in parent_state.definition.children:
            parent_state.definition.children.append(definition.id)
        
        self.logger.log_behavior_tree_modification("add_state", definition.id, parent_id=parent_id)
        self.save_states()
        return True
    
    def remove_state(self, state_id: str) -> bool:
        """Remove a state from the tree."""
        if state_id == "root":
            raise BehaviorTreeError("Cannot remove root state")
        
        if state_id not in self.states:
            raise BehaviorTreeError(f"State '{state_id}' not found")
        
        # Remove from all parents
        for state in self.states.values():
            if state_id in state.definition.children:
                state.definition.children.remove(state_id)
                state.remove_child(state_id)
        
        # Remove state
        del self.states[state_id]
        
        self.logger.log_behavior_tree_modification("remove_state", state_id)
        self.save_states()
        return True
    
    def modify_state(self, state_id: str, updates: Dict[str, Any]) -> bool:
        """Modify an existing state."""
        if state_id not in self.states:
            raise BehaviorTreeError(f"State '{state_id}' not found")
        
        # Check cooldown
        if datetime.now() - self.last_modification < self.modification_cooldown:
            raise BehaviorTreeError("Modification cooldown active")
        
        # Create backup
        backup = self.create_backup()
        
        try:
            state = self.states[state_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(state.definition, key):
                    setattr(state.definition, key, value)
            
            # Update modification timestamp
            state.definition.metadata.modified_at = datetime.now()
            self.last_modification = datetime.now()
            
            # Validate tree integrity
            if not self.validate_tree():
                self.restore_backup(backup)
                return False
            
            self.logger.log_behavior_tree_modification("modify_state", state_id, updates=updates)
            self.save_states()
            return True
            
        except Exception as e:
            self.restore_backup(backup)
            self.logger.error(f"State modification failed: {e}", state_id=state_id)
            return False
    
    @time_operation("behavior_tree_execution")
    async def execute_tree(self, context: Dict[str, Any]) -> StateStatus:
        """Execute the behavior tree."""
        return await self.root_state.execute(context)
    
    def validate_tree(self) -> bool:
        """Validate tree structure and integrity."""
        try:
            # Check for cycles
            visited = set()
            
            def check_cycles(state_id: str, path: set):
                if state_id in path:
                    return False  # Cycle detected
                if state_id in visited:
                    return True  # Already validated
                
                visited.add(state_id)
                path.add(state_id)
                
                state = self.states.get(state_id)
                if not state:
                    return False
                
                for child_id in state.definition.children:
                    if not check_cycles(child_id, path.copy()):
                        return False
                
                return True
            
            return check_cycles("root", set())
            
        except Exception as e:
            self.logger.error(f"Tree validation failed: {e}")
            return False
    
    def create_backup(self) -> Dict[str, Any]:
        """Create a backup of current state."""
        return {
            state_id: state.definition.to_dict()
            for state_id, state in self.states.items()
        }
    
    def restore_backup(self, backup: Dict[str, Any]):
        """Restore from backup."""
        self.states.clear()
        
        for state_id, state_data in backup.items():
            definition = StateDefinition.from_dict(state_data)
            state = StateFactory.create_state(definition)
            self.states[state_id] = state
        
        # Rebuild tree structure
        self._rebuild_tree_structure()
    
    def _rebuild_tree_structure(self):
        """Rebuild parent-child relationships."""
        for state in self.states.values():
            state.children.clear()
        
        for state in self.states.values():
            for child_id in state.definition.children:
                if child_id in self.states:
                    state.add_child(self.states[child_id])
    
    def save_states(self):
        """Save states to file."""
        state_data = {
            state_id: state.definition.to_dict()
            for state_id, state in self.states.items()
        }
        
        with open(self.states_file, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def load_states(self):
        """Load states from file."""
        if not self.states_file.exists():
            return
        
        try:
            with open(self.states_file, 'r') as f:
                state_data = json.load(f)
            
            for state_id, data in state_data.items():
                if state_id == "root":
                    continue  # Root already exists
                
                definition = StateDefinition.from_dict(data)
                state = StateFactory.create_state(definition)
                self.states[state_id] = state
            
            # Rebuild tree structure
            self._rebuild_tree_structure()
            
        except Exception as e:
            self.logger.error(f"Failed to load states: {e}")
    
    def get_state_info(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a state."""
        if state_id not in self.states:
            return None
        
        state = self.states[state_id]
        return {
            "definition": state.definition.to_dict(),
            "status": state.status.value,
            "children_count": len(state.children)
        }
    
    def list_states(self) -> List[Dict[str, Any]]:
        """List all states."""
        return [self.get_state_info(state_id) for state_id in self.states.keys()]
