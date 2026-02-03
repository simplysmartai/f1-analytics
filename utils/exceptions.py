"""Custom exceptions"""

class F1DashboardException(Exception):
    """Base exception for F1 Dashboard"""
    pass

class DataLoadException(F1DashboardException):
    """Raised when data cannot be loaded"""
    pass

class CacheException(F1DashboardException):
    """Raised when cache operations fail"""
    pass

class ValidationException(F1DashboardException):
    """Raised when validation fails"""
    pass

class SessionDataException(F1DashboardException):
    """Raised when session data is invalid"""
    pass
