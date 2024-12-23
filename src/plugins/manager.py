class PluginManager:
    """Plugin manager for document processing"""
    def __init__(self):
        self.plugins = []
    
    def register_plugin(self, plugin):
        """Register a new plugin"""
        self.plugins.append(plugin)
    
    def process_document(self, text):
        """Process document with all registered plugins"""
        results = {}
        for plugin in self.plugins:
            results[plugin.name] = plugin.process(text)
        return results