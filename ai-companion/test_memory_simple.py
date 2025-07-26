#!/usr/bin/env python3
"""
Simple memory system test.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
import pickle

def test_memory_database():
    """Test memory database operations."""
    print("Testing Memory Database...")
    
    # Create test database
    test_db = Path("./test_data/test_memories.db")
    test_db.parent.mkdir(exist_ok=True)
    
    # Initialize database
    with sqlite3.connect(str(test_db)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content_data BLOB,
                type TEXT,
                importance REAL,
                timestamp TEXT,
                tags TEXT
            )
        """)
        conn.commit()
    
    print("✅ Database initialized")
    
    # Test storing memory
    memory_id = str(uuid.uuid4())
    content = "Test memory content about AI companion"
    content_data = pickle.dumps(content)
    
    with sqlite3.connect(str(test_db)) as conn:
        conn.execute("""
            INSERT INTO memories (id, content_data, type, importance, timestamp, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            memory_id,
            content_data,
            "episodic",
            0.8,
            datetime.now().isoformat(),
            json.dumps(["test", "ai"])
        ))
        conn.commit()
    
    print(f"✅ Stored memory: {memory_id[:8]}...")
    
    # Test retrieving memory
    with sqlite3.connect(str(test_db)) as conn:
        cursor = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        
        if row:
            retrieved_content = pickle.loads(row[1])
            print(f"✅ Retrieved memory: {retrieved_content}")
        else:
            print("❌ Failed to retrieve memory")
    
    # Test finding memories
    with sqlite3.connect(str(test_db)) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        print(f"✅ Total memories in database: {count}")
    
    # Test importance calculation
    importance_factors = {
        'recency': 0.9,
        'frequency': 0.5,
        'relevance': 0.7,
        'emotional': 0.6
    }
    
    weights = {'recency': 0.3, 'frequency': 0.2, 'relevance': 0.4, 'emotional': 0.1}
    calculated_importance = sum(importance_factors[k] * weights[k] for k in weights.keys())
    
    print(f"✅ Calculated importance score: {calculated_importance:.3f}")
    
    print("✅ Memory database test completed!")
    return True

if __name__ == "__main__":
    result = test_memory_database()
    print(f"Test result: {result}")
