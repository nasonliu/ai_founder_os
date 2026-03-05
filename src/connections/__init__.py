"""
AI Founder OS - Connections Module

This module provides connection management for external services.
"""

from .manager import (
    ConnectionManager,
    Connection,
    CapabilityToken,
    ProviderType,
    AuthType,
    ConnectionStatus,
    HealthStatus,
    create_connection_manager,
    PERMISSION_TYPES,
    DEFAULT_ROUTING_RULES,
    DEFAULT_BUDGET_RULES
)

__all__ = [
    "ConnectionManager",
    "Connection",
    "CapabilityToken",
    "ProviderType",
    "AuthType", 
    "ConnectionStatus",
    "HealthStatus",
    "create_connection_manager",
    "PERMISSION_TYPES",
    "DEFAULT_ROUTING_RULES",
    "DEFAULT_BUDGET_RULES"
]
