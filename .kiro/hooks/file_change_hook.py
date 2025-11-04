#!/usr/bin/env python3
"""
File Change Hook for ADK IDE Development

This hook automatically triggers when files are saved, created, or modified
to record development activities and maintain documentation.
"""

import sys
import os
from pathlib import Path

# Add the hooks directory to Python path
hooks_dir = Path(__file__).parent
sys.path.insert(0, str(hooks_dir))

from development_recorder import record_file_change, record_milestone

def on_file_save(file_path: str):
    """
    Triggered when a file is saved in the IDE
    
    Args:
        file_path: Path to the saved file
    """
    file_path = Path(file_path)
    
    # Determine change type and description based on file content and type
    change_type = "modified"
    description = ""
    
    # Check if this is a new file
    if not file_path.exists():
        return  # File doesn't exist, skip
        
    # Analyze file type and content for better description
    if file_path.suffix == '.py':
        description = analyze_python_file(file_path)
    elif file_path.suffix in ['.js', '.ts']:
        description = analyze_javascript_file(file_path)
    elif file_path.suffix == '.html':
        description = analyze_html_file(file_path)
    elif file_path.suffix == '.css':
        description = analyze_css_file(file_path)
    elif file_path.suffix == '.md':
        description = analyze_markdown_file(file_path)
    elif file_path.suffix in ['.json', '.yaml', '.yml']:
        description = analyze_config_file(file_path)
    
    # Record the file change
    record_file_change(str(file_path), change_type, description)
    
    # Check for milestone triggers
    check_milestone_triggers(file_path)

def on_file_create(file_path: str):
    """
    Triggered when a new file is created
    
    Args:
        file_path: Path to the created file
    """
    file_path = Path(file_path)
    
    description = f"Created new {file_path.suffix} file"
    
    # Add specific descriptions for important file types
    if file_path.name.startswith('adk_'):
        description = f"Created new ADK component: {file_path.stem}"
    elif 'agent' in file_path.name.lower():
        description = f"Created new agent implementation: {file_path.stem}"
    elif 'hook' in file_path.name.lower():
        description = f"Created new development hook: {file_path.stem}"
    elif file_path.suffix == '.html' and 'ide' in file_path.name.lower():
        description = f"Created IDE interface file: {file_path.name}"
    
    record_file_change(str(file_path), "created", description)
    
    # Check for milestone triggers
    check_milestone_triggers(file_path)

def on_file_delete(file_path: str):
    """
    Triggered when a file is deleted
    
    Args:
        file_path: Path to the deleted file
    """
    description = f"Deleted file: {Path(file_path).name}"
    record_file_change(file_path, "deleted", description)

def analyze_python_file(file_path: Path) -> str:
    """Analyze Python file content for meaningful description"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        descriptions = []
        
        # Check for ADK imports and components
        if 'from google.adk' in content or 'import google.adk' in content:
            descriptions.append("ADK integration")
            
        # Check for specific ADK components
        adk_components = [
            ('LlmAgent', 'LLM agent'),
            ('LoopAgent', 'loop agent'),
            ('SequentialAgent', 'sequential agent'),
            ('ParallelAgent', 'parallel agent'),
            ('BuiltInCodeExecutor', 'code executor'),
            ('SessionService', 'session service'),
            ('ArtifactService', 'artifact service')
        ]
        
        for component, desc in adk_components:
            if component in content:
                descriptions.append(f"implements {desc}")
                
        # Check for class definitions
        if 'class ' in content:
            class_count = content.count('class ')
            descriptions.append(f"{class_count} class{'es' if class_count > 1 else ''}")
            
        # Check for function definitions
        if 'def ' in content:
            func_count = content.count('def ')
            descriptions.append(f"{func_count} function{'s' if func_count > 1 else ''}")
            
        # Check for specific patterns
        if 'async def' in content:
            descriptions.append("async functions")
        if '@app.route' in content or 'FastAPI' in content:
            descriptions.append("web endpoints")
        if 'WebSocket' in content:
            descriptions.append("WebSocket handling")
            
        return "Python file: " + ", ".join(descriptions) if descriptions else "Python file updated"
        
    except Exception:
        return "Python file updated"

def analyze_javascript_file(file_path: Path) -> str:
    """Analyze JavaScript/TypeScript file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        descriptions = []
        
        # Check for specific patterns
        if 'class ' in content:
            descriptions.append("class definitions")
        if 'function ' in content or '=>' in content:
            descriptions.append("functions")
        if 'WebSocket' in content:
            descriptions.append("WebSocket client")
        if 'monaco' in content.lower():
            descriptions.append("Monaco editor integration")
        if 'addEventListener' in content:
            descriptions.append("event handlers")
        if 'fetch(' in content or 'axios' in content:
            descriptions.append("API calls")
            
        file_type = "TypeScript" if file_path.suffix == '.ts' else "JavaScript"
        return f"{file_type} file: " + ", ".join(descriptions) if descriptions else f"{file_type} file updated"
        
    except Exception:
        return f"{file_path.suffix[1:].upper()} file updated"

def analyze_html_file(file_path: Path) -> str:
    """Analyze HTML file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        descriptions = []
        
        # Check for specific patterns
        if 'ide' in file_path.name.lower() or 'editor' in content.lower():
            descriptions.append("IDE interface")
        if 'voice' in content.lower():
            descriptions.append("voice interface")
        if '<canvas' in content:
            descriptions.append("canvas elements")
        if 'WebSocket' in content:
            descriptions.append("WebSocket integration")
        if 'monaco' in content.lower():
            descriptions.append("Monaco editor")
            
        return "HTML file: " + ", ".join(descriptions) if descriptions else "HTML file updated"
        
    except Exception:
        return "HTML file updated"

def analyze_css_file(file_path: Path) -> str:
    """Analyze CSS file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        descriptions = []
        
        # Check for specific patterns
        if '.ide' in content or '#ide' in content:
            descriptions.append("IDE styling")
        if 'grid' in content:
            descriptions.append("CSS Grid layout")
        if 'flexbox' in content or 'flex' in content:
            descriptions.append("Flexbox layout")
        if '@media' in content:
            descriptions.append("responsive design")
        if 'animation' in content or 'transition' in content:
            descriptions.append("animations")
            
        return "CSS file: " + ", ".join(descriptions) if descriptions else "CSS file updated"
        
    except Exception:
        return "CSS file updated"

def analyze_markdown_file(file_path: Path) -> str:
    """Analyze Markdown file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        descriptions = []
        
        # Check for specific patterns
        if file_path.name.upper().startswith('README'):
            descriptions.append("project documentation")
        elif 'requirements' in file_path.name.lower():
            descriptions.append("requirements specification")
        elif 'api' in file_path.name.lower():
            descriptions.append("API documentation")
        elif 'development' in file_path.name.lower():
            descriptions.append("development documentation")
            
        # Count headers
        header_count = content.count('\n#')
        if header_count > 0:
            descriptions.append(f"{header_count} sections")
            
        return "Documentation: " + ", ".join(descriptions) if descriptions else "Documentation updated"
        
    except Exception:
        return "Documentation updated"

def analyze_config_file(file_path: Path) -> str:
    """Analyze configuration file content"""
    try:
        descriptions = []
        
        if 'package.json' in file_path.name:
            descriptions.append("Node.js package configuration")
        elif 'requirements.txt' in file_path.name:
            descriptions.append("Python dependencies")
        elif 'docker' in file_path.name.lower():
            descriptions.append("Docker configuration")
        elif 'adk' in file_path.name.lower():
            descriptions.append("ADK configuration")
        else:
            descriptions.append("configuration file")
            
        return "Config: " + ", ".join(descriptions) if descriptions else "Configuration updated"
        
    except Exception:
        return "Configuration file updated"

def check_milestone_triggers(file_path: Path):
    """Check if file changes trigger milestone recording"""
    
    # Check for Kiro settings changes that affect development workflow
    if 'settings.json' in str(file_path) and 'Kiro' in str(file_path):
        record_milestone(
            'development_environment_updated',
            'Kiro development environment configuration updated',
            [str(file_path)]
        )
    
    # Define milestone triggers
    milestone_triggers = {
        # Architecture milestones
        'adk_architecture_complete': {
            'files': ['adk_multi_agent_system.py', 'adk_workflow_orchestrator.py'],
            'description': 'ADK multi-agent architecture implementation completed'
        },
        
        # Core component milestones
        'code_execution_ready': {
            'files': ['adk_code_executor.py', 'adk_execution_manager.py'],
            'description': 'Code execution system implementation completed'
        },
        
        # IDE component milestones
        'ide_foundation_complete': {
            'files': ['ide_interface.html', 'ide_controller.js', 'ide_styles.css'],
            'description': 'IDE foundation components implemented'
        },
        
        'editor_integration_complete': {
            'files': ['monaco_integration.js', 'code_editor_agent.py'],
            'description': 'Code editor integration with ADK completed'
        },
        
        # Safety and security milestones
        'safety_system_active': {
            'files': ['adk_safety_callbacks.py', 'security_policies.py'],
            'description': 'Safety and security system implementation completed'
        },
        
        # Documentation milestones
        'documentation_complete': {
            'files': ['API_REFERENCE.md', 'DEVELOPMENT_GUIDE.md', 'USER_MANUAL.md'],
            'description': 'Comprehensive documentation completed'
        }
    }
    
    # Check each milestone trigger
    for milestone_name, trigger_info in milestone_triggers.items():
        trigger_files = trigger_info['files']
        
        # Check if the current file is one of the trigger files
        if file_path.name in trigger_files:
            # Check if all trigger files exist
            project_root = find_project_root()
            all_files_exist = True
            existing_files = []
            
            for trigger_file in trigger_files:
                # Search for the file in the project
                found = False
                for root, dirs, files in os.walk(project_root):
                    if trigger_file in files:
                        existing_files.append(os.path.join(root, trigger_file))
                        found = True
                        break
                        
                if not found:
                    all_files_exist = False
                    break
                    
            # If all files exist, record the milestone
            if all_files_exist:
                record_milestone(
                    milestone_name,
                    trigger_info['description'],
                    existing_files
                )

def find_project_root() -> Path:
    """Find the project root directory"""
    current = Path.cwd()
    
    # Look for common project root indicators
    indicators = ['.git', '.kiro', 'package.json', 'requirements.txt', 'pyproject.toml']
    
    while current != current.parent:
        if any((current / indicator).exists() for indicator in indicators):
            return current
        current = current.parent
        
    return Path.cwd()

# Hook entry points for Kiro IDE
def main():
    """Main entry point for the hook"""
    if len(sys.argv) < 3:
        print("Usage: file_change_hook.py <action> <file_path>")
        sys.exit(1)
        
    action = sys.argv[1]
    file_path = sys.argv[2]
    
    if action == "save":
        on_file_save(file_path)
    elif action == "create":
        on_file_create(file_path)
    elif action == "delete":
        on_file_delete(file_path)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()