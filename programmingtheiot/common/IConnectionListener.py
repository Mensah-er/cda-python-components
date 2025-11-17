from abc import ABC, abstractmethod

class IConnectionListener(ABC):
    """Python version of the Java IConnectionListener interface."""

    @abstractmethod
    def connection_lost(self, cause: Exception):
        """Called when the connection is lost."""
        pass

    @abstractmethod
    def on_connect(self):
        """Called when the connection is successfully established."""
        pass

    @abstractmethod
    def on_disconnect(self):
        """Called when the connection is disconnected."""
        pass
