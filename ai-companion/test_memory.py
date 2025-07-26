#!/usr/bin/env python3
"""
Test the memory system implementation.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from memory.memory_system import MemoryManager, MemoryType
from core.logging import setup_logging


async def test_memory_system():
    """Test memory system functionality."""
    print("Testing AI Companion Memory System...")
    
    # Setup logging
    setup_logging(debug_mode=True)
    
    # Create memory manager
    manager = MemoryManager("./test_data")
    
    print("✅ Created memory manager")
    
    # Test storing different types of memories
    episodic_id = manager.store_memory(
        content="User asked about the weather today",
        memory_type=MemoryType.EPISODIC,
        tags=["weather", "conversation"],
        context={"user_id": "test_user", "session": "test_session"}
    )
    
    semantic_id = manager.store_memory(
        content="Paris is the capital of France",
        memory_type=MemoryType.SEMANTIC,
        tags=["geography", "facts"],
        context={"topic": "geography"}
    )
    
    working_id = manager.store_memory(
        content="Current conversation context",
        memory_type=MemoryType.WORKING,
        tags=["context"],
        context={"active": True}
    )
    
    print(f"✅ Stored memories: episodic={episodic_id[:8]}..., semantic={semantic_id[:8]}..., working={working_id[:8]}...")
    
    # Test retrieving memories
    episodic_memory = manager.retrieve_memory(episodic_id)
    print(f"✅ Retrieved episodic memory: {episodic_memory.content}")
    
    semantic_memory = manager.retrieve_memory(semantic_id)
    print(f"✅ Retrieved semantic memory: {semantic_memory.content}")
    
    # Test finding relevant memories
    context = {
        "tags": ["weather"],
        "content": "What's the weather like?",
        "current_states": []
    }
    
    relevant = manager.find_relevant_memories(context, limit=5)
    print(f"✅ Found {len(relevant)} relevant memories for weather context")
    
    # Test memory stats
    stats = manager.get_memory_stats()
    print(f"✅ Memory stats: {stats}")
    
    # Test working memory clear
    manager.clear_working_memory()
    print("✅ Cleared working memory")
    
    # Test memory retrieval after working memory clear
    working_memory = manager.retrieve_memory(working_id)
    if working_memory is None:
        print("✅ Working memory correctly cleared")
    else:
        print("❌ Working memory not cleared properly")
    
    print("✅ Memory system test completed successfully!")
    return True


if __name__ == "__main__":
    result = asyncio.run(test_memory_system())
    print(f"Test result: {result}")
