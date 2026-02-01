"""
Monitoring - Metrics and statistics for observability

Provides:
- Execution metrics
- Performance tracking
- Usage statistics
- Error tracking
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import statistics


@dataclass
class ExecutionMetrics:
    """Metrics for a single execution"""
    
    session_id: str
    user_id: int
    agent_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    events_count: int = 0
    success: bool = True
    error_message: Optional[str] = None
    input_length: int = 0
    output_length: int = 0
    
    def complete(self, success: bool = True, error: Optional[str] = None):
        """Mark execution as complete"""
        self.end_time = datetime.now(timezone.utc)
        self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.error_message = error


@dataclass
class AgentStatistics:
    """Statistics for an agent type"""
    
    agent_type: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_duration_seconds: float = 0.0
    average_duration_seconds: float = 0.0
    min_duration_seconds: float = 0.0
    max_duration_seconds: float = 0.0
    total_events: int = 0
    average_events: float = 0.0
    
    def update(self, metrics: ExecutionMetrics):
        """Update statistics with new metrics"""
        self.total_executions += 1
        
        if metrics.success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        
        self.total_duration_seconds += metrics.duration_seconds
        self.average_duration_seconds = (
            self.total_duration_seconds / self.total_executions
        )
        
        if self.min_duration_seconds == 0 or metrics.duration_seconds < self.min_duration_seconds:
            self.min_duration_seconds = metrics.duration_seconds
        
        if metrics.duration_seconds > self.max_duration_seconds:
            self.max_duration_seconds = metrics.duration_seconds
        
        self.total_events += metrics.events_count
        self.average_events = self.total_events / self.total_executions


class MetricsCollector:
    """
    Collects and aggregates execution metrics.
    """
    
    def __init__(self):
        """Initialize metrics collector"""
        self.executions: List[ExecutionMetrics] = []
        self.agent_stats: Dict[str, AgentStatistics] = {}
        self.error_counts: Dict[str, int] = defaultdict(int)
    
    def record_execution(self, metrics: ExecutionMetrics):
        """
        Record execution metrics.
        
        Args:
            metrics: Execution metrics to record
        """
        self.executions.append(metrics)
        
        # Update agent statistics
        if metrics.agent_type not in self.agent_stats:
            self.agent_stats[metrics.agent_type] = AgentStatistics(
                agent_type=metrics.agent_type
            )
        
        self.agent_stats[metrics.agent_type].update(metrics)
        
        # Track errors
        if not metrics.success and metrics.error_message:
            self.error_counts[metrics.error_message] += 1
    
    def get_agent_stats(self, agent_type: str) -> Optional[AgentStatistics]:
        """Get statistics for a specific agent type"""
        return self.agent_stats.get(agent_type)
    
    def get_all_stats(self) -> Dict[str, AgentStatistics]:
        """Get statistics for all agents"""
        return self.agent_stats
    
    def get_recent_executions(
        self,
        limit: int = 100,
        agent_type: Optional[str] = None
    ) -> List[ExecutionMetrics]:
        """
        Get recent executions.
        
        Args:
            limit: Maximum number of executions to return
            agent_type: Optional filter by agent type
            
        Returns:
            List of recent execution metrics
        """
        executions = self.executions
        
        if agent_type:
            executions = [e for e in executions if e.agent_type == agent_type]
        
        return executions[-limit:]
    
    def get_error_summary(self) -> Dict[str, int]:
        """Get summary of errors"""
        return dict(self.error_counts)
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        total_executions = len(self.executions)
        successful = sum(1 for e in self.executions if e.success)
        failed = total_executions - successful
        
        durations = [e.duration_seconds for e in self.executions if e.duration_seconds > 0]
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": successful / total_executions if total_executions > 0 else 0,
            "average_duration_seconds": statistics.mean(durations) if durations else 0,
            "median_duration_seconds": statistics.median(durations) if durations else 0,
            "total_agents": len(self.agent_stats),
            "most_used_agent": max(
                self.agent_stats.items(),
                key=lambda x: x[1].total_executions,
                default=(None, None)
            )[0] if self.agent_stats else None
        }
    
    def clear_old_metrics(self, days: int = 7):
        """
        Clear metrics older than specified days.
        
        Args:
            days: Number of days to keep
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        self.executions = [
            e for e in self.executions
            if e.start_time > cutoff
        ]


# Global metrics collector
metrics_collector = MetricsCollector()
