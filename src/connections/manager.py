"""
AI Founder OS - Connection Manager Module

Manages external service connections including:
- LLM providers (OpenAI, Anthropic, DeepSeek, Ollama, vLLM)
- Search providers (Brave Search, SerpAPI, Tavily)
- Repository providers (GitHub, GitLab)
- OAuth services (Google Drive, Notion, Slack)

Key features:
- Unified credential management
- Capability tokenization
- Budget control
- Health monitoring
"""

import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import os


class ProviderType(Enum):
    """Supported provider types"""
    # LLM Providers
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    OLLAMA = "ollama"
    VLLM = "vllm"
    
    # Search Providers
    BRAVE_SEARCH = "brave_search"
    SERPAPI = "serpapi"
    TAVILY = "tavily"
    BING = "bing"
    
    # Repository Providers
    GITHUB = "github"
    GITLAB = "gitlab"
    
    # OAuth Services
    GOOGLE = "google"
    NOTION = "notion"
    SLACK = "slack"


class AuthType(Enum):
    """Authentication types"""
    API_KEY = "api_key"
    OAUTH = "oauth"
    LOCAL = "local"


class ConnectionStatus(Enum):
    """Connection status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    UNHEALTHY = "unhealthy"


class HealthStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class LocalModel:
    """Local model configuration"""
    name: str
    context_limit: int = 8192
    recommended_for: List[str] = field(default_factory=list)


@dataclass
class LocalConfig:
    """Local model runtime configuration"""
    endpoint: str
    models: List[LocalModel] = field(default_factory=list)
    concurrency_limit: int = 2


@dataclass
class OAuthConfig:
    """OAuth configuration"""
    client_id: str
    scopes: List[str] = field(default_factory=list)
    token_type: str = "bearer"


@dataclass
class Quota:
    """Quota tracking"""
    quota_type: str = "monthly"  # monthly, usage_based, rate_limit
    limit: str = "100"
    current: str = "0"
    reset_at: Optional[str] = None


@dataclass
class HealthCheck:
    """Health check configuration"""
    enabled: bool = True
    interval_minutes: int = 60
    last_check: Optional[str] = None
    status: str = "unknown"


@dataclass
class Credentials:
    """Encrypted credentials storage"""
    encrypted: bool = True
    storage: str = "keychain"  # keychain, vault, file
    key_ref: Optional[str] = None
    refresh_token_ref: Optional[str] = None


@dataclass
class Connection:
    """
    Connection data model representing an external service connection.
    """
    connection_id: str
    provider: str
    name: str
    auth_type: str
    created_at: str = ""
    updated_at: str = ""
    
    # Optional fields
    credentials: Optional[Credentials] = None
    scopes: List[str] = field(default_factory=list)
    quota: Optional[Quota] = None
    allowed_workers: List[str] = field(default_factory=list)
    allowed_projects: List[str] = field(default_factory=list)
    status: str = "active"
    expires_at: Optional[str] = None
    
    # OAuth specific
    oauth_config: Optional[OAuthConfig] = None
    
    # Local model specific
    local_config: Optional[LocalConfig] = None
    
    # Health check
    health_check: Optional[HealthCheck] = None
    
    # For tracking
    last_used: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            now = datetime.utcnow().isoformat() + "Z"
            self.created_at = now
            self.updated_at = now
        
        # Initialize defaults
        if self.quota is None:
            self.quota = Quota()
        if self.health_check is None:
            self.health_check = HealthCheck()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = {}
        for key, value in asdict(self).items():
            if isinstance(value, LocalModel):
                result[key] = asdict(value)
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Connection':
        """Create from dictionary"""
        # Handle nested objects
        if 'local_config' in data and data['local_config']:
            models = [LocalModel(**m) if isinstance(m, dict) else m 
                     for m in data['local_config'].get('models', [])]
            data['local_config'] = LocalConfig(
                endpoint=data['local_config'].get('endpoint', ''),
                models=models,
                concurrency_limit=data['local_config'].get('concurrency_limit', 2)
            )
        
        if 'oauth_config' in data and data['oauth_config']:
            data['oauth_config'] = OAuthConfig(**data['oauth_config'])
        
        if 'quota' in data and data['quota']:
            data['quota'] = Quota(**data['quota'])
        
        if 'health_check' in data and data['health_check']:
            data['health_check'] = HealthCheck(**data['health_check'])
        
        if 'credentials' in data and data['credentials']:
            data['credentials'] = Credentials(**data['credentials'])
        
        return cls(**data)
    
    def is_active(self) -> bool:
        """Check if connection is active"""
        return self.status == ConnectionStatus.ACTIVE.value
    
    def is_expired(self) -> bool:
        """Check if connection is expired"""
        if self.expires_at:
            try:
                expiry = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
                return datetime.now(expiry.tzinfo) > expiry
            except ValueError:
                return False
        return False


@dataclass
class CapabilityToken:
    """
    Capability token issued to workers for scoped access.
    Short-lived tokens that delegate connection access.
    """
    token_id: str
    connection_id: str
    issued_to: Dict[str, str]  # worker_id, task_id
    permissions: List[str] = field(default_factory=list)
    restrictions: Dict[str, Any] = field(default_factory=dict)
    issued_at: str = ""
    expires_at: str = ""
    status: str = "active"
    
    def __post_init__(self):
        if not self.issued_at:
            self.issued_at = datetime.utcnow().isoformat() + "Z"
        if not self.expires_at:
            # Default 15 minute expiry
            expiry = datetime.utcnow() + timedelta(minutes=15)
            self.expires_at = expiry.isoformat() + "Z"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CapabilityToken':
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        try:
            expiry = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
            return datetime.now(expiry.tzinfo) > expiry
        except ValueError:
            return True
    
    def is_valid(self) -> bool:
        """Check if token is valid"""
        return self.status == "active" and not self.is_expired()


# Permission type definitions
PERMISSION_TYPES = {
    "llm": ["llm.call", "llm.embeddings", "llm.batch"],
    "search": ["search.query", "search.fetch"],
    "github": [
        "github.repo.read", "github.repo.write", 
        "github.pr.create", "github.issue.write"
    ],
    "filesystem": ["fs.read", "fs.write"],
    "notion": ["notion.page.read", "notion.page.write"],
    "google": ["google.drive.read", "google.drive.write"],
    "slack": ["slack.message.send", "slack.channel.read"]
}

# Default routing rules by worker type
DEFAULT_ROUTING_RULES = {
    "builder": {
        "primary": "local_ollama:deepseek-8b",
        "fallback": "cloud_openai:gpt-4",
        "retry_on_failure": True
    },
    "researcher": {
        "primary": "localqwen2.5",
        "_ollama:fallback": "brave_search",
        "retry_on_failure": True
    },
    "documenter": {
        "primary": "local_ollama:qwen2.5",
        "fallback": "cloud_openai:gpt-3.5-turbo",
        "retry_on_failure": False
    },
    "verifier": {
        "primary": "cloud_openai:gpt-4",
        "fallback": "cloud_anthropic:claude-3",
        "retry_on_failure": False
    },
    "evaluator": {
        "primary": "local_ollama:deepseek-8b",
        "fallback": "cloud_openai:gpt-4",
        "retry_on_failure": True
    }
}

# Auto upgrade conditions
AUTO_UPGRADE_CONDITIONS = [
    "consecutive_failures >= 2",
    "verifier_confidence < 0.5",
    "task_priority == P0",
    "task_risk_level == high"
]

# Budget rules
DEFAULT_BUDGET_RULES = {
    "default_daily_limit": "10usd",
    "warning_threshold": 0.8,
    "hard_limit_action": "pause_all_tasks",
    "per_project_limit": {}
}


class ConnectionManager:
    """
    Centralized connection management system.
    
    Responsibilities:
    - Store and manage external service connections
    - Generate and manage capability tokens
    - Enforce routing rules
    - Track budgets and quotas
    - Perform health checks
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.connections: Dict[str, Connection] = {}
        self.tokens: Dict[str, CapabilityToken] = {}
        self.routing_rules = self.config.get("routing_rules", DEFAULT_ROUTING_RULES)
        self.budget_rules = self.config.get("budget_rules", DEFAULT_BUDGET_RULES)
        self.default_token_ttl = self.config.get("default_token_ttl_minutes", 15)
        
        # Budget tracking
        self.daily_spend: Dict[str, float] = {}  # date -> amount
        self.project_spend: Dict[str, float] = {}  # project_id -> amount
    
    # ==================== Connection Management ====================
    
    def add_connection(self, connection_data: Dict) -> Connection:
        """Add a new connection"""
        connection = Connection.from_dict(connection_data)
        self.connections[connection.connection_id] = connection
        return connection
    
    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Get connection by ID"""
        return self.connections.get(connection_id)
    
    def list_connections(
        self, 
        provider: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Connection]:
        """List connections with optional filters"""
        connections = list(self.connections.values())
        
        if provider:
            connections = [c for c in connections if c.provider == provider]
        if status:
            connections = [c for c in connections if c.status == status]
        
        return connections
    
    def update_connection(
        self, 
        connection_id: str, 
        updates: Dict
    ) -> Optional[Connection]:
        """Update connection properties"""
        connection = self.connections.get(connection_id)
        if not connection:
            return None
        
        for key, value in updates.items():
            if hasattr(connection, key):
                setattr(connection, key, value)
        
        connection.updated_at = datetime.utcnow().isoformat() + "Z"
        return connection
    
    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            return True
        return False
    
    def update_connection_status(
        self, 
        connection_id: str, 
        status: str
    ) -> bool:
        """Update connection status"""
        connection = self.connections.get(connection_id)
        if not connection:
            return False
        
        connection.status = status
        connection.updated_at = datetime.utcnow().isoformat() + "Z"
        return True
    
    # ==================== Capability Tokens ====================
    
    def generate_token(
        self,
        connection_id: str,
        worker_id: str,
        task_id: str,
        permissions: List[str],
        restrictions: Optional[Dict] = None,
        ttl_minutes: Optional[int] = None
    ) -> Optional[CapabilityToken]:
        """
        Generate a capability token for a worker.
        
        Args:
            connection_id: Connection to grant access to
            worker_id: Worker requesting access
            task_id: Task this token is for
            permissions: List of permissions to grant
            restrictions: Additional restrictions (rpm, cost limits, etc.)
            ttl_minutes: Token time-to-live in minutes
        
        Returns:
            CapabilityToken if successful, None if connection not found
        """
        connection = self.connections.get(connection_id)
        if not connection:
            return None
        
        # Validate permissions against connection scopes
        valid_permissions = self._validate_permissions(
            permissions, connection.scopes
        )
        
        if not valid_permissions:
            return None
        
        # Check quota
        if not self._check_quota(connection):
            return None
        
        # Create token
        ttl = ttl_minutes or self.default_token_ttl
        expiry = datetime.utcnow() + timedelta(minutes=ttl)
        
        token = CapabilityToken(
            token_id=f"cap_{uuid.uuid4().hex[:12]}",
            connection_id=connection_id,
            issued_to={
                "worker_id": worker_id,
                "task_id": task_id
            },
            permissions=valid_permissions,
            restrictions=restrictions or {},
            expires_at=expiry.isoformat() + "Z"
        )
        
        self.tokens[token.token_id] = token
        
        # Update connection last used
        connection.last_used = datetime.utcnow().isoformat() + "Z"
        
        # Update quota
        self._increment_quota(connection)
        
        return token
    
    def get_token(self, token_id: str) -> Optional[CapabilityToken]:
        """Get token by ID"""
        return self.tokens.get(token_id)
    
    def validate_token(self, token_id: str) -> bool:
        """Validate a token"""
        token = self.tokens.get(token_id)
        if not token:
            return False
        return token.is_valid()
    
    def revoke_token(self, token_id: str) -> bool:
        """Revoke a token"""
        token = self.tokens.get(token_id)
        if not token:
            return False
        
        token.status = "revoked"
        return True
    
    def get_worker_tokens(self, worker_id: str) -> List[CapabilityToken]:
        """Get all tokens for a worker"""
        return [
            t for t in self.tokens.values()
            if t.issued_to.get("worker_id") == worker_id
        ]
    
    def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens"""
        expired = [
            token_id for token_id, token in self.tokens.items()
            if token.is_expired()
        ]
        for token_id in expired:
            del self.tokens[token_id]
        return len(expired)
    
    def _validate_permissions(
        self, 
        permissions: List[str], 
        allowed_scopes: List[str]
    ) -> List[str]:
        """Validate permissions against allowed scopes
        
        More permissive validation:
        - If no scopes defined, allow all permissions
        - Check permission category matches scope prefix
        - Also allow if permission is explicitly in PERMISSION_TYPES
        """
        if not allowed_scopes:
            # No scopes defined, allow requested permissions
            return permissions
        
        valid = []
        permission_categories = set()
        for perm in permissions:
            # Extract category (e.g., "llm" from "llm.call")
            category = perm.split('.')[0] if '.' in perm else perm
            permission_categories.add(category)
        
        for perm in permissions:
            category = perm.split('.')[0] if '.' in perm else perm
            # Check if any allowed scope matches the category
            for scope in allowed_scopes:
                scope_category = scope.split('.')[0] if '.' in scope else scope
                if category == scope_category:
                    valid.append(perm)
                    break
            else:
                # Also check if permission exists in PERMISSION_TYPES
                if category in PERMISSION_TYPES:
                    # If the category is known, be permissive
                    valid.append(perm)
        
        return valid
    
    def _check_quota(self, connection: Connection) -> bool:
        """Check if connection has quota available"""
        if not connection.quota:
            return True
        
        try:
            current = float(connection.quota.current)
            limit = float(connection.quota.limit)
            return current < limit
        except (ValueError, TypeError):
            return True
    
    def _increment_quota(self, connection: Connection) -> None:
        """Increment quota usage (simplified tracking)"""
        if connection.quota:
            try:
                current = float(connection.quota.current)
                connection.quota.current = str(current + 1)
            except (ValueError, TypeError):
                pass
    
    # ==================== Routing ====================
    
    def get_connection_for_worker(
        self,
        worker_type: str,
        prefer_local: bool = True
    ) -> Optional[Connection]:
        """
        Get appropriate connection for a worker type based on routing rules.
        
        Args:
            worker_type: Type of worker (builder, researcher, etc.)
            prefer_local: Whether to prefer local models
        
        Returns:
            Best matching Connection or None
        """
        rules = self.routing_rules.get(worker_type, {})
        
        # Try primary connection
        primary_name = rules.get("primary", "")
        if primary_name:
            conn = self._find_connection_by_name(primary_name)
            if conn and conn.is_active():
                return conn
        
        # Try fallback
        fallback_name = rules.get("fallback", "")
        if fallback_name:
            conn = self._find_connection_by_name(fallback_name)
            if conn and conn.is_active():
                return conn
        
        # Fallback to any active connection
        active_conns = self.list_connections(status="active")
        if active_conns:
            return active_conns[0]
        
        return None
    
    def _find_connection_by_name(self, name: str) -> Optional[Connection]:
        """Find connection by name pattern"""
        for conn in self.connections.values():
            if name in conn.name.lower() or name in conn.connection_id.lower():
                return conn
            # Check local config
            if conn.local_config:
                for model in conn.local_config.models:
                    if name in model.name:
                        return conn
        return None
    
    def should_auto_upgrade(
        self,
        consecutive_failures: int = 0,
        verifier_confidence: float = 1.0,
        task_priority: str = "P2",
        task_risk_level: str = "low"
    ) -> bool:
        """Determine if should auto-upgrade to more powerful model"""
        if consecutive_failures >= 2:
            return True
        if verifier_confidence < 0.5:
            return True
        if task_priority in ["P0", "P1"]:
            return True
        if task_risk_level == "high":
            return True
        return False
    
    # ==================== Budget Control ====================
    
    def check_budget(
        self, 
        project_id: str, 
        estimated_cost: float = 0,
        record_spend_on_check: bool = True
    ) -> Dict[str, Any]:
        """
        Check if project is within budget.
        
        Args:
            project_id: Project ID to check
            estimated_cost: Estimated cost to check against limits
            record_spend_on_check: Whether to record the spend when allowed (default True)
        
        Returns:
            Dict with 'allowed' bool and 'reason' if denied
        """
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Check daily limit
        daily_limit = self._parse_budget(self.budget_rules["default_daily_limit"])
        current_daily = self.daily_spend.get(today, 0)
        
        if current_daily + estimated_cost > daily_limit:
            return {
                "allowed": False,
                "reason": "daily_limit_exceeded",
                "current": current_daily,
                "limit": daily_limit
            }
        
        # Check project-specific limit
        project_limit = self.budget_rules.get("per_project_limit", {}).get(
            project_id
        )
        if project_limit:
            limit = self._parse_budget(project_limit)
            current_project = self.project_spend.get(project_id, 0)
            
            if current_project + estimated_cost > limit:
                return {
                    "allowed": False,
                    "reason": "project_limit_exceeded",
                    "current": current_project,
                    "limit": limit
                }
        
        # Budget is available - optionally record the spend
        if record_spend_on_check and estimated_cost > 0:
            self.record_spend(project_id, estimated_cost)
        
        return {"allowed": True}
    
    def record_spend(
        self, 
        project_id: str, 
        amount: float
    ) -> None:
        """Record spending for a project"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Update daily spend
        self.daily_spend[today] = self.daily_spend.get(today, 0) + amount
        
        # Update project spend
        self.project_spend[project_id] = self.project_spend.get(
            project_id, 0
        ) + amount
    
    def get_budget_status(self) -> Dict:
        """Get current budget status"""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        daily_limit = self._parse_budget(
            self.budget_rules["default_daily_limit"]
        )
        
        return {
            "daily_spend": self.daily_spend.get(today, 0),
            "daily_limit": daily_limit,
            "daily_remaining": max(0, daily_limit - self.daily_spend.get(today, 0)),
            "warning_threshold": self.budget_rules["warning_threshold"],
            "project_spends": dict(self.project_spend)
        }
    
    def _parse_budget(self, budget_str: str) -> float:
        """Parse budget string like '10usd' to float"""
        try:
            return float(budget_str.lower().replace("usd", ""))
        except ValueError:
            return float("inf")
    
    # ==================== Health Check ====================
    
    def perform_health_check(self, connection_id: str) -> Dict:
        """
        Perform health check on a connection.
        
        In a real implementation, this would actually test the connection
        by making a simple API call.
        """
        connection = self.connections.get(connection_id)
        if not connection:
            return {"status": "unknown", "error": "connection_not_found"}
        
        if not connection.health_check or not connection.health_check.enabled:
            return {"status": "unknown", "error": "health_check_disabled"}
        
        # Update last check time
        now = datetime.utcnow().isoformat() + "Z"
        connection.health_check.last_check = now
        
        # Simplified health check - in real impl would test actual connectivity
        # For now, check if connection is active and not expired
        is_healthy = connection.is_active() and not connection.is_expired()
        
        health_status = HealthStatus.HEALTHY.value if is_healthy else \
                        HealthStatus.UNHEALTHY.value
        connection.health_check.status = health_status
        
        return {
            "connection_id": connection_id,
            "status": health_status,
            "last_check": now
        }
    
    def get_unhealthy_connections(self) -> List[Connection]:
        """Get all unhealthy connections"""
        return [
            c for c in self.connections.values()
            if c.health_check and c.health_check.status == HealthStatus.UNHEALTHY.value
        ]
    
    # ==================== State Management ====================
    
    def export_state(self) -> Dict:
        """Export current state for persistence"""
        return {
            "connections": [
                c.to_dict() for c in self.connections.values()
            ],
            "routing_rules": self.routing_rules,
            "budget_rules": self.budget_rules,
            "daily_spend": self.daily_spend,
            "project_spend": self.project_spend
        }
    
    def import_state(self, state: Dict) -> None:
        """Import state from persistence"""
        self.connections.clear()
        
        for conn_data in state.get("connections", []):
            conn = Connection.from_dict(conn_data)
            self.connections[conn.connection_id] = conn
        
        self.routing_rules = state.get("routing_rules", DEFAULT_ROUTING_RULES)
        self.budget_rules = state.get("budget_rules", DEFAULT_BUDGET_RULES)
        self.daily_spend = state.get("daily_spend", {})
        self.project_spend = state.get("project_spend", {})
    
    def get_status_summary(self) -> Dict:
        """Get overall status summary"""
        total_connections = len(self.connections)
        active_connections = len([
            c for c in self.connections.values() 
            if c.status == ConnectionStatus.ACTIVE.value
        ])
        
        return {
            "total_connections": total_connections,
            "active_connections": active_connections,
            "total_tokens": len(self.tokens),
            "active_tokens": len([t for t in self.tokens.values() if t.is_valid()]),
            "budget_status": self.get_budget_status()
        }


def create_connection_manager(config: Optional[Dict] = None) -> ConnectionManager:
    """Factory function to create a ConnectionManager"""
    return ConnectionManager(config)


# ==================== Demo Usage ====================

if __name__ == "__main__":
    # Create connection manager
    cm = create_connection_manager()
    
    # Add an OpenAI connection
    openai_conn = cm.add_connection({
        "connection_id": "conn_openai_001",
        "provider": "openai",
        "name": "Work OpenAI",
        "auth_type": "api_key",
        "scopes": ["chat_completions", "embeddings"],
        "quota": {
            "quota_type": "monthly",
            "limit": "100",
            "current": "25"
        },
        "allowed_workers": ["worker_builder_01"],
        "allowed_projects": ["proj_story_engine"]
    })
    print(f"Added OpenAI connection: {openai_conn.connection_id}")
    
    # Add an Ollama local connection
    ollama_conn = cm.add_connection({
        "connection_id": "conn_ollama_001",
        "provider": "ollama",
        "name": "Local DeepSeek",
        "auth_type": "local",
        "local_config": {
            "endpoint": "http://localhost:11434",
            "models": [
                {
                    "name": "deepseek-r1:8b",
                    "context_limit": 32768,
                    "recommended_for": ["builder", "reasoning"]
                },
                {
                    "name": "qwen2.5:14b",
                    "context_limit": 32768,
                    "recommended_for": ["documenter"]
                }
            ],
            "concurrency_limit": 2
        },
        "allowed_workers": ["worker_builder_01", "worker_doc_01"],
        "allowed_projects": ["proj_story_engine"]
    })
    print(f"Added Ollama connection: {ollama_conn.connection_id}")
    
    # Generate a token for a worker
    token = cm.generate_token(
        connection_id="conn_ollama_001",
        worker_id="worker_builder_01",
        task_id="task_001",
        permissions=["llm.call"],
        restrictions={"max_rpm": 30}
    )
    print(f"Generated token: {token.token_id}")
    
    # Check routing for builder
    builder_conn = cm.get_connection_for_worker("builder")
    print(f"Builder connection: {builder_conn.name if builder_conn else 'None'}")
    
    # Check budget
    budget = cm.check_budget("proj_story_engine", 2.0)
    print(f"Budget check: {budget}")
    
    # Record spend
    cm.record_spend("proj_story_engine", 2.0)
    
    # Get status
    print(f"\nStatus: {cm.get_status_summary()}")
