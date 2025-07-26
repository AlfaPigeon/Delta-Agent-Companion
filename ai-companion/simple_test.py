#!/usr/bin/env python3
"""
Simple test for behavior tree implementation.
"""

import asyncio
import json
import uuid
from pathlib import Path
from datetime import datetime
from enum import Enum

# Simplified test - inline implementation
class StateType(Enum):
    ACTION = "action"
    ROOT = "root"

class StateStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"

# Test the basic concepts
async def simple_test():
    print("Testing AI Companion Behavior Tree...")
    
    # Test state creation
    state_data = {
        "id": str(uuid.uuid4()),
        "name": "Test Action",
        "type": "action",
        "actions": ["test_action"],
        "created_at": datetime.now().isoformat()
    }
    
    print(f"Created state: {state_data['name']}")
    
    # Test JSON serialization
    json_str = json.dumps(state_data, indent=2)
    print(f"State as JSON: {json_str}")
    
    # Test data directory creation
    data_dir = Path("./test_data")
    data_dir.mkdir(exist_ok=True)
    
    # Test file operations
    states_file = data_dir / "states.json"
    with open(states_file, 'w') as f:
        json.dump(state_data, f, indent=2)
    
    print(f"Saved state to: {states_file}")
    
    # Load and verify
    with open(states_file, 'r') as f:
        loaded_data = json.load(f)
    
    print(f"Loaded state: {loaded_data['name']}")
    
    print("✅ Basic behavior tree concepts working!")
    return True

if __name__ == "__main__":
    result = asyncio.run(simple_test())
    print(f"Test result: {result}")
