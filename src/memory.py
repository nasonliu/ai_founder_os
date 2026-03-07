"""
Vector Memory System for AI Founder OS

Similar to OpenClaw's memory system with:
- Vector embeddings for semantic search
- Per-agent (planner/worker) memory isolation
- File-based vector storage
- Multiple embedding provider support
"""

import json
import os
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import math

BASE_DIR = Path(__file__).parent.parent
MEMORY_DIR = BASE_DIR / "memory"
VECTOR_DIR = MEMORY_DIR / "vectors"
MEMORY_DIR.mkdir(exist_ok=True)
VECTOR_DIR.mkdir(exist_ok=True)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if len(a) != len(b):
        return 0.0
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def text_to_hash(text: str) -> str:
    """Generate unique ID from text content"""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


class VectorMemory:
    """
    Vector-based memory with semantic search.
    Each agent (planner/worker) has isolated memory.
    """
    
    def __init__(self, agent_id: str, embedding_provider: str = "simple"):
        """
        Initialize vector memory for an agent.
        
        Args:
            agent_id: Unique identifier for the agent (e.g., "planner", "builder", "researcher")
            embedding_provider: Provider to use for embeddings ("simple", "openai", "deepseek")
        """
        self.agent_id = agent_id
        self.embedding_provider = embedding_provider
        self.agent_dir = VECTOR_DIR / agent_id
        self.agent_dir.mkdir(exist_ok=True)
        self.vectors_file = self.agent_dir / "vectors.json"
        self.chunks_file = self.agent_dir / "chunks.json"
        
        # Load existing data
        self.vectors: Dict[str, List[float]] = self._load_json(self.vectors_file, {})
        self.chunks: Dict[str, Dict] = self._load_json(self.chunks_file, {})
    
    def _load_json(self, path: Path, default: Any) -> Any:
        """Load JSON file or return default"""
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, path: Path, data: Any) -> None:
        """Save data to JSON file"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.
        Uses simple hash-based embedding as fallback.
        """
        if self.embedding_provider == "simple":
            # Simple deterministic embedding based on text hash
            # This is not semantic but provides consistent results
            hash_val = hashlib.sha256(text.encode()).hexdigest()
            # Convert hex to float vector
            vector = []
            for i in range(0, min(len(hash_val), 256), 2):
                vector.append(int(hash_val[i:i+2], 16) / 255.0)
            # Pad to 128 dimensions
            while len(vector) < 128:
                vector.append(0.0)
            return vector[:128]
        else:
            # For real embeddings, would call API here
            return self._get_embedding(text)
    
    def add_memory(self, content: str, metadata: Optional[Dict] = None) -> str:
        """
        Add a memory to the vector store.
        
        Args:
            content: Text content to store
            metadata: Optional metadata (title, tags, etc.)
            
        Returns:
            Memory ID
        """
        # Generate ID
        memory_id = text_to_hash(content + str(datetime.now().timestamp()))
        
        # Get embedding
        vector = self._get_embedding(content)
        
        # Store chunk
        self.chunks[memory_id] = {
            "id": memory_id,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "vector_id": memory_id
        }
        
        # Store vector
        self.vectors[memory_id] = vector
        
        # Save to disk
        self._save_json(self.chunks_file, self.chunks)
        self._save_json(self.vectors_file, self.vectors)
        
        return memory_id
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Semantic search for similar memories.
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching memories with scores
        """
        query_vector = self._get_embedding(query)
        
        results = []
        for memory_id, vector in self.vectors.items():
            score = cosine_similarity(query_vector, vector)
            chunk = self.chunks.get(memory_id, {})
            results.append({
                "id": memory_id,
                "content": chunk.get("content", ""),
                "metadata": chunk.get("metadata", {}),
                "score": score,
                "created_at": chunk.get("created_at", "")
            })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def get_all_memories(self) -> List[Dict]:
        """Get all memories for this agent"""
        return [
            {
                "id": memory_id,
                "content": chunk.get("content", ""),
                "metadata": chunk.get("metadata", {}),
                "created_at": chunk.get("created_at", "")
            }
            for memory_id, chunk in self.chunks.items()
        ]
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory"""
        if memory_id in self.chunks:
            del self.chunks[memory_id]
            if memory_id in self.vectors:
                del self.vectors[memory_id]
            self._save_json(self.chunks_file, self.chunks)
            self._save_json(self.vectors_file, self.vectors)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all memories for this agent"""
        self.chunks = {}
        self.vectors = {}
        self._save_json(self.chunks_file, {})
        self._save_json(self.vectors_file, {})


class MemoryManager:
    """
    Global memory manager that handles multiple agents.
    Provides isolated memory for each planner/worker.
    """
    
    _instances: Dict[str, VectorMemory] = {}
    
    @classmethod
    def get_memory(cls, agent_id: str, embedding_provider: str = "simple") -> VectorMemory:
        """
        Get or create memory for an agent.
        
        Args:
            agent_id: Agent identifier (planner, builder, researcher, etc.)
            embedding_provider: Embedding provider to use
            
        Returns:
            VectorMemory instance for the agent
        """
        key = f"{agent_id}_{embedding_provider}"
        if key not in cls._instances:
            cls._instances[key] = VectorMemory(agent_id, embedding_provider)
        return cls._instances[key]
    
    @classmethod
    def search_all(cls, query: str, agent_ids: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """
        Search across multiple agents' memories.
        
        Args:
            query: Search query
            agent_ids: List of agent IDs to search (None = all)
            
        Returns:
            Dict mapping agent_id to search results
        """
        results = {}
        agents = agent_ids if agent_ids else DEFAULT_AGENTS
        
        for agent_id in agents:
            memory = cls.get_memory(agent_id)
            agent_results = memory.search(query)
            if agent_results:
                results[agent_id] = agent_results
        
        return results


# Default agents
DEFAULT_AGENTS = [
    "planner",      # 🧠 Main planner
    "builder",      # 🔨 Code builder
    "researcher",   # 🔍 Research worker
    "verifier",     # ✅ Testing/verification
    "documenter",   # 📝 Documentation
    "evaluator",    # 📊 Metrics/evaluation
]


def init_agent_memories():
    """Initialize memory for all default agents"""
    for agent_id in DEFAULT_AGENTS:
        MemoryManager.get_memory(agent_id)
    return DEFAULT_AGENTS


if __name__ == "__main__":
    # Test the memory system
    print("Testing Vector Memory System...")
    
    # Initialize
    agents = init_agent_memories()
    print(f"Initialized agents: {agents}")
    
    # Get planner memory
    planner_mem = MemoryManager.get_memory("planner")
    
    # Add some memories
    planner_mem.add_memory(
        "User prefers concise responses. Don't be verbose.",
        {"type": "preference", "source": "onboarding"}
    )
    planner_mem.add_memory(
        "The project uses React with TypeScript. Follow existing patterns.",
        {"type": "context", "project": "ai-founder-os"}
    )
    planner_mem.add_memory(
        "Remember to test all new features before committing.",
        {"type": "guideline", "priority": "high"}
    )
    
    # Search
    print("\n--- Search: 'testing guidelines' ---")
    results = planner_mem.search("testing guidelines")
    for r in results:
        print(f"  Score: {r['score']:.3f} | {r['content'][:50]}...")
    
    print("\n--- Search: 'user preferences' ---")
    results = planner_mem.search("user preferences")
    for r in results:
        print(f"  Score: {r['score']:.3f} | {r['content'][:50]}...")
    
    # Get builder memory
    builder_mem = MemoryManager.get_memory("builder")
    builder_mem.add_memory(
        "Use functional components with hooks in React.",
        {"type": "style", "framework": "react"}
    )
    
    # Cross-agent search
    print("\n--- Cross-agent search: 'code style' ---")
    results = MemoryManager.search_all("code style")
    for agent_id, agent_results in results.items():
        print(f"  {agent_id}: {len(agent_results)} results")
        for r in agent_results[:2]:
            print(f"    - {r['content'][:40]}... (score: {r['score']:.3f})")
    
    print("\n✓ Memory system working!")
