"""Common decorators for the application"""
import functools
from typing import Any, Callable
from utils.logger import logger
from utils.exceptions import F1DashboardException


def handle_errors(func: Callable) -> Callable:
    """
    Decorator to handle errors in functions.
    Logs exceptions and re-raises them.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except F1DashboardException as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise F1DashboardException(f"Error in {func.__name__}: {e}")
    
    return wrapper


def log_operation(operation_name: str) -> Callable:
    """
    Decorator to log function operations.
    
    Args:
        operation_name: Human-readable name for logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.info(f"Starting: {operation_name}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed: {operation_name}")
                return result
            except Exception as e:
                logger.error(f"Failed: {operation_name} - {e}")
                raise
        
        return wrapper
    
    return decorator
