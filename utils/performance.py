"""Performance monitoring and metrics collection"""
import time
from typing import Callable, Any, Dict, TypeVar, Optional
from functools import wraps
from dataclasses import dataclass, field
from datetime import datetime
from utils.logger import logger

T = TypeVar('T')


@dataclass
class PerformanceMetric:
    """Single performance metric"""
    name: str
    operation: str
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_msg: Optional[str] = None
    
    def __str__(self) -> str:
        status = "✅" if self.success else "❌"
        return f"{status} {self.operation}: {self.duration_ms:.2f}ms"


class PerformanceMonitor:
    """Monitor and collect performance metrics"""
    
    def __init__(self, max_metrics: int = 1000):
        """
        Initialize performance monitor.
        
        Args:
            max_metrics: Maximum metrics to keep in memory
        """
        self.metrics: list[PerformanceMetric] = []
        self.max_metrics = max_metrics
        self.cache_hits = 0
        self.cache_misses = 0
    
    def record_metric(self, metric: PerformanceMetric) -> None:
        """
        Record a performance metric.
        
        Args:
            metric: Metric to record
        """
        self.metrics.append(metric)
        
        # Keep only recent metrics
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics:]
        
        logger.debug(f"Metric recorded: {metric}")
    
    def record_cache_hit(self) -> None:
        """Record a cache hit"""
        self.cache_hits += 1
        logger.debug(f"Cache hit (total: {self.cache_hits})")
    
    def record_cache_miss(self) -> None:
        """Record a cache miss"""
        self.cache_misses += 1
        logger.debug(f"Cache miss (total: {self.cache_misses})")
    
    def get_cache_hit_rate(self) -> float:
        """
        Get cache hit rate.
        
        Returns:
            Cache hit rate as percentage (0-100)
        """
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return (self.cache_hits / total) * 100.0
    
    def get_average_duration(self, operation: str = None) -> float:
        """
        Get average operation duration.
        
        Args:
            operation: Filter by operation name (None = all)
            
        Returns:
            Average duration in milliseconds
        """
        if not self.metrics:
            return 0.0
        
        filtered = self.metrics
        if operation:
            filtered = [m for m in self.metrics if m.operation == operation]
        
        if not filtered:
            return 0.0
        
        total = sum(m.duration_ms for m in filtered)
        return total / len(filtered)
    
    def get_slowest_operations(self, limit: int = 5) -> list[PerformanceMetric]:
        """
        Get slowest operations.
        
        Args:
            limit: Number of operations to return
            
        Returns:
            List of slowest metrics
        """
        return sorted(self.metrics, key=lambda m: m.duration_ms, reverse=True)[:limit]
    
    def get_failed_operations(self) -> list[PerformanceMetric]:
        """
        Get failed operations.
        
        Returns:
            List of failed metrics
        """
        return [m for m in self.metrics if not m.success]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics.
        
        Returns:
            Dictionary with performance statistics
        """
        total_metrics = len(self.metrics)
        failed = len(self.get_failed_operations())
        
        return {
            "total_metrics": total_metrics,
            "successful": total_metrics - failed,
            "failed": failed,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": f"{self.get_cache_hit_rate():.1f}%",
            "avg_duration_ms": f"{self.get_average_duration():.2f}",
            "slowest_operations": [str(m) for m in self.get_slowest_operations(3)],
            "timestamp": datetime.now().isoformat()
        }
    
    def clear(self) -> None:
        """Clear all metrics"""
        self.metrics.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Performance monitor cleared")


def monitor_performance(operation_name: str = None) -> Callable:
    """
    Decorator to monitor performance of a function.
    
    Args:
        operation_name: Name of operation (defaults to function name)
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        op_name = operation_name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                metric = PerformanceMetric(
                    name=func.__module__,
                    operation=op_name,
                    duration_ms=duration_ms,
                    success=True
                )
                monitor.record_metric(metric)
                return result
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                metric = PerformanceMetric(
                    name=func.__module__,
                    operation=op_name,
                    duration_ms=duration_ms,
                    success=False,
                    error_msg=str(e)
                )
                monitor.record_metric(metric)
                logger.warning(f"{op_name} failed after {duration_ms:.2f}ms: {e}")
                raise
        
        return wrapper
    return decorator


# Global monitor instance
monitor = PerformanceMonitor()
