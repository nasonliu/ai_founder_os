"""
AI Founder OS - Planner Commands Module

Realtime command interface for controlling the Planner.
Provides conversational command parsing and execution.
"""

import re
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum


class CommandType(Enum):
    """Command type categories"""
    TASK_CREATE = "task_create"
    TASK_QUEUE = "task_queue"
    TASK_ASSIGN = "task_assign"
    TASK_COMPLETE = "task_complete"
    TASK_CANCEL = "task_cancel"
    TASK_RETRY = "task_retry"
    TASK_STATUS = "task_status"
    PROJECT_CREATE = "project_create"
    PROJECT_STATUS = "project_status"
    SYSTEM_STATUS = "system_status"
    SYSTEM_PAUSE = "system_pause"
    SYSTEM_RESUME = "system_resume"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class Command:
    """Parsed command structure"""
    type: CommandType
    raw_input: str
    args: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # Confidence score for parsing
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "raw_input": self.raw_input,
            "args": self.args,
            "confidence": self.confidence,
            "error": self.error
        }


@dataclass
class CommandResult:
    """Command execution result"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    command: Optional[Command] = None
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "command": self.command.to_dict() if self.command else None
        }


class CommandParser:
    """
    Natural language command parser.
    
    Parses conversational input into structured commands.
    """
    
    # Command patterns - order matters (more specific first)
    PATTERNS = [
        # Task operations
        (r"^(?:create|make|add)\s+(?:a\s+)?task\s+(?:called\s+)?(.+?)(?:\s+for\s+(.+))?$", 
         CommandType.TASK_CREATE),
        (r"^queue\s+(?:task\s+)?(.+)$", CommandType.TASK_QUEUE),
        (r"^assign\s+(?:task\s+)?(.+?)\s+to\s+(.+)$", CommandType.TASK_ASSIGN),
        (r"^(?:complete|finish|done)\s+(?:task\s+)?(.+?)(?:\s+(success|fail|failed))?$", 
         CommandType.TASK_COMPLETE),
        (r"^cancel\s+(?:task\s+)?(.+)$", CommandType.TASK_CANCEL),
        (r"^retry\s+(?:task\s+)?(.+)$", CommandType.TASK_RETRY),
        (r"^(?:status|state)\s+(?:of\s+)?(?:task\s+)?(.+)$", CommandType.TASK_STATUS),
        
        # Project operations  
        (r"^(?:create|make|start)\s+(?:a\s+)?project\s+(?:called\s+)?(.+?)(?:\s+for\s+(.+))?$",
         CommandType.PROJECT_CREATE),
        (r"^(?:status|state)\s+(?:of\s+)?project\s+(.+)$", CommandType.PROJECT_STATUS),
        
        # System operations
        (r"^status$", CommandType.SYSTEM_STATUS),
        (r"^(?:show\s+)?(?:me\s+)?(?:the\s+)?status$", CommandType.SYSTEM_STATUS),
        (r"^pause$", CommandType.SYSTEM_PAUSE),
        (r"^resume$", CommandType.SYSTEM_RESUME),
        (r"^help$", CommandType.HELP),
        (r"^(?:show\s+)?help$", CommandType.HELP),
    ]
    
    def __init__(self):
        self._custom_patterns: List[tuple] = []
    
    def add_pattern(self, pattern: str, command_type: CommandType) -> None:
        """Add custom command pattern"""
        compiled = re.compile(pattern, re.IGNORECASE)
        self._custom_patterns.insert(0, (compiled, command_type))
    
    def parse(self, input_str: str) -> Command:
        """
        Parse natural language input into a Command.
        
        Args:
            input_str: Natural language command string
            
        Returns:
            Parsed Command object
        """
        if not input_str or not input_str.strip():
            return Command(
                type=CommandType.UNKNOWN,
                raw_input=input_str or "",
                error="Empty command"
            )
        
        input_str = input_str.strip()
        
        # Try custom patterns first
        all_patterns = self._custom_patterns + [
            (re.compile(p, re.IGNORECASE), t) 
            for p, t in self.PATTERNS
        ]
        
        for pattern, cmd_type in all_patterns:
            match = pattern.match(input_str)
            if match:
                args = self._extract_args(cmd_type, match.groups())
                return Command(
                    type=cmd_type,
                    raw_input=input_str,
                    args=args,
                    confidence=1.0
                )
        
        # No pattern matched
        return Command(
            type=CommandType.UNKNOWN,
            raw_input=input_str,
            error=f"Unknown command: {input_str}"
        )
    
    def _extract_args(self, cmd_type: CommandType, groups: tuple) -> Dict[str, Any]:
        """Extract structured args from regex match groups"""
        args = {}
        
        if not groups:
            return args
        
        if cmd_type == CommandType.TASK_CREATE:
            args["title"] = groups[0].strip() if groups[0] else ""
            args["project_ref"] = groups[1].strip() if len(groups) > 1 and groups[1] else None
            
        elif cmd_type == CommandType.TASK_QUEUE:
            args["task_ref"] = groups[0].strip() if groups[0] else ""
            
        elif cmd_type == CommandType.TASK_ASSIGN:
            args["task_ref"] = groups[0].strip() if groups[0] else ""
            args["worker_ref"] = groups[1].strip() if len(groups) > 1 and groups[1] else ""
            
        elif cmd_type == CommandType.TASK_COMPLETE:
            args["task_ref"] = groups[0].strip() if groups[0] else ""
            args["result"] = groups[1].strip() if len(groups) > 1 and groups[1] else "success"
            
        elif cmd_type == CommandType.TASK_CANCEL:
            args["task_ref"] = groups[0].strip() if groups[0] else ""
            
        elif cmd_type == CommandType.TASK_RETRY:
            args["task_ref"] = groups[0].strip() if groups[0] else ""
            
        elif cmd_type == CommandType.TASK_STATUS:
            args["task_ref"] = groups[0].strip() if groups[0] else ""
            
        elif cmd_type == CommandType.PROJECT_CREATE:
            args["name"] = groups[0].strip() if groups[0] else ""
            args["goal"] = groups[1].strip() if len(groups) > 1 and groups[1] else ""
            
        elif cmd_type == CommandType.PROJECT_STATUS:
            args["project_ref"] = groups[0].strip() if groups[0] else ""
            
        return args


class CommandExecutor:
    """
    Executes commands against the Planner.
    """
    
    def __init__(self, planner: Any):
        self.planner = planner
        self.paused = False
    
    def execute(self, command: Command) -> CommandResult:
        """
        Execute a parsed command.
        
        Args:
            command: Parsed Command object
            
        Returns:
            CommandResult with execution outcome
        """
        # Check if system is paused
        if self.paused and command.type not in [CommandType.SYSTEM_RESUME, CommandType.HELP]:
            return CommandResult(
                success=False,
                message="System is paused. Use 'resume' to continue.",
                command=command
            )
        
        # Dispatch to handler
        handlers = {
            CommandType.TASK_CREATE: self._handle_task_create,
            CommandType.TASK_QUEUE: self._handle_task_queue,
            CommandType.TASK_ASSIGN: self._handle_task_assign,
            CommandType.TASK_COMPLETE: self._handle_task_complete,
            CommandType.TASK_CANCEL: self._handle_task_cancel,
            CommandType.TASK_RETRY: self._handle_task_retry,
            CommandType.TASK_STATUS: self._handle_task_status,
            CommandType.PROJECT_CREATE: self._handle_project_create,
            CommandType.PROJECT_STATUS: self._handle_project_status,
            CommandType.SYSTEM_STATUS: self._handle_system_status,
            CommandType.SYSTEM_PAUSE: self._handle_system_pause,
            CommandType.SYSTEM_RESUME: self._handle_system_resume,
            CommandType.HELP: self._handle_help,
            CommandType.UNKNOWN: self._handle_unknown,
        }
        
        handler = handlers.get(command.type, self._handle_unknown)
        return handler(command)
    
    def _resolve_task_ref(self, ref: str) -> Optional[Any]:
        """Resolve task reference (ID, title, or partial match)"""
        if not ref:
            return None
        
        # Try exact ID match first
        if ref in self.planner.tasks:
            return self.planner.tasks[ref]
        
        # Try title match (case insensitive)
        for task in self.planner.tasks.values():
            if task.title.lower() == ref.lower():
                return task
        
        # Try partial title match
        ref_lower = ref.lower()
        for task in self.planner.tasks.values():
            if ref_lower in task.title.lower():
                return task
        
        return None
    
    def _resolve_project_ref(self, ref: str) -> Optional[Any]:
        """Resolve project reference (ID, name, or partial match)"""
        if not ref:
            return None
        
        # Try exact ID match
        if ref in self.planner.projects:
            return self.planner.projects[ref]
        
        # Try name match
        for proj in self.planner.projects.values():
            if proj.name.lower() == ref.lower():
                return proj
        
        # Try partial match
        ref_lower = ref.lower()
        for proj in self.planner.projects.values():
            if ref_lower in proj.name.lower():
                return proj
        
        return None
    
    def _handle_task_create(self, cmd: Command) -> CommandResult:
        """Handle task creation"""
        args = cmd.args
        title = args.get("title", "Untitled Task")
        project_ref = args.get("project_ref")
        
        # Resolve project
        project_id = None
        if project_ref:
            project = self._resolve_project_ref(project_ref)
            if project:
                project_id = project.id
            else:
                # Try using as direct ID
                project_id = project_ref
        
        if not project_id and self.planner.projects:
            # Use first available project
            project_id = list(self.planner.projects.keys())[0]
        
        if not project_id:
            return CommandResult(
                success=False,
                message="No project available. Create a project first.",
                command=cmd
            )
        
        task_data = {
            "project_id": project_id,
            "title": title,
            "goal": f"Task: {title}",
            "risk_level": "medium"
        }
        
        task = self.planner.create_task(task_data)
        
        return CommandResult(
            success=True,
            message=f"Created task '{task.title}' with ID {task.id}",
            data={"task_id": task.id, "title": task.title},
            command=cmd
        )
    
    def _handle_task_queue(self, cmd: Command) -> CommandResult:
        """Handle task queuing"""
        ref = cmd.args.get("task_ref", "")
        task = self._resolve_task_ref(ref)
        
        if not task:
            return CommandResult(
                success=False,
                message=f"Task not found: {ref}",
                command=cmd
            )
        
        if self.planner.queue_task(task.id):
            return CommandResult(
                success=True,
                message=f"Queued task '{task.title}'",
                data={"task_id": task.id},
                command=cmd
            )
        else:
            return CommandResult(
                success=False,
                message=f"Cannot queue task '{task.title}' (state: {task.state})",
                command=cmd
            )
    
    def _handle_task_assign(self, cmd: Command) -> CommandResult:
        """Handle task assignment"""
        task_ref = cmd.args.get("task_ref", "")
        worker_ref = cmd.args.get("worker_ref", "")
        
        task = self._resolve_task_ref(task_ref)
        if not task:
            return CommandResult(
                success=False,
                message=f"Task not found: {task_ref}",
                command=cmd
            )
        
        worker_id = worker_ref  # Use as-is (could integrate with worker registry)
        
        if self.planner.assign_task(task.id, worker_id):
            return CommandResult(
                success=True,
                message=f"Assigned task '{task.title}' to worker {worker_id}",
                data={"task_id": task.id, "worker_id": worker_id},
                command=cmd
            )
        else:
            return CommandResult(
                success=False,
                message=f"Cannot assign task '{task.title}'",
                command=cmd
            )
    
    def _handle_task_complete(self, cmd: Command) -> CommandResult:
        """Handle task completion"""
        ref = cmd.args.get("task_ref", "")
        result = cmd.args.get("result", "success")
        
        task = self._resolve_task_ref(ref)
        if not task:
            return CommandResult(
                success=False,
                message=f"Task not found: {ref}",
                command=cmd
            )
        
        success = result.lower() in ("success", "done")
        
        if self.planner.complete_task(task.id, success=success):
            status = "completed" if success else "failed"
            return CommandResult(
                success=True,
                message=f"Task '{task.title}' {status}",
                data={"task_id": task.id, "status": status},
                command=cmd
            )
        else:
            return CommandResult(
                success=False,
                message=f"Cannot complete task '{task.title}'",
                command=cmd
            )
    
    def _handle_task_cancel(self, cmd: Command) -> CommandResult:
        """Handle task cancellation"""
        ref = cmd.args.get("task_ref", "")
        task = self._resolve_task_ref(ref)
        
        if not task:
            return CommandResult(
                success=False,
                message=f"Task not found: {ref}",
                command=cmd
            )
        
        if task.state in ["created", "queued"]:
            task.state = "canceled"
            return CommandResult(
                success=True,
                message=f"Canceled task '{task.title}'",
                data={"task_id": task.id},
                command=cmd
            )
        else:
            return CommandResult(
                success=False,
                message=f"Cannot cancel task '{task.title}' (state: {task.state})",
                command=cmd
            )
    
    def _handle_task_retry(self, cmd: Command) -> CommandResult:
        """Handle task retry"""
        ref = cmd.args.get("task_ref", "")
        task = self._resolve_task_ref(ref)
        
        if not task:
            return CommandResult(
                success=False,
                message=f"Task not found: {ref}",
                command=cmd
            )
        
        if task.can_retry(max_retries=self.planner.retry_limit):
            task.state = "created"
            task.retry_count += 1
            return CommandResult(
                success=True,
                message=f"Retrying task '{task.title}' (attempt {task.retry_count})",
                data={"task_id": task.id, "retry_count": task.retry_count},
                command=cmd
            )
        else:
            return CommandResult(
                success=False,
                message=f"Cannot retry task '{task.title}' (max retries exceeded)",
                command=cmd
            )
    
    def _handle_task_status(self, cmd: Command) -> CommandResult:
        """Handle task status query"""
        ref = cmd.args.get("task_ref", "")
        
        if not ref:
            # List all tasks
            tasks = [
                {
                    "id": t.id,
                    "title": t.title,
                    "state": t.state,
                    "project_id": t.project_id
                }
                for t in self.planner.tasks.values()
            ]
            return CommandResult(
                success=True,
                message=f"Found {len(tasks)} tasks",
                data={"tasks": tasks},
                command=cmd
            )
        
        task = self._resolve_task_ref(ref)
        if not task:
            return CommandResult(
                success=False,
                message=f"Task not found: {ref}",
                command=cmd
            )
        
        return CommandResult(
            success=True,
            message=f"Task '{task.title}': {task.state}",
            data=self.planner.get_task_status(task.id),
            command=cmd
        )
    
    def _handle_project_create(self, cmd: Command) -> CommandResult:
        """Handle project creation"""
        from src.planner.planner import Project
        
        args = cmd.args
        name = args.get("name", "Untitled Project")
        goal = args.get("goal", "")
        
        project = Project(
            id=f"proj_{uuid.uuid4().hex[:8]}",
            name=name,
            one_sentence_goal=goal
        )
        self.planner.projects[project.id] = project
        
        return CommandResult(
            success=True,
            message=f"Created project '{project.name}' with ID {project.id}",
            data={"project_id": project.id, "name": project.name},
            command=cmd
        )
    
    def _handle_project_status(self, cmd: Command) -> CommandResult:
        """Handle project status query"""
        ref = cmd.args.get("project_ref", "")
        
        if not ref:
            # List all projects
            projects = [
                {
                    "id": p.id,
                    "name": p.name,
                    "status": p.status
                }
                for p in self.planner.projects.values()
            ]
            return CommandResult(
                success=True,
                message=f"Found {len(projects)} projects",
                data={"projects": projects},
                command=cmd
            )
        
        project = self._resolve_project_ref(ref)
        if not project:
            return CommandResult(
                success=False,
                message=f"Project not found: {ref}",
                command=cmd
            )
        
        return CommandResult(
            success=True,
            message=f"Project '{project.name}': {project.status}",
            data=self.planner.get_project_status(project.id),
            command=cmd
        )
    
    def _handle_system_status(self, cmd: Command) -> CommandResult:
        """Handle system status query"""
        status = self.planner.get_status_summary()
        
        blockers = self.planner.get_blockers()
        if blockers:
            status["blockers"] = blockers
        
        return CommandResult(
            success=True,
            message=f"System status: {status['total_tasks']} tasks, {status['queue_length']} queued",
            data=status,
            command=cmd
        )
    
    def _handle_system_pause(self, cmd: Command) -> CommandResult:
        """Handle system pause"""
        self.paused = True
        return CommandResult(
            success=True,
            message="System paused",
            data={"paused": True},
            command=cmd
        )
    
    def _handle_system_resume(self, cmd: Command) -> CommandResult:
        """Handle system resume"""
        self.paused = False
        return CommandResult(
            success=True,
            message="System resumed",
            data={"paused": False},
            command=cmd
        )
    
    def _handle_help(self, cmd: Command) -> CommandResult:
        """Handle help request"""
        help_text = {
            "commands": [
                {"pattern": "create task <title>", "description": "Create a new task"},
                {"pattern": "queue <task>", "description": "Queue a task for execution"},
                {"pattern": "assign <task> to <worker>", "description": "Assign task to worker"},
                {"pattern": "complete <task> [success|fail]", "description": "Mark task complete"},
                {"pattern": "cancel <task>", "description": "Cancel a task"},
                {"pattern": "retry <task>", "description": "Retry a failed task"},
                {"pattern": "status [task|project]", "description": "Get status info"},
                {"pattern": "create project <name>", "description": "Create a new project"},
                {"pattern": "pause", "description": "Pause the system"},
                {"pattern": "resume", "description": "Resume the system"},
                {"pattern": "status", "description": "Show system status"},
                {"pattern": "help", "description": "Show this help"},
            ]
        }
        
        return CommandResult(
            success=True,
            message="Available commands:",
            data=help_text,
            command=cmd
        )
    
    def _handle_unknown(self, cmd: Command) -> CommandResult:
        """Handle unknown command"""
        return CommandResult(
            success=False,
            message=cmd.error or "Unknown command. Type 'help' for available commands.",
            command=cmd
        )


class CommandInterface:
    """
    High-level command interface combining parser and executor.
    
    This is the main entry point for the Realtime Command Interface.
    """
    
    def __init__(self, planner: Any):
        self.planner = planner
        self.parser = CommandParser()
        self.executor = CommandExecutor(planner)
    
    def execute(self, input_str: str) -> CommandResult:
        """
        Parse and execute a command.
        
        Args:
            input_str: Natural language command string
            
        Returns:
            CommandResult with execution outcome
        """
        command = self.parser.parse(input_str)
        
        if command.type == CommandType.UNKNOWN and command.error:
            return CommandResult(
                success=False,
                message=command.error,
                command=command
            )
        
        return self.executor.execute(command)
    
    def add_custom_command(self, pattern: str, handler: Callable[[Command], CommandResult]) -> None:
        """
        Add a custom command handler.
        
        Args:
            pattern: Regex pattern for the command
            handler: Callable that handles the command
        """
        # This would require extending the executor to support custom handlers
        # For now, add pattern to parser
        self.parser.add_pattern(pattern, CommandType.UNKNOWN)
    
    def get_help(self) -> str:
        """Get help text"""
        result = self.execute("help")
        return result.message + "\n" + json.dumps(result.data, indent=2)


def create_command_interface(planner: Any) -> CommandInterface:
    """
    Factory function to create a CommandInterface.
    
    Args:
        planner: Planner instance to control
        
    Returns:
        CommandInterface instance
    """
    return CommandInterface(planner)


# Convenience function for direct command execution
def execute_command(planner: Any, command_str: str) -> CommandResult:
    """
    Execute a command string against a planner.
    
    Args:
        planner: Planner instance
        command_str: Command string to execute
        
    Returns:
        CommandResult
    """
    interface = create_command_interface(planner)
    return interface.execute(command_str)


if __name__ == "__main__":
    # Demo usage
    from src.planner.planner import create_planner, Project
    
    # Create planner
    planner = create_planner({"max_concurrency": 3, "retry_limit": 3})
    
    # Create a project
    project = Project(
        id="proj_001",
        name="AI Founder OS",
        one_sentence_goal="Build an AI-native operating system"
    )
    planner.projects[project.id] = project
    
    # Create command interface
    cmd_interface = create_command_interface(planner)
    
    # Demo commands
    commands = [
        "help",
        "create task Implement user authentication",
        "status",
        "queue task_001",
    ]
    
    print("=== Command Interface Demo ===\n")
    
    for cmd in commands:
        print(f"> {cmd}")
        result = cmd_interface.execute(cmd)
        print(f"  Success: {result.success}")
        print(f"  Message: {result.message}")
        if result.data:
            print(f"  Data: {json.dumps(result.data, indent=2)}")
        print()
