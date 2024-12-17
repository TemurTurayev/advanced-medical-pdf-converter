from typing import Any, Dict, Optional

class BasePlugin:
    """Base class for all plugins"""
    def __init__(self):
        self.name = self.__class__.__name__
        self.enabled = True

    def process(self, content: Any, context: Optional[Dict] = None) -> Any:
        """Process the content using the plugin
        Args:
            content: Content to process
            context: Additional context for processing
        Returns:
            Processed content
        """
        raise NotImplementedError("Plugin must implement process method")

    def validate(self, content: Any) -> bool:
        """Validate if content can be processed by this plugin
        Args:
            content: Content to validate
        Returns:
            True if content can be processed, False otherwise
        """
        return True