"""
Memory System for AI Companion.
Implements episodic, semantic, working, and procedural memory with importance scoring.
"""

import sqlite3
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import pickle
import asyncio
from collections import defaultdict

from ..core.logging import get_logger, time_operation
from ..core.exceptions import MemoryError


class MemoryType(Enum):
    """Types of memory."""
    EPISODIC = "episodic"      # Event-based memories with temporal context
    SEMANTIC = "semantic"      # Factual information and learned patterns  
    WORKING = "working"        # Active context and immediate processing data
    PROCEDURAL = "procedural"  # Tool usage patterns and behavioral sequences


@dataclass
class Memory:
    """Core memory structure."""
    id: str
    content: Any
    type: MemoryType
    importance: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    associated_states: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type.value,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "associated_states": self.associated_states,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "tags": self.tags,
            "context": self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create memory from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            type=MemoryType(data["type"]),
            importance=data.get("importance", 0.5),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            associated_states=data.get("associated_states", []),
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None,
            tags=data.get("tags", []),
            context=data.get("context", {})
        )


class MemoryStorage:
    """Handles memory persistence using SQLite."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = get_logger()
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content_hash TEXT,
                    content_data BLOB,
                    type TEXT,
                    importance REAL,
                    timestamp TEXT,
                    associated_states TEXT,
                    access_count INTEGER,
                    last_accessed TEXT,
                    tags TEXT,
                    context TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_type ON memories(type)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
            """)
            
            conn.commit()
    
    def store_memory(self, memory: Memory) -> bool:
        """Store a memory in the database."""
        try:
            # Serialize content
            content_data = pickle.dumps(memory.content)
            content_hash = hashlib.md5(content_data).hexdigest()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories 
                    (id, content_hash, content_data, type, importance, timestamp, 
                     associated_states, access_count, last_accessed, tags, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory.id,
                    content_hash,
                    content_data,
                    memory.type.value,
                    memory.importance,
                    memory.timestamp.isoformat(),
                    json.dumps(memory.associated_states),
                    memory.access_count,
                    memory.last_accessed.isoformat() if memory.last_accessed else None,
                    json.dumps(memory.tags),
                    json.dumps(memory.context)
                ))
                conn.commit()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}", memory_id=memory.id)
            return False
    
    def retrieve_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT * FROM memories WHERE id = ?", (memory_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Deserialize content
                content = pickle.loads(row[2])
                
                return Memory(
                    id=row[0],
                    content=content,
                    type=MemoryType(row[3]),
                    importance=row[4],
                    timestamp=datetime.fromisoformat(row[5]),
                    associated_states=json.loads(row[6]),
                    access_count=row[7],
                    last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
                    tags=json.loads(row[9]),
                    context=json.loads(row[10])
                )
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve memory: {e}", memory_id=memory_id)
            return None
    
    def find_memories(self, 
                     memory_type: Optional[MemoryType] = None,
                     min_importance: float = 0.0,
                     limit: int = 100,
                     tags: Optional[List[str]] = None) -> List[Memory]:
        """Find memories matching criteria."""
        try:
            query = "SELECT * FROM memories WHERE importance >= ?"
            params = [min_importance]
            
            if memory_type:
                query += " AND type = ?"
                params.append(memory_type.value)
            
            query += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
            params.append(limit)
            
            memories = []
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                
                for row in cursor.fetchall():
                    try:
                        content = pickle.loads(row[2])
                        memory = Memory(
                            id=row[0],
                            content=content,
                            type=MemoryType(row[3]),
                            importance=row[4],
                            timestamp=datetime.fromisoformat(row[5]),
                            associated_states=json.loads(row[6]),
                            access_count=row[7],
                            last_accessed=datetime.fromisoformat(row[8]) if row[8] else None,
                            tags=json.loads(row[9]),
                            context=json.loads(row[10])
                        )
                        
                        # Filter by tags if specified
                        if tags and not any(tag in memory.tags for tag in tags):
                            continue
                        
                        memories.append(memory)
                        
                    except Exception as e:
                        self.logger.warning(f"Failed to deserialize memory {row[0]}: {e}")
                        continue
            
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed to find memories: {e}")
            return []
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete memory: {e}", memory_id=memory_id)
            return False
    
    def get_memory_count(self) -> int:
        """Get total memory count."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM memories")
                return cursor.fetchone()[0]
        except Exception:
            return 0


class ImportanceCalculator:
    """Calculates and updates memory importance scores."""
    
    def __init__(self, decay_rate: float = 0.1):
        self.decay_rate = decay_rate
        self.logger = get_logger()
    
    def calculate_importance(self, memory: Memory, context: Dict[str, Any]) -> float:
        """Calculate importance score for a memory."""
        factors = {}
        
        # Recency factor (more recent = more important)
        time_diff = datetime.now() - memory.timestamp
        recency_score = max(0.1, 1.0 - (time_diff.total_seconds() / (30 * 24 * 3600)))  # 30 days decay
        factors['recency'] = recency_score
        
        # Frequency factor (more accessed = more important)
        frequency_score = min(1.0, memory.access_count / 10.0)  # Cap at 10 accesses
        factors['frequency'] = frequency_score
        
        # Context relevance (how relevant to current context)
        relevance_score = self._calculate_relevance(memory, context)
        factors['relevance'] = relevance_score
        
        # Emotional weight (extracted from content)
        emotional_score = self._extract_emotional_weight(memory)
        factors['emotional'] = emotional_score
        
        # State association (associated with more states = more important)
        state_score = min(1.0, len(memory.associated_states) * 0.2)
        factors['state_association'] = state_score
        
        # Weighted average
        weights = {
            'recency': 0.3,
            'frequency': 0.2, 
            'relevance': 0.3,
            'emotional': 0.1,
            'state_association': 0.1
        }
        
        weighted_score = sum(factors[key] * weights[key] for key in weights.keys())
        return max(0.0, min(1.0, weighted_score))
    
    def _calculate_relevance(self, memory: Memory, context: Dict[str, Any]) -> float:
        """Calculate relevance to current context."""
        relevance = 0.0
        
        # Check tag overlap
        context_tags = context.get('tags', [])
        if context_tags and memory.tags:
            tag_overlap = len(set(context_tags) & set(memory.tags))
            relevance += tag_overlap / max(len(context_tags), len(memory.tags))
        
        # Check state overlap
        current_states = context.get('current_states', [])
        if current_states and memory.associated_states:
            state_overlap = len(set(current_states) & set(memory.associated_states))
            relevance += state_overlap / max(len(current_states), len(memory.associated_states))
        
        # Content similarity (simplified - could use embeddings)
        current_content = context.get('content', '')
        if current_content and isinstance(memory.content, str):
            # Simple word overlap
            current_words = set(current_content.lower().split())
            memory_words = set(memory.content.lower().split())
            if current_words and memory_words:
                word_overlap = len(current_words & memory_words)
                relevance += word_overlap / max(len(current_words), len(memory_words))
        
        return min(1.0, relevance)
    
    def _extract_emotional_weight(self, memory: Memory) -> float:
        """Extract emotional weight from memory content."""
        # Simplified emotional analysis
        if not isinstance(memory.content, str):
            return 0.5
        
        content = memory.content.lower()
        
        # Positive emotions
        positive_words = ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing']
        positive_count = sum(1 for word in positive_words if word in content)
        
        # Negative emotions  
        negative_words = ['sad', 'angry', 'frustrated', 'terrible', 'awful', 'hate']
        negative_count = sum(1 for word in negative_words if word in content)
        
        # Important markers
        important_words = ['important', 'critical', 'urgent', 'remember', 'key']
        important_count = sum(1 for word in important_words if word in content)
        
        # Calculate emotional weight
        emotional_weight = 0.5  # Neutral baseline
        emotional_weight += (positive_count + negative_count + important_count) * 0.1
        
        return min(1.0, max(0.0, emotional_weight))


class MemoryManager:
    """Main memory management system."""
    
    def __init__(self, data_directory: str = "./data", max_memories: int = 10000):
        self.data_dir = Path(data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.storage = MemoryStorage(str(self.data_dir / "memories.db"))
        self.importance_calc = ImportanceCalculator()
        
        self.max_memories = max_memories
        self.logger = get_logger()
        
        # In-memory cache for working memory
        self.working_memory: Dict[str, Memory] = {}
    
    def store_memory(self, content: Any, memory_type: MemoryType, 
                    tags: Optional[List[str]] = None,
                    context: Optional[Dict[str, Any]] = None,
                    associated_states: Optional[List[str]] = None) -> str:
        """Store a new memory."""
        memory_id = str(uuid.uuid4())
        
        memory = Memory(
            id=memory_id,
            content=content,
            type=memory_type,
            tags=tags or [],
            context=context or {},
            associated_states=associated_states or []
        )
        
        # Calculate initial importance
        memory.importance = self.importance_calc.calculate_importance(memory, context or {})
        
        # Store based on type
        if memory_type == MemoryType.WORKING:
            self.working_memory[memory_id] = memory
        else:
            self.storage.store_memory(memory)
            self.logger.log_memory_operation("store", 1, memory_type=memory_type.value)
        
        # Check if we need to consolidate
        if self.storage.get_memory_count() > self.max_memories:
            asyncio.create_task(self._consolidate_memories())
        
        return memory_id
    
    def retrieve_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory and update access stats."""
        # Check working memory first
        if memory_id in self.working_memory:
            memory = self.working_memory[memory_id]
        else:
            memory = self.storage.retrieve_memory(memory_id)
        
        if memory:
            # Update access stats
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            
            # Recalculate importance
            memory.importance = self.importance_calc.calculate_importance(memory, {})
            
            # Update in storage
            if memory.type != MemoryType.WORKING:
                self.storage.store_memory(memory)
            
            self.logger.log_memory_operation("retrieve", 1, memory_id=memory_id)
        
        return memory
    
    def find_relevant_memories(self, context: Dict[str, Any], 
                             memory_types: Optional[List[MemoryType]] = None,
                             limit: int = 10) -> List[Memory]:
        """Find memories relevant to the current context."""
        relevant_memories = []
        
        types_to_search = memory_types or [MemoryType.EPISODIC, MemoryType.SEMANTIC, MemoryType.PROCEDURAL]
        
        for memory_type in types_to_search:
            if memory_type == MemoryType.WORKING:
                # Include working memory
                for memory in self.working_memory.values():
                    relevance = self.importance_calc._calculate_relevance(memory, context)
                    if relevance > 0.3:  # Threshold for relevance
                        relevant_memories.append(memory)
            else:
                # Search persistent storage
                memories = self.storage.find_memories(
                    memory_type=memory_type,
                    min_importance=0.3,
                    limit=limit
                )
                
                # Calculate relevance and filter
                for memory in memories:
                    relevance = self.importance_calc._calculate_relevance(memory, context)
                    if relevance > 0.3:
                        memory.importance = max(memory.importance, relevance)  # Boost importance
                        relevant_memories.append(memory)
        
        # Sort by importance and limit
        relevant_memories.sort(key=lambda m: m.importance, reverse=True)
        return relevant_memories[:limit]
    
    def clear_working_memory(self):
        """Clear working memory."""
        self.working_memory.clear()
        self.logger.log_memory_operation("clear_working", 0)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        stats = {
            'total_memories': self.storage.get_memory_count(),
            'working_memory_count': len(self.working_memory),
            'memory_types': {}
        }
        
        for memory_type in MemoryType:
            if memory_type == MemoryType.WORKING:
                count = len([m for m in self.working_memory.values() if m.type == memory_type])
            else:
                memories = self.storage.find_memories(memory_type=memory_type, limit=1000)
                count = len(memories)
            
            stats['memory_types'][memory_type.value] = count
        
        return stats
    
    async def _consolidate_memories(self):
        """Consolidate old memories to free up space."""
        self.logger.info("Starting memory consolidation")
        
        # Get old, low-importance memories
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # This is a simplified consolidation - in a full implementation,
        # you'd use LLM to merge related memories
        memories_to_remove = []
        
        for memory_type in [MemoryType.EPISODIC, MemoryType.SEMANTIC]:
            memories = self.storage.find_memories(memory_type=memory_type, limit=1000)
            
            for memory in memories:
                if (memory.timestamp < cutoff_date and 
                    memory.importance < 0.3 and 
                    memory.access_count < 2):
                    memories_to_remove.append(memory.id)
        
        # Remove low-value memories
        removed_count = 0
        for memory_id in memories_to_remove[:100]:  # Limit to 100 per consolidation
            if self.storage.delete_memory(memory_id):
                removed_count += 1
        
        self.logger.log_memory_operation("consolidate", removed_count)
        self.logger.info(f"Memory consolidation complete: removed {removed_count} memories")
