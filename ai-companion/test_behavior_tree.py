"""
Test the behavior tree implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path and import modules directly
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from behavior_tree.behavior_tree import BehaviorTreeManager, StateDefinition, StateType
from core.logging import setup_logging


async def test_behavior_tree():
    """Test basic behavior tree functionality."""
    # Setup logging
    setup_logging(debug_mode=True)
    
    # Create behavior tree manager
    manager = BehaviorTreeManager("./test_data")
    
    print("Created behavior tree manager")
    
    # Create a simple action state
    action_state = StateDefinition(
        id="test_action",
        name="Test Action",
        type=StateType.ACTION,
        actions=["print('Hello from behavior tree!')"],
        conditions=["True"]  # Always execute
    )
    
    # Add state to tree
    success = manager.add_state(action_state)
    print(f"Added action state: {success}")
    
    # List states
    states = manager.list_states()
    print(f"States in tree: {len(states)}")
    for state in states:
        print(f"  - {state['definition']['id']}: {state['definition']['name']}")
    
    # Execute tree
    context = {"test_var": "test_value"}
    result = await manager.execute_tree(context)
    print(f"Tree execution result: {result}")
    
    # Test state modification
    updates = {"name": "Modified Test Action"}
    success = manager.modify_state("test_action", updates)
    print(f"State modification: {success}")
    
    print("Behavior tree test completed!")


if __name__ == "__main__":
    asyncio.run(test_behavior_tree())
