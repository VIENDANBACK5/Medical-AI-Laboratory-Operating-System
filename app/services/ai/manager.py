import os
import importlib
import inspect
from typing import Dict, List, Optional

from app.services.ai.base import IAIPlugin, ModelInfo


class AIEngineManager:
    _instance: Optional["AIEngineManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AIEngineManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.plugins: Dict[str, IAIPlugin] = {}
        self.plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
        
        # Ensure plugins directory exists
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # Auto-discover plugins
        self.discover_plugins()
        self._initialized = True

    def discover_plugins(self) -> None:
        """Scan app/services/ai/plugins/ for IAIPlugin implementations and load them."""
        if not os.path.exists(self.plugins_dir):
            return

        # Check all python files
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"app.services.ai.plugins.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    # Find all classes that implement IAIPlugin
                    for _, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, IAIPlugin)
                            and obj is not IAIPlugin
                        ):
                            plugin_instance = obj()
                            info = plugin_instance.get_info()
                            self.plugins[info.name] = plugin_instance
                except Exception as e:
                    # In a production context, log this error to logging services
                    print(f"Error loading AI plugin from {module_name}: {str(e)}")

    def list_models(self) -> List[ModelInfo]:
        """Returns metadata for all dynamically loaded models."""
        return [plugin.get_info() for plugin in self.plugins.values()]

    def get_plugin(self, name: str) -> IAIPlugin:
        """Returns the registered plugin instance for the given model name."""
        if name not in self.plugins:
            raise KeyError(f"AI model plugin '{name}' is not registered in the system.")
        return self.plugins[name]
