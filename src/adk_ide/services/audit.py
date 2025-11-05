"""Audit trail service for comprehensive logging of all code changes."""
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json


@dataclass
class AuditEntry:
    """Audit trail entry."""
    timestamp: datetime
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class AuditService:
    """Audit trail service for logging all system activities."""
    
    def __init__(self) -> None:
        self.entries: List[AuditEntry] = []
        self.max_entries = 10000  # Keep last 10k entries in memory
    
    def log(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> AuditEntry:
        """Log an audit entry."""
        entry = AuditEntry(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            session_id=session_id,
        )
        self.entries.append(entry)
        
        # Trim old entries if needed
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
        
        return entry
    
    def query(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Query audit entries."""
        results = self.entries
        
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if action:
            results = [e for e in results if e.action == action]
        if resource_type:
            results = [e for e in results if e.resource_type == resource_type]
        if resource_id:
            results = [e for e in results if e.resource_id == resource_id]
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]
        
        # Sort by timestamp descending
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        return results[:limit]
    
    def export(self, format: str = "json") -> str:
        """Export audit trail."""
        if format == "json":
            entries_dict = [e.to_dict() for e in self.entries]
            return json.dumps(entries_dict, indent=2)
        elif format == "csv":
            lines = ["timestamp,user_id,action,resource_type,resource_id,details"]
            for entry in self.entries:
                details_str = json.dumps(entry.details).replace(",", ";")
                lines.append(
                    f"{entry.timestamp.isoformat()},{entry.user_id},{entry.action},"
                    f"{entry.resource_type},{entry.resource_id},{details_str}"
                )
            return "\n".join(lines)
        return ""

