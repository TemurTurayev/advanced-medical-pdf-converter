from typing import Dict, List, Type
from .plugins.base import BasePlugin
from .errors import PluginError

class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
    
    def register_plugin(self, plugin: BasePlugin):
        """Register a new plugin"""
        self.plugins[plugin.name] = plugin
    
    def get_plugin(self, name: str) -> BasePlugin:
        """Get plugin by name"""
        if name not in self.plugins:
            raise PluginError(f'Plugin {name} not found')
        return self.plugins[name]
    
    def process_content(self, content: any, context: Dict = None) -> Dict:
        """Process content through all enabled plugins"""
        results = {}
        for name, plugin in self.plugins.items():
            if plugin.enabled and plugin.validate(content):
                try:
                    results[name] = plugin.process(content, context)
                except Exception as e:
                    raise PluginError(f'Plugin {name} failed: {str(e)}')
        return results