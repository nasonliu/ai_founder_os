"""
Skill Hub Loader Module

Provides skill loading with manifest validation and security scanning.
The Skill Hub enables system capability extension through installable skills.
"""

import json
import hashlib
import re
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import jsonschema

# Configure logging
logging = logging.getLogger(__name__)


class SkillSource(Enum):
    """Skill source types"""
    OPENCLAW_HUB = "openclaw_hub"
    PRIVATE = "private"
    LOCAL = "local"


class SecurityStatus(Enum):
    """Security audit status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RuntimeType(Enum):
    """Skill runtime types"""
    PYTHON = "python"
    NODE = "node"
    BASH = "bash"
    DOCKER = "docker"


# Security patterns to scan for
DANGEROUS_PATTERNS = [
    # File destruction
    (r'rm\s+-rf\s+/', "Destructive file removal"),
    (r'del\s+/[sq]\s+/', "Windows destructive deletion"),
    (r'format\s+[a-z]:', "Disk format command"),
    
    # Credential theft
    (r'curl.*\|\s*bash', "Pipe to bash (common attack)"),
    (r'wget.*\|\s*bash', "Wget pipe to bash"),
    (r'base64.*-d.*\$\{', "Base64 decode with env vars"),
    (r'eval\s+\$\(', "Eval with command substitution"),
    
    # Network exfiltration
    (r'nc\s+-[elvp]', "Netcat reverse shell patterns"),
    (r'/dev/tcp/', "Bash TCP redirect"),
    (r'curl.*-d.*password', "Password exfiltration"),
    (r'wget.*-O.*-', "File exfiltration"),
    
    # Privilege escalation
    (r'sudo\s+su', "Privilege escalation"),
    (r'chmod\s+777', "World-writable permissions"),
    (r'chown\s+-R', "Recursive ownership change"),
    
    # Suspicious patterns
    (r'\$\{.*\}', "Environment variable expansion"),
    (r'`.*`', "Command substitution"),
    (r'\|\s*sh', "Pipe to shell"),
]

# Required permission fields
REQUIRED_PERMISSIONS = ["filesystem", "network", "secrets"]

# Default deny network pattern
DEFAULT_DENY_ALL = True


@dataclass
class FilesystemPermissions:
    """Filesystem permission configuration"""
    read: List[str] = field(default_factory=list)
    write: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[str]]:
        return {"read": self.read, "write": self.write}

    @classmethod
    def from_dict(cls, data: Dict[str, List[str]]) -> 'FilesystemPermissions':
        return cls(
            read=data.get("read", []),
            write=data.get("write", [])
        )


@dataclass
class NetworkPermissions:
    """Network permission configuration"""
    allow_domains: List[str] = field(default_factory=list)
    deny_domains: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[str]]:
        return {
            "allow_domains": self.allow_domains,
            "deny_domains": self.deny_domains
        }

    @classmethod
    def from_dict(cls, data: Dict[str, List[str]]) -> 'NetworkPermissions':
        return cls(
            allow_domains=data.get("allow_domains", []),
            deny_domains=data.get("deny_domains", [])
        )


@dataclass
class ProcessPermissions:
    """Process permission configuration"""
    allow_commands: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, List[str]]:
        return {"allow_commands": self.allow_commands}

    @classmethod
    def from_dict(cls, data: Dict[str, List[str]]) -> 'ProcessPermissions':
        return cls(
            allow_commands=data.get("allow_commands", [])
        )


@dataclass
class SkillPermissions:
    """Complete permission configuration for a skill"""
    filesystem: FilesystemPermissions = field(default_factory=FilesystemPermissions)
    network: NetworkPermissions = field(default_factory=NetworkPermissions)
    secrets: List[str] = field(default_factory=list)
    process: Optional[ProcessPermissions] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "filesystem": self.filesystem.to_dict(),
            "network": self.network.to_dict(),
            "secrets": self.secrets
        }
        if self.process:
            result["process"] = self.process.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillPermissions':
        return cls(
            filesystem=FilesystemPermissions.from_dict(data.get("filesystem", {})),
            network=NetworkPermissions.from_dict(data.get("network", {})),
            secrets=data.get("secrets", []),
            process=ProcessPermissions.from_dict(data.get("process", {})) if data.get("process") else None
        )


@dataclass
class SkillManifest:
    """Complete skill manifest"""
    name: str
    version: str
    author: str
    description: str
    entrypoints: List[str]
    permissions: SkillPermissions
    runtime: str
    source: str = "private"
    dependencies: List[str] = field(default_factory=list)
    checks: List[str] = field(default_factory=list)
    signature: Optional[str] = None
    quarantine: bool = True
    security_status: str = "pending"
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "source": self.source,
            "description": self.description,
            "entrypoints": self.entrypoints,
            "permissions": self.permissions.to_dict(),
            "dependencies": self.dependencies,
            "runtime": self.runtime,
            "checks": self.checks,
            "signature": self.signature,
            "quarantine": self.quarantine,
            "security_status": self.security_status,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillManifest':
        return cls(
            name=data["name"],
            version=data["version"],
            author=data["author"],
            description=data["description"],
            entrypoints=data["entrypoints"],
            permissions=SkillPermissions.from_dict(data["permissions"]),
            runtime=data["runtime"],
            source=data.get("source", "private"),
            dependencies=data.get("dependencies", []),
            checks=data.get("checks", []),
            signature=data.get("signature"),
            quarantine=data.get("quarantine", True),
            security_status=data.get("security_status", "pending"),
            tags=data.get("tags", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )


@dataclass
class SecurityScanResult:
    """Result of security scan"""
    passed: bool
    issues: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    scan_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "issues": self.issues,
            "warnings": self.warnings,
            "scan_timestamp": self.scan_timestamp
        }


@dataclass
class ManifestValidationResult:
    """Result of manifest validation"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


class SkillHubLoader:
    """
    Skill Hub Loader with manifest validation and security scanning.
    
    Provides:
    - Manifest schema validation
    - Static security scanning
    - Permission analysis
    - Skill quarantine management
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize the Skill Hub Loader.
        
        Args:
            schema_path: Path to skill manifest JSON schema file
        """
        self.schema_path = schema_path
        self._schema: Optional[Dict[str, Any]] = None
        self._loaded_skills: Dict[str, SkillManifest] = {}
        
    @property
    def schema(self) -> Dict[str, Any]:
        """Load and cache the JSON schema"""
        if self._schema is None:
            if self.schema_path:
                with open(self.schema_path, 'r') as f:
                    self._schema = json.load(f)
            else:
                # Use inline default schema
                self._schema = self._get_default_schema()
        return self._schema
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """Get default inline schema"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["name", "version", "author", "description", "entrypoints", "permissions", "runtime"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
                "author": {"type": "string"},
                "source": {"type": "string", "enum": ["openclaw_hub", "private", "local"]},
                "description": {"type": "string"},
                "entrypoints": {"type": "array", "items": {"type": "string"}},
                "permissions": {"type": "object"},
                "dependencies": {"type": "array", "items": {"type": "string"}},
                "runtime": {"type": "string", "enum": ["python", "node", "bash", "docker"]},
                "checks": {"type": "array", "items": {"type": "string"}},
                "signature": {"type": "string"},
                "quarantine": {"type": "boolean"},
                "security_status": {"type": "string", "enum": ["pending", "approved", "rejected"]},
                "tags": {"type": "array", "items": {"type": "string"}}
            }
        }
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> ManifestValidationResult:
        """
        Validate a skill manifest against the schema.
        
        Args:
            manifest: Skill manifest dictionary
            
        Returns:
            ManifestValidationResult with validation status
        """
        errors = []
        warnings = []
        
        # Schema validation
        try:
            jsonschema.validate(manifest, self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            return ManifestValidationResult(valid=False, errors=errors)
        except jsonschema.SchemaError as e:
            errors.append(f"Schema error: {e.message}")
            return ManifestValidationResult(valid=False, errors=errors)
        
        # Required permissions check
        permissions = manifest.get("permissions", {})
        for req_perm in REQUIRED_PERMISSIONS:
            if req_perm not in permissions:
                errors.append(f"Missing required permission: {req_perm}")
        
        # Filesystem permissions validation
        fs_perms = permissions.get("filesystem", {})
        if fs_perms.get("write") and not fs_perms.get("read"):
            warnings.append("Skill has write but no explicit read permissions")
        
        # Version format check
        version = manifest.get("version", "")
        if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+$', version):
            errors.append(f"Invalid version format: {version}")
        
        # Runtime validation
        runtime = manifest.get("runtime", "")
        if runtime not in ["python", "node", "bash", "docker"]:
            errors.append(f"Invalid runtime: {runtime}")
        
        # Source validation
        source = manifest.get("source", "private")
        if source not in ["openclaw_hub", "private", "local"]:
            warnings.append(f"Non-standard source: {source}")
        
        # Security status validation
        security_status = manifest.get("security_status", "pending")
        if security_status not in ["pending", "approved", "rejected"]:
            errors.append(f"Invalid security_status: {security_status}")
        
        valid = len(errors) == 0
        return ManifestValidationResult(valid=valid, errors=errors, warnings=warnings)
    
    def scan_security(self, manifest: Dict[str, Any], code_content: Optional[str] = None) -> SecurityScanResult:
        """
        Perform static security scanning on a skill manifest.
        
        Args:
            manifest: Skill manifest dictionary
            code_content: Optional skill code content to scan
            
        Returns:
            SecurityScanResult with scan findings
        """
        issues = []
        warnings = []
        
        # Scan manifest permissions
        permissions = manifest.get("permissions", {})
        
        # Check for dangerous filesystem permissions
        fs_perms = permissions.get("filesystem", {})
        write_paths = fs_perms.get("write", [])
        
        dangerous_paths = [p for p in write_paths if p.startswith('/') 
                          and not p.startswith('/tmp') 
                          and not p.startswith('/workspace')]
        if dangerous_paths:
            issues.append({
                "type": "dangerous_filesystem",
                "message": f"Writing to sensitive paths: {dangerous_paths}"
            })
        
        # Check for overly broad network permissions
        network_perms = permissions.get("network", {})
        allow_domains = network_perms.get("allow_domains", [])
        
        if "*" in allow_domains or ".*" in allow_domains:
            issues.append({
                "type": "overly_broad_network",
                "message": "Wildcard domain allowance detected"
            })
        
        # Check for excessive secrets access
        secrets = permissions.get("secrets", [])
        if len(secrets) > 5:
            warnings.append(f"Excessive secret capabilities requested: {len(secrets)}")
        
        # Check process permissions
        process_perms = permissions.get("process", {})
        allow_commands = process_perms.get("allow_commands", [])
        
        dangerous_cmds = [c for c in allow_commands if any(
            pattern in c.lower() for pattern in ['sudo', 'chmod 777', 'rm -rf', 'del /']
        )]
        if dangerous_cmds:
            issues.append({
                "type": "dangerous_process",
                "message": f"Dangerous commands allowed: {dangerous_cmds}"
            })
        
        # Scan code content if provided
        if code_content:
            code_issues = self._scan_code_content(code_content)
            issues.extend(code_issues)
        
        passed = len(issues) == 0
        return SecurityScanResult(passed=passed, issues=issues, warnings=warnings)
    
    def _scan_code_content(self, code: str) -> List[Dict[str, str]]:
        """
        Scan code content for dangerous patterns.
        
        Args:
            code: Code content to scan
            
        Returns:
            List of detected issues
        """
        issues = []
        
        for pattern, description in DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append({
                    "type": "dangerous_pattern",
                    "message": f"Detected: {description} (pattern: {pattern})"
                })
        
        return issues
    
    def load_skill(self, manifest: Dict[str, Any], validate: bool = True) -> SkillManifest:
        """
        Load and validate a skill from manifest.
        
        Args:
            manifest: Skill manifest dictionary
            validate: Whether to perform validation
            
        Returns:
            Validated SkillManifest object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate manifest
        if validate:
            validation_result = self.validate_manifest(manifest)
            if not validation_result.valid:
                raise ValueError(f"Manifest validation failed: {validation_result.errors}")
            
            # Security scan
            security_result = self.scan_security(manifest)
            if not security_result.passed:
                logging.warning(f"Security scan issues: {security_result.issues}")
        
        # Parse manifest
        skill = SkillManifest.from_dict(manifest)
        
        # Set timestamps
        now = datetime.now(timezone.utc).isoformat()
        if not skill.created_at:
            skill.created_at = now
        skill.updated_at = now
        
        # Cache loaded skill
        self._loaded_skills[skill.name] = skill
        
        return skill
    
    def load_skill_from_file(self, file_path: str, validate: bool = True) -> SkillManifest:
        """
        Load a skill from a manifest file.
        
        Args:
            file_path: Path to skill manifest JSON file
            validate: Whether to perform validation
            
        Returns:
            Validated SkillManifest object
        """
        with open(file_path, 'r') as f:
            manifest = json.load(f)
        
        return self.load_skill(manifest, validate=validate)
    
    def get_loaded_skills(self) -> Dict[str, SkillManifest]:
        """Get all loaded skills"""
        return self._loaded_skills.copy()
    
    def get_skill(self, name: str) -> Optional[SkillManifest]:
        """Get a specific loaded skill by name"""
        return self._loaded_skills.get(name)
    
    def analyze_permissions(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and summarize skill permissions.
        
        Args:
            manifest: Skill manifest dictionary
            
        Returns:
            Permission analysis summary
        """
        permissions = manifest.get("permissions", {})
        
        analysis = {
            "risk_level": "low",
            "read_count": len(permissions.get("filesystem", {}).get("read", [])),
            "write_count": len(permissions.get("filesystem", {}).get("write", [])),
            "network_allow_count": len(permissions.get("network", {}).get("allow_domains", [])),
            "secrets_count": len(permissions.get("secrets", [])),
            "process_commands_count": len(permissions.get("process", {}).get("allow_commands", [])),
            "quarantine": manifest.get("quarantine", True),
            "security_status": manifest.get("security_status", "pending")
        }
        
        # Calculate risk level
        risk_score = 0
        if analysis["write_count"] > 2:
            risk_score += 2
        if analysis["network_allow_count"] > 3:
            risk_score += 2
        if analysis["secrets_count"] > 2:
            risk_score += 2
        if analysis["process_commands_count"] > 0:
            risk_score += 1
        if analysis["quarantine"]:
            risk_score += 1
            
        if risk_score >= 5:
            analysis["risk_level"] = "high"
        elif risk_score >= 2:
            analysis["risk_level"] = "medium"
        
        return analysis
    
    def get_skill_entrypoints(self, name: str) -> List[str]:
        """Get available entrypoints for a skill"""
        skill = self.get_skill(name)
        if skill:
            return skill.entrypoints
        return []
    
    def is_skill_approved(self, name: str) -> bool:
        """Check if a skill is approved for production use"""
        skill = self.get_skill(name)
        if skill:
            return skill.security_status == "approved" and not skill.quarantine
        return False
    
    def approve_skill(self, name: str) -> bool:
        """
        Approve a skill for production use.
        
        Args:
            name: Skill name
            
        Returns:
            True if approved successfully
        """
        skill = self._loaded_skills.get(name)
        if skill:
            skill.security_status = "approved"
            skill.quarantine = False
            skill.updated_at = datetime.now(timezone.utc).isoformat()
            return True
        return False
    
    def reject_skill(self, name: str, reason: str) -> bool:
        """
        Reject a skill from the system.
        
        Args:
            name: Skill name
            reason: Rejection reason
            
        Returns:
            True if rejected successfully
        """
        skill = self._loaded_skills.get(name)
        if skill:
            skill.security_status = "rejected"
            skill.updated_at = datetime.now(timezone.utc).isoformat()
            logging.warning(f"Skill {name} rejected: {reason}")
            return True
        return False


def create_sample_skill() -> Dict[str, Any]:
    """Create a sample skill manifest for testing"""
    return {
        "name": "brave_search",
        "version": "1.0.0",
        "author": "ai-founder-os",
        "source": "openclaw_hub",
        "description": "Brave Search API skill for web searching",
        "entrypoints": ["search", "news_search", "images_search"],
        "permissions": {
            "filesystem": {
                "read": ["/tmp", "/workspace/experiments"],
                "write": ["/workspace/experiments/outputs"]
            },
            "network": {
                "allow_domains": ["api.brave.com"],
                "deny_domains": []
            },
            "secrets": ["cap_search_brave"],
            "process": {
                "allow_commands": ["python", "pip"]
            }
        },
        "dependencies": ["requests"],
        "runtime": "python",
        "checks": ["python -m pytest tests/"],
        "quarantine": True,
        "security_status": "pending",
        "tags": ["search", "api", "web"]
    }


def create_dangerous_skill() -> Dict[str, Any]:
    """Create a deliberately dangerous skill manifest for testing"""
    return {
        "name": "dangerous_skill",
        "version": "1.0.0",
        "author": "malicious",
        "source": "private",
        "description": "A skill with dangerous permissions",
        "entrypoints": ["run_anything"],
        "permissions": {
            "filesystem": {
                "read": ["/"],
                "write": ["/etc", "/root"]
            },
            "network": {
                "allow_domains": ["*"],
                "deny_domains": []
            },
            "secrets": ["cap_admin", "cap_all"],
            "process": {
                "allow_commands": ["sudo", "rm -rf", "chmod 777"]
            }
        },
        "dependencies": [],
        "runtime": "bash",
        "quarantine": True,
        "security_status": "pending",
        "tags": []
    }
