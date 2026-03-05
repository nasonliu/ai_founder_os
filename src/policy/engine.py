"""
AI Founder OS - Policy Engine

The Policy Engine is responsible for system governance across three policy layers:
- Execution Policy: Task validation, concurrency, retry, slowdown
- Safety Policy: Secret isolation, network control, capability enforcement
- Quality Policy: Validator requirements, evidence standards, verifier independence, KPI gate

This module provides policy enforcement for all system operations.
"""

import json
import re
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolicyType(Enum):
    """Policy evaluation types"""
    EXECUTION = "execution"
    SAFETY = "safety"
    QUALITY = "quality"


class ValidationResult(Enum):
    """Policy validation results"""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    BLOCK = "block"


class OperatingMode(Enum):
    """System operating modes"""
    SAFE = "safe"
    NORMAL = "normal"
    TURBO = "turbo"


class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PolicyViolation:
    """Represents a policy violation"""
    policy_type: str
    rule: str
    severity: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


@dataclass
class PolicyCheckResult:
    """Result of a policy check"""
    result: ValidationResult
    policy_type: PolicyType
    violations: List[PolicyViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def passed(self) -> bool:
        return self.result in [ValidationResult.PASS, ValidationResult.WARN]
    
    @property
    def blocked(self) -> bool:
        return self.result == ValidationResult.BLOCK


class PolicyBase(ABC):
    """Base class for all policies"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.violations: List[PolicyViolation] = []
    
    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> PolicyCheckResult:
        """Evaluate policy against context"""
        pass
    
    def _create_violation(self, rule: str, severity: str, 
                         message: str, details: Dict = None) -> PolicyViolation:
        """Create a policy violation"""
        return PolicyViolation(
            policy_type=self.__class__.__name__,
            rule=rule,
            severity=severity,
            message=message,
            details=details or {}
        )


class ExecutionPolicy(PolicyBase):
    """
    Execution Policy handles task execution rules.
    
    Rules:
    - Each Task must have goal, inputs, expected_artifact, validator, risk_level
    - Failure handling with auto-slowdown after 3 consecutive failures
    - Concurrency control based on operating mode
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        # Default concurrency limits by mode
        self.concurrency_limits = {
            "safe": 1,
            "normal": 3,
            "turbo": 5
        }
        self.default_retry_limit = 3
        self.slowdown_threshold = 3
    
    def evaluate(self, context: Dict[str, Any]) -> PolicyCheckResult:
        """Evaluate execution policy"""
        violations = []
        warnings = []
        metadata = {}
        
        task = context.get("task")
        project = context.get("project")
        
        if not task:
            violations.append(self._create_violation(
                "task_required",
                "high",
                "Task is required for execution policy evaluation"
            ))
            return PolicyCheckResult(
                result=ValidationResult.BLOCK,
                policy_type=PolicyType.EXECUTION,
                violations=violations
            )
        
        # Rule 1: Task must have required fields
        required_fields = ["goal", "inputs", "expected_artifact", "validators", "risk_level"]
        missing_fields = [f for f in required_fields if not task.get(f) and task.get(f) != {}]
        
        if missing_fields:
            violations.append(self._create_violation(
                "missing_required_fields",
                "high",
                f"Task missing required fields: {missing_fields}",
                {"missing": missing_fields}
            ))
        
        # Rule 2: Validators must have at least one blocking validator
        validators = task.get("validators", [])
        if not validators:
            violations.append(self._create_violation(
                "no_validators",
                "high",
                "Task must have at least one validator"
            ))
        else:
            blocking_validators = [v for v in validators if v.get("blocking", False)]
            if not blocking_validators:
                # Warn but don't fail - non-blocking validators are still valid
                warnings.append("Task should have at least one blocking validator (non-blocking validators present)")
        
        # Rule 3: Check retry limits
        retry_count = task.get("retry_count", 0)
        project_retry_limit = project.get("execution_limits", {}).get("retry_limit") if project else None
        retry_limit = project_retry_limit or self.default_retry_limit
        
        if retry_count >= retry_limit:
            violations.append(self._create_violation(
                "retry_limit_exceeded",
                "high",
                f"Task has exceeded retry limit ({retry_count}/{retry_limit})",
                {"retry_count": retry_count, "retry_limit": retry_limit}
            ))
        
        # Rule 4: Concurrency control based on operating mode
        if project:
            operating_mode = project.get("operating_mode", "normal")
            max_concurrency = project.get("execution_limits", {}).get("max_concurrency")
            
            if not max_concurrency:
                max_concurrency = self.concurrency_limits.get(operating_mode, 3)
            
            current_concurrency = context.get("current_concurrency", 0)
            metadata["operating_mode"] = operating_mode
            metadata["max_concurrency"] = max_concurrency
            metadata["current_concurrency"] = current_concurrency
            
            if current_concurrency >= max_concurrency:
                violations.append(self._create_violation(
                    "concurrency_limit",
                    "medium",
                    f"Concurrency limit reached ({current_concurrency}/{max_concurrency})",
                    {"current": current_concurrency, "max": max_concurrency}
                ))
        
        # Rule 5: Risk level validation
        risk_level = task.get("risk_level", "low")
        if risk_level not in ["low", "medium", "high"]:
            violations.append(self._create_violation(
                "invalid_risk_level",
                "medium",
                f"Invalid risk level: {risk_level}"
            ))
        
        # Determine result
        high_severity = [v for v in violations if v.severity == "high"]
        if high_severity:
            result = ValidationResult.BLOCK
        elif violations:
            result = ValidationResult.FAIL
        elif warnings:
            result = ValidationResult.WARN
        else:
            result = ValidationResult.PASS
        
        return PolicyCheckResult(
            result=result,
            policy_type=PolicyType.EXECUTION,
            violations=violations,
            warnings=warnings,
            metadata=metadata
        )
    
    def check_concurrency(self, operating_mode: str, current: int) -> PolicyCheckResult:
        """Check if concurrency is within limits"""
        max_allowed = self.concurrency_limits.get(operating_mode, 3)
        
        violations = []
        if current >= max_allowed:
            violations.append(self._create_violation(
                "concurrency_exceeded",
                "medium",
                f"Current concurrency {current} exceeds limit {max_allowed} for {operating_mode} mode"
            ))
        
        return PolicyCheckResult(
            result=ValidationResult.BLOCK if violations else ValidationResult.PASS,
            policy_type=PolicyType.EXECUTION,
            violations=violations,
            metadata={"current": current, "max_allowed": max_allowed}
        )
    
    def should_slowdown(self, consecutive_failures: int) -> bool:
        """Check if auto-slowdown should be triggered"""
        return consecutive_failures >= self.slowdown_threshold


class SafetyPolicy(PolicyBase):
    """
    Safety Policy handles security rules.
    
    Rules:
    - Secrets must not go to git, logs, or prompts
    - Workers only get capability tokens, not credentials
    - Network access controlled by skill manifest whitelist
    - Incident detection and response
    """
    
    # Secret patterns to detect
    SECRET_PATTERNS = [
        (r"sk-[a-zA-Z0-9]{20,}", "OpenAI API Key"),
        (r"sk-ant-[a-zA-Z0-9_-]{20,}", "Anthropic API Key"),
        (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
        (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
        (r"xoxb-[a-zA-Z0-9-]{20,}", "Slack Bot Token"),
        (r"xoxp-[a-zA-Z0-9-]{20,}", "Slack User Token"),
        (r"AIza[0-9A-Za-z_-]{35}", "Google API Key"),
        (r"ya29\.[0-9A-Za-z_-]+", "Google OAuth Token"),
    ]
    
    # Forbidden paths for secrets
    FORBIDDEN_PATHS = [
        "git",
        "log",
        "prompt",
        "memory"
    ]
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.blocked_domains: Set[str] = set()
        self.incidents: List[Dict] = []
    
    def evaluate(self, context: Dict[str, Any]) -> PolicyCheckResult:
        """Evaluate safety policy"""
        violations = []
        warnings = []
        metadata = {}
        
        # Check for secret leakage in content
        content = context.get("content", "")
        if content:
            leaked_secrets = self._detect_secrets(content)
            if leaked_secrets:
                for secret_type, _ in leaked_secrets:
                    violations.append(self._create_violation(
                        "secret_detected",
                        "critical",
                        f"Potential secret detected: {secret_type}",
                        {"secret_type": secret_type}
                    ))
        
        # Check if credentials are being exposed
        if context.get("has_credentials"):
            violations.append(self._create_violation(
                "credentials_exposed",
                "critical",
                "Credentials should not be exposed to workers"
            ))
        
        # Check network access
        target = context.get("target")
        if target:
            allowed_domains = context.get("allowed_domains", [])
            if not self._is_network_allowed(target, allowed_domains):
                violations.append(self._create_violation(
                    "network_blocked",
                    "high",
                    f"Network access to {target} is not allowed",
                    {"target": target, "allowed": allowed_domains}
                ))
        
        # Check worker capability tokens
        worker = context.get("worker")
        if worker and context.get("check_tokens"):
            if not self._validate_capability_tokens(worker, context.get("required_capabilities", [])):
                violations.append(self._create_violation(
                    "insufficient_capabilities",
                    "high",
                    "Worker does not have required capability tokens"
                ))
        
        # Determine result
        critical = [v for v in violations if v.severity == "critical"]
        if critical:
            result = ValidationResult.BLOCK
        elif [v for v in violations if v.severity == "high"]:
            result = ValidationResult.FAIL
        elif violations:
            result = ValidationResult.WARN
        else:
            result = ValidationResult.PASS
        
        return PolicyCheckResult(
            result=result,
            policy_type=PolicyType.SAFETY,
            violations=violations,
            warnings=warnings,
            metadata=metadata
        )
    
    def _detect_secrets(self, content: str) -> List[tuple]:
        """Detect potential secrets in content"""
        detected = []
        for pattern, secret_type in self.SECRET_PATTERNS:
            if re.search(pattern, content):
                detected.append((secret_type, pattern))
        return detected
    
    def _is_network_allowed(self, target: str, allowed_domains: List[str]) -> bool:
        """Check if network target is allowed"""
        if not allowed_domains:
            return False
        
        # Simple domain matching
        for domain in allowed_domains:
            if domain in target or domain == "*":
                return True
        return False
    
    def _validate_capability_tokens(self, worker: Dict, required: List[str]) -> bool:
        """Validate worker has required capability tokens"""
        worker_tokens = worker.get("capability_tokens", [])
        return all(cap in worker_tokens for cap in required)
    
    def check_secret_leak(self, content: str, context_type: str) -> PolicyCheckResult:
        """Check if content contains secrets in forbidden context"""
        violations = []
        
        # Check for forbidden path usage
        if context_type in self.FORBIDDEN_PATHS:
            leaked = self._detect_secrets(content)
            if leaked:
                for secret_type, _ in leaked:
                    violations.append(self._create_violation(
                        "secret_in_forbidden_context",
                        "critical",
                        f"Secret type {secret_type} found in forbidden context: {context_type}",
                        {"secret_type": secret_type, "context": context_type}
                    ))
        
        return PolicyCheckResult(
            result=ValidationResult.BLOCK if violations else ValidationResult.PASS,
            policy_type=PolicyType.SAFETY,
            violations=violations,
            metadata={"context_type": context_type}
        )
    
    def create_incident(self, incident_type: str, severity: str, 
                       details: Dict) -> Dict:
        """Create a security incident record"""
        incident = {
            "id": f"inc_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "type": incident_type,
            "severity": severity,
            "details": details,
            "status": "open",
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        self.incidents.append(incident)
        
        logger.warning(f"Security incident created: {incident['id']} - {incident_type}")
        
        return incident
    
    def get_incidents(self, status: Optional[str] = None) -> List[Dict]:
        """Get incidents, optionally filtered by status"""
        if status:
            return [i for i in self.incidents if i.get("status") == status]
        return self.incidents


class QualityPolicy(PolicyBase):
    """
    Quality Policy handles quality rules.
    
    Rules:
    - Each Task must have at least 1 validator with blocking=true
    - Evidence Pack must be complete with artifact refs, repro command, validation result
    - Verifier must be independent from Builder
    - KPI Gate: Project must have KPIs, and they must be met to continue
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.kpi_thresholds = config.get("kpi_thresholds", {}) if config else {}
    
    def evaluate(self, context: Dict[str, Any]) -> PolicyCheckResult:
        """Evaluate quality policy"""
        violations = []
        warnings = []
        metadata = {}
        
        task = context.get("task")
        project = context.get("project")
        evidence = context.get("evidence_pack")
        
        # Rule 1: Validator requirements
        if task:
            validators = task.get("validators", [])
            if not validators:
                violations.append(self._create_violation(
                    "no_validator",
                    "high",
                    "Task must have at least one validator"
                ))
            else:
                blocking = [v for v in validators if v.get("blocking")]
                if not blocking:
                    violations.append(self._create_violation(
                        "no_blocking_validator",
                        "high",
                        "Task must have at least one blocking validator"
                    ))
                metadata["validator_count"] = len(validators)
                metadata["blocking_count"] = len(blocking)
        
        # Rule 2: Evidence Pack completeness
        if evidence:
            required_evidence = ["artifact_ids", "validation", "repro"]
            missing_evidence = [e for e in required_evidence if not evidence.get(e)]
            
            if missing_evidence:
                violations.append(self._create_violation(
                    "incomplete_evidence",
                    "medium",
                    f"Evidence Pack missing: {missing_evidence}",
                    {"missing": missing_evidence}
                ))
            
            # Check repro command
            repro = evidence.get("repro", {})
            if not repro.get("commands"):
                violations.append(self._create_violation(
                    "no_repro_command",
                    "high",
                    "Evidence Pack must include repro command"
                ))
        
        # Rule 3: Verifier independence
        if context.get("builder_id") and context.get("verifier_id"):
            if context["builder_id"] == context["verifier_id"]:
                violations.append(self._create_violation(
                    "verifier_not_independent",
                    "high",
                    "Verifier must be independent from Builder"
                ))
        
        # Rule 4: KPI Gate
        if project:
            kpis = project.get("kpis", [])
            if not kpis:
                warnings.append("Project has no KPIs defined")
            else:
                # Check if KPI results are provided
                kpi_results = context.get("kpi_results", {})
                for kpi in kpis:
                    kpi_name = kpi.get("name")
                    if kpi_name in kpi_results:
                        result = kpi_results[kpi_name]
                        target = kpi.get("target")
                        
                        # Simple threshold check (can be extended)
                        if not self._check_kpi_threshold(result, target):
                            violations.append(self._create_violation(
                                "kpi_not_met",
                                "high",
                                f"KPI '{kpi_name}' not met: got {result}, expected {target}",
                                {"kpi": kpi_name, "result": result, "target": target}
                            ))
                metadata["kpi_count"] = len(kpis)
        
        # Determine result
        high_severity = [v for v in violations if v.severity == "high"]
        if high_severity:
            result = ValidationResult.BLOCK
        elif violations:
            result = ValidationResult.FAIL
        elif warnings:
            result = ValidationResult.WARN
        else:
            result = ValidationResult.PASS
        
        return PolicyCheckResult(
            result=result,
            policy_type=PolicyType.QUALITY,
            violations=violations,
            warnings=warnings,
            metadata=metadata
        )
    
    def _check_kpi_threshold(self, result: Any, target: str) -> bool:
        """Check if KPI result meets threshold"""
        # Simple implementation - can be extended
        try:
            # Try numeric comparison
            result_num = float(result)
            # Parse target like ">=80%" or "<100ms"
            if ">=" in target:
                threshold = float(target.replace(">=", "").replace("%", ""))
                return result_num >= threshold
            elif "<=" in target:
                threshold = float(target.replace("<=", "").replace("%", ""))
                return result_num <= threshold
            elif ">" in target:
                threshold = float(target.replace(">", "").replace("%", ""))
                return result_num > threshold
            elif "<" in target:
                threshold = float(target.replace("<", "").replace("%", ""))
                return result_num < threshold
        except (ValueError, TypeError):
            # Non-numeric comparison
            return str(result) == target
        
        return True
    
    def check_verifier_independence(self, builder_id: str, 
                                    verifier_id: str) -> PolicyCheckResult:
        """Check if verifier is independent from builder"""
        violations = []
        
        if builder_id == verifier_id:
            violations.append(self._create_violation(
                "verifier_not_independent",
                "high",
                f"Verifier {verifier_id} is the same as Builder {builder_id}"
            ))
        
        return PolicyCheckResult(
            result=ValidationResult.BLOCK if violations else ValidationResult.PASS,
            policy_type=PolicyType.QUALITY,
            violations=violations,
            metadata={"builder_id": builder_id, "verifier_id": verifier_id}
        )


class PolicyEngine:
    """
    Main Policy Engine that orchestrates all three policy layers.
    
    The Policy Engine evaluates actions through all three policy layers
    in sequence: Execution -> Safety -> Quality
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Initialize policies
        self.execution_policy = ExecutionPolicy(self.config.get("execution"))
        self.safety_policy = SafetyPolicy(self.config.get("safety"))
        self.quality_policy = QualityPolicy(self.config.get("quality"))
        
        # Policy evaluation history
        self.evaluation_history: List[PolicyCheckResult] = []
        
        # Global state
        self.operating_mode = OperatingMode.NORMAL
        self.consecutive_failures = 0
        self.kill_switch_armed = False
    
    @property
    def execution_mode(self) -> OperatingMode:
        """Alias for operating_mode for backward compatibility"""
        return self.operating_mode
    
    def set_execution_mode(self, mode: str) -> None:
        """
        Set the execution mode.
        
        Args:
            mode: One of 'safe', 'normal', or 'turbo'
        """
        mode_lower = mode.lower()
        if mode_lower == 'safe':
            self.operating_mode = OperatingMode.SAFE
        elif mode_lower == 'normal':
            self.operating_mode = OperatingMode.NORMAL
        elif mode_lower == 'turbo':
            self.operating_mode = OperatingMode.TURBO
        else:
            raise ValueError(f"Unknown execution mode: {mode}. Must be 'safe', 'normal', or 'turbo'")
    
    def get_incidents(self, status: Optional[str] = None) -> List[Dict]:
        """Get incidents from safety policy"""
        return self.safety_policy.get_incidents(status)
    
    def evaluate(self, context: Dict[str, Any], 
                 policy_types: Optional[List[PolicyType]] = None) -> PolicyCheckResult:
        """
        Evaluate context through specified policies.
        
        If policy_types is None, evaluates all three policies in order:
        Execution -> Safety -> Quality
        
        Returns aggregated result from all policies.
        """
        if policy_types is None:
            policy_types = [PolicyType.EXECUTION, PolicyType.SAFETY, PolicyType.QUALITY]
        
        all_violations = []
        all_warnings = []
        metadata = {}
        
        for policy_type in policy_types:
            if policy_type == PolicyType.EXECUTION:
                result = self.execution_policy.evaluate(context)
            elif policy_type == PolicyType.SAFETY:
                result = self.safety_policy.evaluate(context)
            elif policy_type == PolicyType.QUALITY:
                result = self.quality_policy.evaluate(context)
            else:
                continue
            
            all_violations.extend(result.violations)
            all_warnings.extend(result.warnings)
            metadata[policy_type.value] = result.metadata
            
            # If blocked, stop further evaluation
            if result.blocked:
                logger.warning(f"Policy {policy_type} blocked: {result.violations}")
                break
        
        # Determine final result - high severity violations are blocking for task execution
        critical = [v for v in all_violations if v.severity == "critical"]
        high = [v for v in all_violations if v.severity == "high"]
        
        if critical:
            final_result = ValidationResult.BLOCK
        elif high:
            # High severity violations are blocking for task execution
            final_result = ValidationResult.BLOCK
        elif all_violations:
            final_result = ValidationResult.WARN
        elif all_warnings:
            final_result = ValidationResult.WARN
        else:
            final_result = ValidationResult.PASS
        
        final_check = PolicyCheckResult(
            result=final_result,
            policy_type=PolicyType.EXECUTION,  # Placeholder
            violations=all_violations,
            warnings=all_warnings,
            metadata=metadata
        )
        
        self.evaluation_history.append(final_check)
        
        return final_check
    
    def check_task_execution(self, task: Dict, project: Dict,
                           current_concurrency: int = 0) -> PolicyCheckResult:
        """Check if a task can be executed"""
        context = {
            "task": task,
            "project": project,
            "current_concurrency": current_concurrency
        }
        return self.evaluate(context)
    
    def check_worker_assignment(self, task: Dict, worker: Dict,
                               project: Dict) -> PolicyCheckResult:
        """Check if a worker can be assigned to a task"""
        context = {
            "task": task,
            "worker": worker,
            "project": project,
            "check_tokens": True,
            "required_capabilities": task.get("required_capabilities", [])
        }
        return self.evaluate(context)
    
    def check_evidence_pack(self, evidence: Dict, task: Dict,
                          builder_id: str, verifier_id: str) -> PolicyCheckResult:
        """Check if an evidence pack meets quality standards"""
        # Only check evidence-specific rules, not task validators
        context = {
            "evidence_pack": evidence,
            "builder_id": builder_id,
            "verifier_id": verifier_id
        }
        
        # Only evaluate quality policy for evidence
        result = self.quality_policy.evaluate(context)
        return result
    
    def check_kpi_gate(self, project: Dict, kpi_results: Dict) -> PolicyCheckResult:
        """Check if project KPIs are met"""
        context = {
            "project": project,
            "kpi_results": kpi_results
        }
        
        # Only evaluate quality policy for KPIs
        result = self.quality_policy.evaluate(context)
        return result
    
    def check_secret_leakage(self, content: str, 
                           context_type: str) -> PolicyCheckResult:
        """Check for secret leakage in content"""
        context = {
            "content": content,
            "context_type": context_type
        }
        
        # Only evaluate safety policy for secrets
        result = self.safety_policy.check_secret_leak(content, context_type)
        return result
    
    def trigger_slowdown(self) -> Dict:
        """Trigger auto-slowdown due to consecutive failures"""
        self.consecutive_failures += 1
        
        if self.execution_policy.should_slowdown(self.consecutive_failures):
            # Determine new concurrency limit
            old_mode = self.operating_mode
            if self.operating_mode == OperatingMode.TURBO:
                self.operating_mode = OperatingMode.NORMAL
            elif self.operating_mode == OperatingMode.NORMAL:
                self.operating_mode = OperatingMode.SAFE
            
            # Create incident
            incident = self.safety_policy.create_incident(
                "auto_slowdown",
                "medium",
                {
                    "consecutive_failures": self.consecutive_failures,
                    "old_mode": old_mode.value,
                    "new_mode": self.operating_mode.value
                }
            )
            
            return {
                "slowdown_triggered": True,
                "new_mode": self.operating_mode.value,
                "incident": incident
            }
        
        return {
            "slowdown_triggered": False,
            "consecutive_failures": self.consecutive_failures
        }
    
    def reset_slowdown(self) -> None:
        """Reset slowdown mode"""
        self.consecutive_failures = 0
        self.operating_mode = OperatingMode.NORMAL
    
    def activate_kill_switch(self, reason: str) -> Dict:
        """Activate emergency kill switch"""
        self.kill_switch_armed = True
        
        incident = self.safety_policy.create_incident(
            "kill_switch",
            "critical",
            {"reason": reason}
        )
        
        return {
            "kill_switch_armed": True,
            "incident": incident,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_violation_summary(self) -> Dict:
        """Get summary of recent violations"""
        recent = self.evaluation_history[-100:]  # Last 100 evaluations
        
        by_type = {}
        by_severity = {}
        
        for check in recent:
            for violation in check.violations:
                # By type
                policy = violation.policy_type
                by_type[policy] = by_type.get(policy, 0) + 1
                
                # By severity
                sev = violation.severity
                by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_violations": sum(by_type.values()),
            "by_policy_type": by_type,
            "by_severity": by_severity,
            "recent_checks": len(recent)
        }
    
    def get_status(self) -> Dict:
        """Get policy engine status"""
        return {
            "operating_mode": self.operating_mode.value,
            "consecutive_failures": self.consecutive_failures,
            "kill_switch_armed": self.kill_switch_armed,
            "violation_summary": self.get_violation_summary(),
            "incidents": self.safety_policy.get_incidents()
        }


def create_policy_engine(config: Optional[Dict] = None) -> PolicyEngine:
    """Factory function to create a Policy Engine"""
    return PolicyEngine(config)


# Convenience functions
def validate_task(task: Dict, project: Dict, 
                 concurrency: int = 0) -> PolicyCheckResult:
    """Quick validation of a task"""
    engine = create_policy_engine()
    return engine.check_task_execution(task, project, concurrency)


def check_secrets(content: str, context: str) -> bool:
    """Quick secret check"""
    engine = create_policy_engine()
    result = engine.check_secret_leakage(content, context)
    return result.passed


if __name__ == "__main__":
    # Demo usage
    engine = create_policy_engine()
    
    # Sample task
    task = {
        "id": "task_001",
        "project_id": "proj_001",
        "title": "Implement Feature",
        "goal": "Build a new feature",
        "inputs": {"documents": ["doc1.md"]},
        "expected_artifact": {"type": "code", "path_hint": "src/feature.py"},
        "validators": [
            {"id": "val_001", "type": "unit_test", "command": "pytest", "blocking": True}
        ],
        "risk_level": "medium"
    }
    
    # Sample project
    project = {
        "id": "proj_001",
        "name": "AI Founder OS",
        "operating_mode": "normal",
        "execution_limits": {"max_concurrency": 3, "retry_limit": 3},
        "kpis": []
    }
    
    # Test execution policy
    result = engine.check_task_execution(task, project, current_concurrency=1)
    
    print(f"Policy Check Result: {result.result.value}")
    print(f"Violations: {len(result.violations)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Metadata: {result.metadata}")
    
    # Test secret detection
    secret_result = engine.check_secret_leakage(
        "My API key is sk-1234567890abcdefghij",
        "log"
    )
    print(f"\nSecret Check Result: {secret_result.result.value}")
    print(f"Violations: {len(secret_result.violations)}")
