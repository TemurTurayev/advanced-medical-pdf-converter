class PluginManager:
    def __init__(self):
        self.plugins = []
    
    def register_plugin(self, plugin):
        self.plugins.append(plugin)
    
    def process_document(self, text):
        results = {}
        for plugin in self.plugins:
            results[plugin.name] = plugin.process(text)
        return results