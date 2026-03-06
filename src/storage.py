"""
Persistent Storage Module

Provides file-based persistence for AI Founder OS data,
similar to OpenClaw's memory system.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Base directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SOULS_DIR = BASE_DIR / "souls"
MEMORY_DIR = BASE_DIR / "memory"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
SOULS_DIR.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)


class Storage:
    """File-based storage for AI Founder OS"""
    
    @staticmethod
    def save_json(filename: str, data: Any) -> bool:
        """Save data to JSON file"""
        try:
            filepath = DATA_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
    
    @staticmethod
    def load_json(filename: str, default: Any = None) -> Any:
        """Load data from JSON file"""
        try:
            filepath = DATA_DIR / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return default
    
    @staticmethod
    def save_soul(worker_id: str, soul_data: Dict) -> bool:
        """Save soul configuration for a worker"""
        try:
            filepath = SOULS_DIR / f"{worker_id}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(soul_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving soul for {worker_id}: {e}")
            return False
    
    @staticmethod
    def load_soul(worker_id: str) -> Optional[Dict]:
        """Load soul configuration for a worker"""
        try:
            filepath = SOULS_DIR / f"{worker_id}.json"
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading soul for {worker_id}: {e}")
            return None
    
    @staticmethod
    def list_souls() -> List[str]:
        """List all saved soul configurations"""
        try:
            return [f.stem for f in SOULS_DIR.glob("*.json")]
        except Exception as e:
            print(f"Error listing souls: {e}")
            return []
    
    @staticmethod
    def save_memory(date: str, content: str) -> bool:
        """Save daily memory/log"""
        try:
            filepath = MEMORY_DIR / f"{date}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving memory for {date}: {e}")
            return False
    
    @staticmethod
    def load_memory(date: str) -> Optional[str]:
        """Load daily memory/log"""
        try:
            filepath = MEMORY_DIR / f"{date}.md"
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error loading memory for {date}: {e}")
            return None
    
    @staticmethod
    def list_memories() -> List[str]:
        """List all memory dates"""
        try:
            return [f.stem for f in MEMORY_DIR.glob("*.md")]
        except Exception as e:
            print(f"Error listing memories: {e}")
            return []


# Default soul templates
DEFAULT_SOULS = {
    "planner": {
        "name": "Planner",
        "emoji": "🧠",
        "coreTruths": "Be genuinely helpful. Have opinions. Be resourceful before asking. Earn trust through competence.",
        "boundaries": "Private things stay private. When in doubt, ask. Never send half-baked replies.",
        "vibe": "Concise when needed, thorough when it matters. Not a corporate drone. Just good."
    },
    "builder": {
        "name": "Builder",
        "emoji": "🔨",
        "coreTruths": "Write clean code. Prioritize simplicity. Test everything.",
        "boundaries": "Never commit secrets. Validate inputs. Ask for clarification.",
        "vibe": "Get it done, get it right. Speed matters, correctness more."
    },
    "researcher": {
        "name": "Researcher",
        "emoji": "🔍",
        "coreTruths": "Find the truth. Verify sources. Stay objective.",
        "boundaries": "Cite sources. Don't make things up. Distinguish facts from opinions.",
        "vibe": "Thorough, accurate, skeptical of claims without evidence."
    },
    "verifier": {
        "name": "Verifier",
        "emoji": "✅",
        "coreTruths": "Test rigor prevents bugs. If it isn't tested, it's broken. Challenge assumptions.",
        "boundaries": "Don't approve weak code. Document failures clearly. Be firm but helpful.",
        "vibe": "Quality over speed. A good verifier asks hard questions."
    },
    "documenter": {
        "name": "Documenter",
        "emoji": "📝",
        "coreTruths": "Clear documentation saves time. Write for humans. Examples matter.",
        "boundaries": "Don't document obvious things. Keep docs in sync. Less is more.",
        "vibe": "Clarity is king. If you can't explain simply, you don't understand."
    },
    "evaluator": {
        "name": "Evaluator",
        "emoji": "📊",
        "coreTruths": "Data drives decisions. Measure what matters. Correlation isn't causation.",
        "boundaries": "Don't manipulate metrics. Report honestly even when it hurts.",
        "vibe": "Objective, metrics-driven, always questioning assumptions."
    }
}


def init_default_souls():
    """Initialize default soul configurations"""
    for worker_id, soul_data in DEFAULT_SOULS.items():
        if not Storage.load_soul(worker_id):
            Storage.save_soul(worker_id, soul_data)
            print(f"Created default soul for {worker_id}")


if __name__ == "__main__":
    # Initialize
    init_default_souls()
    print(f"\nData directory: {DATA_DIR}")
    print(f"Souls directory: {SOULS_DIR}")
    print(f"Memory directory: {MEMORY_DIR}")
    print(f"\nSaved souls: {Storage.list_souls()}")
    print(f"Saved memories: {Storage.list_memories()}")
