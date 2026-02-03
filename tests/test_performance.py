"""Performance and caching tests"""
import pytest
import pandas as pd
import time
from utils.performance import PerformanceMonitor, monitor_performance, monitor
from utils.caching import SmartCache, CacheEntry, cached, global_cache


class TestPerformanceMonitor:
    """Test performance monitoring functionality"""
    
    def test_performance_metric_creation(self):
        """Test creating performance metrics"""
        pm = PerformanceMonitor()
        from utils.performance import PerformanceMetric
        
        metric = PerformanceMetric(
            name="test",
            operation="test_op",
            duration_ms=10.5,
            success=True
        )
        
        assert metric.name == "test"
        assert metric.operation == "test_op"
        assert metric.duration_ms == 10.5
        assert metric.success is True
    
    def test_monitor_recording(self):
        """Test metric recording"""
        pm = PerformanceMonitor(max_metrics=10)
        from utils.performance import PerformanceMetric
        
        metric = PerformanceMetric("test", "op1", 5.0)
        pm.record_metric(metric)
        
        assert len(pm.metrics) == 1
        assert pm.metrics[0] == metric
    
    def test_monitor_cache_hits_misses(self):
        """Test cache hit/miss tracking"""
        pm = PerformanceMonitor()
        
        pm.record_cache_hit()
        pm.record_cache_hit()
        pm.record_cache_miss()
        
        assert pm.cache_hits == 2
        assert pm.cache_misses == 1
        assert pm.get_cache_hit_rate() == pytest.approx(66.67, rel=1)
    
    def test_get_average_duration(self):
        """Test average duration calculation"""
        pm = PerformanceMonitor()
        from utils.performance import PerformanceMetric
        
        pm.record_metric(PerformanceMetric("test", "op1", 10.0))
        pm.record_metric(PerformanceMetric("test", "op1", 20.0))
        pm.record_metric(PerformanceMetric("test", "op2", 30.0))
        
        avg_all = pm.get_average_duration()
        assert avg_all == pytest.approx(20.0, rel=0.1)
        
        avg_op1 = pm.get_average_duration("op1")
        assert avg_op1 == pytest.approx(15.0, rel=0.1)
    
    def test_get_slowest_operations(self):
        """Test getting slowest operations"""
        pm = PerformanceMonitor()
        from utils.performance import PerformanceMetric
        
        pm.record_metric(PerformanceMetric("test", "fast", 5.0))
        pm.record_metric(PerformanceMetric("test", "slow", 50.0))
        pm.record_metric(PerformanceMetric("test", "medium", 25.0))
        
        slowest = pm.get_slowest_operations(2)
        assert len(slowest) == 2
        assert slowest[0].duration_ms == 50.0
        assert slowest[1].duration_ms == 25.0
    
    def test_monitor_clear(self):
        """Test clearing monitor"""
        pm = PerformanceMonitor()
        from utils.performance import PerformanceMetric
        
        pm.record_metric(PerformanceMetric("test", "op1", 10.0))
        pm.record_cache_hit()
        
        pm.clear()
        
        assert len(pm.metrics) == 0
        assert pm.cache_hits == 0
        assert pm.cache_misses == 0


class TestSmartCache:
    """Test smart caching functionality"""
    
    def test_cache_entry_creation(self):
        """Test cache entry creation"""
        entry = CacheEntry("value", ttl_seconds=60)
        
        assert entry.value == "value"
        assert entry.ttl_seconds == 60
        assert entry.access_count == 0
        assert not entry.is_expired()
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration"""
        entry = CacheEntry("value", ttl_seconds=0)
        time.sleep(0.1)
        
        assert entry.is_expired()
    
    def test_smart_cache_get_set(self):
        """Test cache get/set operations"""
        cache = SmartCache()
        
        cache.set("key1", "value1")
        result = cache.get("key1")
        
        assert result == "value1"
        assert cache.hits == 1
        assert cache.misses == 0
    
    def test_smart_cache_miss(self):
        """Test cache miss"""
        cache = SmartCache()
        
        result = cache.get("nonexistent")
        
        assert result is None
        assert cache.hits == 0
        assert cache.misses == 1
    
    def test_smart_cache_expiration(self):
        """Test cache entry expiration"""
        cache = SmartCache()
        
        cache.set("key1", "value1", ttl_seconds=0)
        time.sleep(0.1)
        result = cache.get("key1")
        
        assert result is None
        assert cache.misses == 1
    
    def test_smart_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = SmartCache(max_size=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Access key1 to make it more recent
        cache.get("key1")
        
        # Adding new item should evict key2 (least recently used)
        cache.set("key4", "value4")
        
        assert len(cache.cache) == 3
        assert cache.get("key1") == "value1"
        assert cache.get("key4") == "value4"
    
    def test_smart_cache_stats(self):
        """Test cache statistics"""
        cache = SmartCache()
        
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("nonexistent")
        
        stats = cache.get_stats()
        
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert "hit_rate" in stats


class TestCachedDecorator:
    """Test @cached decorator"""
    
    def test_cached_decorator_basic(self):
        """Test basic caching with decorator"""
        call_count = 0
        
        @cached(ttl_seconds=60)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)
        result3 = expensive_function(10)
        
        assert result1 == 10
        assert result2 == 10
        assert result3 == 20
        assert call_count == 2  # Called twice (5 and 10)
    
    def test_cached_decorator_with_kwargs(self):
        """Test caching with keyword arguments"""
        call_count = 0
        
        @cached(ttl_seconds=60)
        def function_with_kwargs(a, b=0):
            nonlocal call_count
            call_count += 1
            return a + b
        
        result1 = function_with_kwargs(5, b=3)
        result2 = function_with_kwargs(5, b=3)
        result3 = function_with_kwargs(5, b=2)
        
        assert result1 == 8
        assert result2 == 8
        assert result3 == 7
        assert call_count == 2


class TestMonitorPerformanceDecorator:
    """Test @monitor_performance decorator"""
    
    def test_monitor_performance_success(self):
        """Test monitoring successful function"""
        global_monitor = monitor
        initial_count = len(global_monitor.metrics)
        
        @monitor_performance("test_operation")
        def fast_function():
            time.sleep(0.01)
            return "result"
        
        result = fast_function()
        
        assert result == "result"
        assert len(global_monitor.metrics) > initial_count
        last_metric = global_monitor.metrics[-1]
        assert last_metric.operation == "test_operation"
        assert last_metric.success is True
        assert last_metric.duration_ms >= 10
    
    def test_monitor_performance_failure(self):
        """Test monitoring failed function"""
        global_monitor = monitor
        
        @monitor_performance("failing_operation")
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        last_metric = global_monitor.metrics[-1]
        assert last_metric.operation == "failing_operation"
        assert last_metric.success is False


class TestIntegration:
    """Integration tests for performance features"""
    
    def test_caching_reduces_execution_time(self):
        """Test that caching reduces execution time"""
        @cached(ttl_seconds=60)
        def slow_function(x):
            time.sleep(0.05)
            return x * 2
        
        # First call (cache miss)
        start = time.time()
        slow_function(5)
        time_first = time.time() - start
        
        # Second call (cache hit)
        start = time.time()
        slow_function(5)
        time_second = time.time() - start
        
        # Second call should be much faster
        assert time_second < time_first / 2
    
    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration"""
        monitor.clear()
        
        @monitor_performance("integration_test")
        @cached(ttl_seconds=60)
        def test_func(x):
            time.sleep(0.01)
            return x * 2
        
        test_func(5)
        test_func(5)
        
        stats = monitor.get_stats()
        assert stats["total_metrics"] > 0
        assert stats["cache_hits"] == 1
