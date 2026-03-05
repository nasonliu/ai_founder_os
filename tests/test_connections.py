"""
Integration tests for Connection Manager module
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from src.connections.manager import (
    ConnectionManager,
    Connection,
    CapabilityToken,
    ProviderType,
    AuthType,
    ConnectionStatus,
    HealthStatus,
    create_connection_manager,
    DEFAULT_ROUTING_RULES,
    DEFAULT_BUDGET_RULES,
    LocalModel,
    LocalConfig,
    OAuthConfig,
    Quota,
    HealthCheck,
    Credentials
)


class TestConnection:
    """Test Connection model"""
    
    def test_connection_creation(self):
        """Test creating a connection"""
        conn = Connection(
            connection_id="conn_001",
            provider="openai",
            name="Test OpenAI",
            auth_type="api_key"
        )
        assert conn.connection_id == "conn_001"
        assert conn.provider == "openai"
        assert conn.status == "active"
        assert conn.auth_type == "api_key"
    
    def test_connection_to_dict(self):
        """Test connection serialization"""
        conn = Connection(
            connection_id="conn_001",
            provider="openai",
            name="Test OpenAI",
            auth_type="api_key",
            scopes=["chat_completions"]
        )
        data = conn.to_dict()
        assert data["connection_id"] == "conn_001"
        assert data["provider"] == "openai"
    
    def test_connection_from_dict(self):
        """Test connection deserialization"""
        data = {
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "Test OpenAI",
            "auth_type": "api_key",
            "scopes": ["chat_completions"]
        }
        conn = Connection.from_dict(data)
        assert conn.connection_id == "conn_001"
        assert conn.scopes == ["chat_completions"]
    
    def test_connection_with_local_config(self):
        """Test connection with local model config"""
        conn = Connection(
            connection_id="conn_ollama",
            provider="ollama",
            name="Local Ollama",
            auth_type="local",
            local_config=LocalConfig(
                endpoint="http://localhost:11434",
                models=[
                    LocalModel(
                        name="deepseek-r1:8b",
                        context_limit=32768,
                        recommended_for=["builder"]
                    )
                ]
            )
        )
        assert conn.local_config is not None
        assert len(conn.local_config.models) == 1
        assert conn.local_config.models[0].name == "deepseek-r1:8b"
    
    def test_connection_is_expired(self):
        """Test connection expiry check"""
        # Not expired
        conn = Connection(
            connection_id="conn_001",
            provider="openai",
            name="Test",
            auth_type="api_key"
        )
        assert not conn.is_expired()
        
        # Expired
        conn_expired = Connection(
            connection_id="conn_002",
            provider="openai",
            name="Test",
            auth_type="api_key",
            expires_at="2020-01-01T00:00:00Z"
        )
        assert conn_expired.is_expired()


class TestCapabilityToken:
    """Test CapabilityToken model"""
    
    def test_token_creation(self):
        """Test creating a capability token"""
        token = CapabilityToken(
            token_id="cap_001",
            connection_id="conn_001",
            issued_to={"worker_id": "worker_001", "task_id": "task_001"},
            permissions=["llm.call"]
        )
        assert token.token_id == "cap_001"
        assert token.status == "active"
        assert token.is_valid()
    
    def test_token_expiry(self):
        """Test token expiry"""
        # Valid token
        token = CapabilityToken(
            token_id="cap_001",
            connection_id="conn_001",
            issued_to={"worker_id": "worker_001", "task_id": "task_001"},
            permissions=["llm.call"]
        )
        assert not token.is_expired()
        
        # Expired token
        past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
        token_expired = CapabilityToken(
            token_id="cap_002",
            connection_id="conn_001",
            issued_to={"worker_id": "worker_001", "task_id": "task_001"},
            permissions=["llm.call"],
            expires_at=past_time
        )
        assert token_expired.is_expired()
        assert not token_expired.is_valid()


class TestConnectionManager:
    """Test ConnectionManager"""
    
    def test_create_manager(self):
        """Test creating a connection manager"""
        cm = create_connection_manager()
        assert cm is not None
        assert len(cm.connections) == 0
    
    def test_add_connection(self):
        """Test adding a connection"""
        cm = create_connection_manager()
        conn_data = {
            "connection_id": "conn_openai",
            "provider": "openai",
            "name": "OpenAI API",
            "auth_type": "api_key",
            "scopes": ["chat_completions"]
        }
        conn = cm.add_connection(conn_data)
        assert conn.connection_id == "conn_openai"
        assert len(cm.connections) == 1
    
    def test_get_connection(self):
        """Test retrieving a connection"""
        cm = create_connection_manager()
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "Test",
            "auth_type": "api_key"
        })
        
        conn = cm.get_connection("conn_001")
        assert conn is not None
        assert conn.name == "Test"
        
        # Non-existent
        assert cm.get_connection("conn_999") is None
    
    def test_list_connections(self):
        """Test listing connections with filters"""
        cm = create_connection_manager()
        
        # Add multiple connections
        cm.add_connection({
            "connection_id": "conn_openai",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "status": "active"
        })
        cm.add_connection({
            "connection_id": "conn_ollama",
            "provider": "ollama",
            "name": "Ollama",
            "auth_type": "local",
            "status": "active"
        })
        cm.add_connection({
            "connection_id": "conn_expired",
            "provider": "github",
            "name": "GitHub",
            "auth_type": "oauth",
            "status": "expired"
        })
        
        # List all
        all_conns = cm.list_connections()
        assert len(all_conns) == 3
        
        # Filter by provider
        openai_conns = cm.list_connections(provider="openai")
        assert len(openai_conns) == 1
        
        # Filter by status
        active_conns = cm.list_connections(status="active")
        assert len(active_conns) == 2
    
    def test_update_connection(self):
        """Test updating a connection"""
        cm = create_connection_manager()
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "Original Name",
            "auth_type": "api_key"
        })
        
        updated = cm.update_connection(
            "conn_001", 
            {"name": "New Name"}
        )
        assert updated.name == "New Name"
    
    def test_remove_connection(self):
        """Test removing a connection"""
        cm = create_connection_manager()
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "Test",
            "auth_type": "api_key"
        })
        
        assert cm.remove_connection("conn_001")
        assert len(cm.connections) == 0
        
        # Remove non-existent
        assert not cm.remove_connection("conn_999")


class TestCapabilityTokenManagement:
    """Test capability token generation and management"""
    
    def test_generate_token(self):
        """Test generating a capability token"""
        cm = create_connection_manager()
        
        # Add connection with scopes
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "scopes": ["chat_completions", "embeddings"]
        })
        
        token = cm.generate_token(
            connection_id="conn_001",
            worker_id="worker_001",
            task_id="task_001",
            permissions=["llm.call"]
        )
        
        assert token is not None
        assert token.connection_id == "conn_001"
        assert "llm.call" in token.permissions
    
    def test_generate_token_invalid_connection(self):
        """Test token generation with invalid connection"""
        cm = create_connection_manager()
        
        token = cm.generate_token(
            connection_id="conn_nonexistent",
            worker_id="worker_001",
            task_id="task_001",
            permissions=["llm.call"]
        )
        
        assert token is None
    
    def test_generate_token_quota_exceeded(self):
        """Test token generation when quota exceeded"""
        cm = create_connection_manager()
        
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "scopes": ["chat_completions"],
            "quota": {
                "quota_type": "monthly",
                "limit": "1",
                "current": "1"  # At limit
            }
        })
        
        token = cm.generate_token(
            connection_id="conn_001",
            worker_id="worker_001",
            task_id="task_001",
            permissions=["llm.call"]
        )
        
        assert token is None  # Quota exceeded
    
    def test_validate_token(self):
        """Test token validation"""
        cm = create_connection_manager()
        
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "scopes": ["chat_completions"]
        })
        
        token = cm.generate_token(
            connection_id="conn_001",
            worker_id="worker_001",
            task_id="task_001",
            permissions=["llm.call"]
        )
        
        assert cm.validate_token(token.token_id)
        assert not cm.validate_token("invalid_token")
    
    def test_revoke_token(self):
        """Test revoking a token"""
        cm = create_connection_manager()
        
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "scopes": ["chat_completions"]
        })
        
        token = cm.generate_token(
            connection_id="conn_001",
            worker_id="worker_001",
            task_id="task_001",
            permissions=["llm.call"]
        )
        
        assert cm.revoke_token(token.token_id)
        assert not cm.validate_token(token.token_id)
    
    def test_get_worker_tokens(self):
        """Test getting tokens for a worker"""
        cm = create_connection_manager()
        
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "scopes": ["chat_completions"]
        })
        
        # Generate tokens for same worker
        token1 = cm.generate_token(
            connection_id="conn_001",
            worker_id="worker_001",
            task_id="task_001",
            permissions=["llm.call"]
        )
        
        token2 = cm.generate_token(
            connection_id="conn_001",
            worker_id="worker_001",
            task_id="task_002",
            permissions=["llm.call"]
        )
        
        tokens = cm.get_worker_tokens("worker_001")
        assert len(tokens) == 2
        
        # Different worker
        tokens_other = cm.get_worker_tokens("worker_999")
        assert len(tokens_other) == 0
    
    def test_cleanup_expired_tokens(self):
        """Test cleaning up expired tokens"""
        cm = create_connection_manager()
        
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "scopes": ["chat_completions"]
        })
        
        # Add valid token
        cm.generate_token(
            connection_id="conn_001",
            worker_id="worker_001",
            task_id="task_001",
            permissions=["llm.call"]
        )
        
        # Manually add an expired token
        past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
        expired_token = CapabilityToken(
            token_id="cap_expired",
            connection_id="conn_001",
            issued_to={"worker_id": "worker_002", "task_id": "task_003"},
            permissions=["llm.call"],
            expires_at=past_time
        )
        cm.tokens["cap_expired"] = expired_token
        
        cleaned = cm.cleanup_expired_tokens()
        assert cleaned >= 1


class TestRouting:
    """Test routing functionality"""
    
    def test_get_connection_for_worker(self):
        """Test getting connection for worker type"""
        cm = create_connection_manager()
        
        # Add connections
        cm.add_connection({
            "connection_id": "conn_ollama",
            "provider": "ollama",
            "name": "Local Ollama",
            "auth_type": "local",
            "status": "active"
        })
        cm.add_connection({
            "connection_id": "conn_openai",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "status": "active"
        })
        
        conn = cm.get_connection_for_worker("builder")
        assert conn is not None
    
    def test_should_auto_upgrade(self):
        """Test auto-upgrade conditions"""
        cm = create_connection_manager()
        
        # Should not upgrade
        assert not cm.should_auto_upgrade(
            consecutive_failures=1,
            verifier_confidence=0.8,
            task_priority="P2",
            task_risk_level="low"
        )
        
        # Should upgrade - consecutive failures
        assert cm.should_auto_upgrade(
            consecutive_failures=2,
            verifier_confidence=0.8,
            task_priority="P2",
            task_risk_level="low"
        )
        
        # Should upgrade - low confidence
        assert cm.should_auto_upgrade(
            consecutive_failures=1,
            verifier_confidence=0.4,
            task_priority="P2",
            task_risk_level="low"
        )
        
        # Should upgrade - P0 priority
        assert cm.should_auto_upgrade(
            consecutive_failures=1,
            verifier_confidence=0.8,
            task_priority="P0",
            task_risk_level="low"
        )
        
        # Should upgrade - high risk
        assert cm.should_auto_upgrade(
            consecutive_failures=1,
            verifier_confidence=0.8,
            task_priority="P2",
            task_risk_level="high"
        )


class TestBudgetControl:
    """Test budget control functionality"""
    
    def test_check_budget(self):
        """Test budget checking"""
        cm = create_connection_manager()
        
        # Should allow - check_budget now records spend when allowed
        result = cm.check_budget("proj_001", 5.0)
        assert result["allowed"]
        
        # Should still allow (under default limit 10): 5 + 2 = 7 < 10
        result = cm.check_budget("proj_001", 2.0)
        assert result["allowed"]
        
        # Should deny (would exceed): 7 + 5 = 12 > 10
        result = cm.check_budget("proj_001", 5.0)
        assert not result["allowed"]
        assert result["reason"] == "daily_limit_exceeded"
    
    def test_project_specific_budget(self):
        """Test project-specific budget limits"""
        cm = create_connection_manager({
            "budget_rules": {
                "default_daily_limit": "100usd",
                "per_project_limit": {
                    "proj_story_engine": "5usd"
                }
            }
        })
        
        # Should allow under project limit
        result = cm.check_budget("proj_story_engine", 3.0)
        assert result["allowed"]
        
        # Should deny over project limit
        result = cm.check_budget("proj_story_engine", 4.0)
        assert not result["allowed"]
        assert result["reason"] == "project_limit_exceeded"
    
    def test_get_budget_status(self):
        """Test getting budget status"""
        cm = create_connection_manager()
        
        cm.record_spend("proj_001", 3.0)
        cm.record_spend("proj_002", 2.0)
        
        status = cm.get_budget_status()
        assert "daily_spend" in status
        assert "daily_limit" in status
        assert status["daily_spend"] == 5.0


class TestHealthCheck:
    """Test health check functionality"""
    
    def test_perform_health_check(self):
        """Test performing health check"""
        cm = create_connection_manager()
        
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "health_check": {
                "enabled": True,
                "interval_minutes": 60
            }
        })
        
        result = cm.perform_health_check("conn_001")
        assert "status" in result
        assert result["connection_id"] == "conn_001"
    
    def test_get_unhealthy_connections(self):
        """Test getting unhealthy connections"""
        cm = create_connection_manager()
        
        cm.add_connection({
            "connection_id": "conn_healthy",
            "provider": "openai",
            "name": "Healthy",
            "auth_type": "api_key",
            "status": "active",
            "health_check": {
                "enabled": True,
                "status": "healthy"
            }
        })
        
        cm.add_connection({
            "connection_id": "conn_unhealthy",
            "provider": "openai",
            "name": "Unhealthy",
            "auth_type": "api_key",
            "status": "active",
            "health_check": {
                "enabled": True,
                "status": "unhealthy"
            }
        })
        
        unhealthy = cm.get_unhealthy_connections()
        assert len(unhealthy) == 1
        assert unhealthy[0].connection_id == "conn_unhealthy"


class TestStateManagement:
    """Test state persistence"""
    
    def test_export_import_state(self):
        """Test exporting and importing state"""
        cm = create_connection_manager()
        
        # Add connections and tokens
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key"
        })
        
        cm.record_spend("proj_001", 5.0)
        
        # Export state
        state = cm.export_state()
        assert "connections" in state
        assert len(state["connections"]) == 1
        
        # Create new manager and import
        cm2 = create_connection_manager()
        cm2.import_state(state)
        
        assert len(cm2.connections) == 1
        assert cm2.get_connection("conn_001").name == "OpenAI"
        assert cm2.project_spend.get("proj_001", 0) == 5.0


class TestStatusSummary:
    """Test status summary"""
    
    def test_get_status_summary(self):
        """Test getting status summary"""
        cm = create_connection_manager()
        
        cm.add_connection({
            "connection_id": "conn_001",
            "provider": "openai",
            "name": "OpenAI",
            "auth_type": "api_key",
            "status": "active"
        })
        
        cm.add_connection({
            "connection_id": "conn_002",
            "provider": "ollama",
            "name": "Ollama",
            "auth_type": "local",
            "status": "expired"
        })
        
        summary = cm.get_status_summary()
        assert summary["total_connections"] == 2
        assert summary["active_connections"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
