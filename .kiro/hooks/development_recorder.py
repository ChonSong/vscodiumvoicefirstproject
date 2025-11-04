#!/usr/bin/env python3
"""
ADK Development Process Recording Hook

This hook automatically records development activities, maintains documentation,
and tracks progress during the ADK IDE implementation process.
"""

import json
import os
import datetime
from pathlib import Path
from typing import Dict, List, Any
import hashlib
import subprocess

class DevelopmentRecorder:
    """Records and documents development activities for ADK IDE implementation"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.docs_dir = self.project_root / "docs" / "development"
        self.logs_dir = self.project_root / "logs" / "development"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories for documentation and logs"""
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
    def record_file_change(self, file_path: str, change_type: str, description: str = ""):
        """Record file changes with metadata"""
        timestamp = datetime.datetime.now().isoformat()
        
        # Calculate file hash for change tracking
        file_hash = self._calculate_file_hash(file_path) if os.path.exists(file_path) else None
        
        change_record = {
            "timestamp": timestamp,
            "file_path": file_path,
            "change_type": change_type,  # created, modified, deleted
            "description": description,
            "file_hash": file_hash,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "git_commit": self._get_current_git_commit()
        }
        
        # Log to development log
        log_file = self.logs_dir / f"changes_{datetime.date.today().isoformat()}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(change_record) + "\n")
            
        # Update documentation
        self._update_development_docs(change_record)
        
    def record_milestone(self, milestone: str, description: str, files_affected: List[str] = None):
        """Record development milestones"""
        timestamp = datetime.datetime.now().isoformat()
        
        milestone_record = {
            "timestamp": timestamp,
            "milestone": milestone,
            "description": description,
            "files_affected": files_affected or [],
            "git_commit": self._get_current_git_commit(),
            "project_stats": self._get_project_stats()
        }
        
        # Log milestone
        milestone_file = self.logs_dir / "milestones.jsonl"
        with open(milestone_file, "a") as f:
            f.write(json.dumps(milestone_record) + "\n")
            
        # Update milestone documentation
        self._update_milestone_docs(milestone_record)
        
    def generate_progress_report(self):
        """Generate comprehensive progress report"""
        report = {
            "generated_at": datetime.datetime.now().isoformat(),
            "project_overview": self._get_project_overview(),
            "recent_changes": self._get_recent_changes(),
            "milestones": self._get_milestones(),
            "file_statistics": self._get_file_statistics(),
            "implementation_status": self._assess_implementation_status()
        }
        
        # Save report
        report_file = self.docs_dir / f"progress_report_{datetime.date.today().isoformat()}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
            
        # Generate markdown report
        self._generate_markdown_report(report)
        
        return report
        
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file content"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
            
    def _get_current_git_commit(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
            
    def _get_project_stats(self) -> Dict[str, Any]:
        """Get current project statistics"""
        stats = {
            "total_files": 0,
            "total_lines": 0,
            "file_types": {},
            "adk_components": 0
        }
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for file in files:
                if not file.startswith('.'):
                    file_path = Path(root) / file
                    stats["total_files"] += 1
                    
                    # Count file types
                    ext = file_path.suffix.lower()
                    stats["file_types"][ext] = stats["file_types"].get(ext, 0) + 1
                    
                    # Count lines
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            stats["total_lines"] += sum(1 for _ in f)
                    except Exception:
                        pass
                        
                    # Count ADK components
                    if self._is_adk_component(file_path):
                        stats["adk_components"] += 1
                        
        return stats
        
    def _is_adk_component(self, file_path: Path) -> bool:
        """Check if file is an ADK component"""
        adk_indicators = [
            "LlmAgent", "LoopAgent", "SequentialAgent", "ParallelAgent",
            "BuiltInCodeExecutor", "SessionService", "ArtifactService",
            "google.adk", "from google.adk", "import google.adk"
        ]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return any(indicator in content for indicator in adk_indicators)
        except Exception:
            return False
            
    def _update_development_docs(self, change_record: Dict[str, Any]):
        """Update development documentation with change record"""
        doc_file = self.docs_dir / "DEVELOPMENT_LOG.md"
        
        # Create or update development log
        if not doc_file.exists():
            with open(doc_file, "w") as f:
                f.write("# ADK IDE Development Log\n\n")
                f.write("This document tracks all development activities and changes.\n\n")
                
        # Append change record
        with open(doc_file, "a") as f:
            f.write(f"## {change_record['timestamp']}\n")
            f.write(f"- **File**: `{change_record['file_path']}`\n")
            f.write(f"- **Change**: {change_record['change_type']}\n")
            if change_record['description']:
                f.write(f"- **Description**: {change_record['description']}\n")
            f.write(f"- **Hash**: `{change_record['file_hash']}`\n")
            f.write(f"- **Commit**: `{change_record['git_commit']}`\n\n")
            
    def _update_milestone_docs(self, milestone_record: Dict[str, Any]):
        """Update milestone documentation"""
        doc_file = self.docs_dir / "MILESTONES.md"
        
        # Create or update milestone log
        if not doc_file.exists():
            with open(doc_file, "w") as f:
                f.write("# ADK IDE Implementation Milestones\n\n")
                f.write("This document tracks major development milestones.\n\n")
                
        # Append milestone record
        with open(doc_file, "a") as f:
            f.write(f"## {milestone_record['milestone']}\n")
            f.write(f"**Date**: {milestone_record['timestamp']}\n\n")
            f.write(f"**Description**: {milestone_record['description']}\n\n")
            if milestone_record['files_affected']:
                f.write("**Files Affected**:\n")
                for file_path in milestone_record['files_affected']:
                    f.write(f"- `{file_path}`\n")
                f.write("\n")
            f.write(f"**Commit**: `{milestone_record['git_commit']}`\n\n")
            f.write("---\n\n")
            
    def _get_recent_changes(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent changes within specified days"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        recent_changes = []
        
        # Read change logs
        for log_file in self.logs_dir.glob("changes_*.jsonl"):
            try:
                with open(log_file, "r") as f:
                    for line in f:
                        record = json.loads(line.strip())
                        record_date = datetime.datetime.fromisoformat(record['timestamp'])
                        if record_date >= cutoff_date:
                            recent_changes.append(record)
            except Exception:
                continue
                
        return sorted(recent_changes, key=lambda x: x['timestamp'], reverse=True)
        
    def _get_milestones(self) -> List[Dict[str, Any]]:
        """Get all recorded milestones"""
        milestones = []
        milestone_file = self.logs_dir / "milestones.jsonl"
        
        if milestone_file.exists():
            try:
                with open(milestone_file, "r") as f:
                    for line in f:
                        milestones.append(json.loads(line.strip()))
            except Exception:
                pass
                
        return sorted(milestones, key=lambda x: x['timestamp'], reverse=True)
        
    def _get_file_statistics(self) -> Dict[str, Any]:
        """Get comprehensive file statistics"""
        return self._get_project_stats()
        
    def _assess_implementation_status(self) -> Dict[str, Any]:
        """Assess current implementation status against requirements"""
        status = {
            "overall_progress": 0,
            "components": {
                "multi_agent_architecture": {"status": "not_started", "progress": 0},
                "code_execution": {"status": "not_started", "progress": 0},
                "iterative_workflows": {"status": "not_started", "progress": 0},
                "policy_enforcement": {"status": "not_started", "progress": 0},
                "ide_components": {"status": "not_started", "progress": 0},
                "section_management": {"status": "not_started", "progress": 0},
                "web_interface": {"status": "not_started", "progress": 0},
                "enterprise_integration": {"status": "not_started", "progress": 0}
            }
        }
        
        # Analyze existing files to determine implementation status
        self._analyze_implementation_files(status)
        
        # Calculate overall progress
        total_progress = sum(comp["progress"] for comp in status["components"].values())
        status["overall_progress"] = total_progress / len(status["components"])
        
        return status
        
    def _analyze_implementation_files(self, status: Dict[str, Any]):
        """Analyze existing files to determine implementation status"""
        # Check for ADK components
        adk_files = []
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.endswith(('.py', '.js', '.html', '.css')):
                    file_path = Path(root) / file
                    if self._is_adk_component(file_path):
                        adk_files.append(str(file_path))
                        
        # Update status based on found files
        if adk_files:
            status["components"]["multi_agent_architecture"]["status"] = "in_progress"
            status["components"]["multi_agent_architecture"]["progress"] = min(len(adk_files) * 10, 100)
            
    def _get_project_overview(self) -> Dict[str, Any]:
        """Get project overview information"""
        return {
            "name": "ADK IDE Implementation",
            "description": "High-density coding agent environment using Google ADK",
            "start_date": self._get_project_start_date(),
            "current_phase": self._determine_current_phase(),
            "repository": self._get_repository_info()
        }
        
    def _get_project_start_date(self) -> str:
        """Get project start date from git history or file creation"""
        try:
            result = subprocess.run(
                ["git", "log", "--reverse", "--format=%ai", "--max-count=1"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except Exception:
            pass
            
        # Fallback to earliest file modification time
        earliest_time = datetime.datetime.now()
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                file_path = Path(root) / file
                try:
                    mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < earliest_time:
                        earliest_time = mtime
                except Exception:
                    continue
                    
        return earliest_time.isoformat()
        
    def _determine_current_phase(self) -> str:
        """Determine current development phase"""
        milestones = self._get_milestones()
        if not milestones:
            return "Planning"
            
        latest_milestone = milestones[0]['milestone']
        
        phase_mapping = {
            "requirements": "Requirements Analysis",
            "architecture": "Architecture Design",
            "foundation": "Foundation Development",
            "core": "Core Implementation",
            "integration": "Integration Testing",
            "deployment": "Deployment Preparation",
            "production": "Production Ready"
        }
        
        for key, phase in phase_mapping.items():
            if key in latest_milestone.lower():
                return phase
                
        return "Active Development"
        
    def _get_repository_info(self) -> Dict[str, Any]:
        """Get repository information"""
        repo_info = {
            "remote_url": None,
            "current_branch": None,
            "total_commits": 0
        }
        
        try:
            # Get remote URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                repo_info["remote_url"] = result.stdout.strip()
                
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                repo_info["current_branch"] = result.stdout.strip()
                
            # Get commit count
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                repo_info["total_commits"] = int(result.stdout.strip())
                
        except Exception:
            pass
            
        return repo_info
        
    def _generate_markdown_report(self, report: Dict[str, Any]):
        """Generate markdown progress report"""
        report_file = self.docs_dir / f"PROGRESS_REPORT_{datetime.date.today().isoformat()}.md"
        
        with open(report_file, "w") as f:
            f.write("# ADK IDE Implementation Progress Report\n\n")
            f.write(f"**Generated**: {report['generated_at']}\n\n")
            
            # Project Overview
            f.write("## Project Overview\n\n")
            overview = report['project_overview']
            f.write(f"- **Name**: {overview['name']}\n")
            f.write(f"- **Description**: {overview['description']}\n")
            f.write(f"- **Start Date**: {overview['start_date']}\n")
            f.write(f"- **Current Phase**: {overview['current_phase']}\n")
            f.write(f"- **Repository**: {overview['repository'].get('remote_url', 'Local')}\n")
            f.write(f"- **Branch**: {overview['repository'].get('current_branch', 'Unknown')}\n")
            f.write(f"- **Total Commits**: {overview['repository'].get('total_commits', 0)}\n\n")
            
            # Implementation Status
            f.write("## Implementation Status\n\n")
            status = report['implementation_status']
            f.write(f"**Overall Progress**: {status['overall_progress']:.1f}%\n\n")
            
            f.write("### Component Status\n\n")
            for component, info in status['components'].items():
                status_emoji = {"not_started": "⏳", "in_progress": "🔄", "completed": "✅"}.get(info['status'], "❓")
                f.write(f"- {status_emoji} **{component.replace('_', ' ').title()}**: {info['progress']}% ({info['status']})\n")
            f.write("\n")
            
            # Recent Changes
            f.write("## Recent Changes (Last 7 Days)\n\n")
            recent_changes = report['recent_changes'][:10]  # Show last 10 changes
            if recent_changes:
                for change in recent_changes:
                    f.write(f"- **{change['timestamp'][:19]}**: {change['change_type']} `{change['file_path']}`\n")
                    if change['description']:
                        f.write(f"  - {change['description']}\n")
            else:
                f.write("No recent changes recorded.\n")
            f.write("\n")
            
            # Milestones
            f.write("## Recent Milestones\n\n")
            milestones = report['milestones'][:5]  # Show last 5 milestones
            if milestones:
                for milestone in milestones:
                    f.write(f"### {milestone['milestone']}\n")
                    f.write(f"**Date**: {milestone['timestamp'][:19]}\n\n")
                    f.write(f"{milestone['description']}\n\n")
            else:
                f.write("No milestones recorded yet.\n\n")
            
            # File Statistics
            f.write("## File Statistics\n\n")
            stats = report['file_statistics']
            f.write(f"- **Total Files**: {stats['total_files']}\n")
            f.write(f"- **Total Lines**: {stats['total_lines']:,}\n")
            f.write(f"- **ADK Components**: {stats['adk_components']}\n\n")
            
            f.write("### File Types\n\n")
            for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
                if ext:
                    f.write(f"- **{ext}**: {count} files\n")
            f.write("\n")
            
            # Next Steps
            f.write("## Recommended Next Steps\n\n")
            f.write(self._generate_next_steps_recommendations(status))
            
    def _generate_next_steps_recommendations(self, status: Dict[str, Any]) -> str:
        """Generate next steps recommendations based on current status"""
        recommendations = []
        
        for component, info in status['components'].items():
            if info['status'] == 'not_started':
                recommendations.append(f"- Start implementation of {component.replace('_', ' ')}")
            elif info['status'] == 'in_progress' and info['progress'] < 50:
                recommendations.append(f"- Continue development of {component.replace('_', ' ')} (currently {info['progress']}%)")
                
        if not recommendations:
            recommendations.append("- All major components are in progress or completed")
            recommendations.append("- Focus on integration testing and documentation")
            recommendations.append("- Prepare for deployment and production readiness")
            
        return "\n".join(recommendations) + "\n"

# Global recorder instance
recorder = DevelopmentRecorder()

def record_file_change(file_path: str, change_type: str, description: str = ""):
    """Hook function to record file changes"""
    recorder.record_file_change(file_path, change_type, description)

def record_milestone(milestone: str, description: str, files_affected: List[str] = None):
    """Hook function to record milestones"""
    recorder.record_milestone(milestone, description, files_affected)

def generate_progress_report():
    """Hook function to generate progress report"""
    return recorder.generate_progress_report()

if __name__ == "__main__":
    # Generate progress report when run directly
    report = generate_progress_report()
    print(f"Progress report generated: {report}")