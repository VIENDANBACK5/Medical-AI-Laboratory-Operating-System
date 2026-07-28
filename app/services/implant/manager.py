import os
import importlib
import inspect
from typing import Dict, List, Optional

from app.services.implant.base import IImplantPlugin, ImplantInfo


class ImplantEngineManager:
    """Auto-discovering registry for implant generation plugins.

    Mirrors :class:`AIEngineManager`: it scans ``implant/plugins/`` for any
    :class:`IImplantPlugin` implementation and loads it, so a new implant model
    is added by dropping a single file into that folder.
    """

    _instance: Optional["ImplantEngineManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ImplantEngineManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.plugins: Dict[str, IImplantPlugin] = {}
        self.plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
        os.makedirs(self.plugins_dir, exist_ok=True)
        self.discover_plugins()
        self._initialized = True

    def discover_plugins(self) -> None:
        """Scan app/services/implant/plugins/ for IImplantPlugin implementations."""
        if not os.path.exists(self.plugins_dir):
            return

        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f"app.services.implant.plugins.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    for _, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, IImplantPlugin)
                            and obj is not IImplantPlugin
                        ):
                            plugin_instance = obj()
                            info = plugin_instance.get_info()
                            self.plugins[info.name] = plugin_instance
                except Exception as e:
                    print(f"Error loading implant plugin from {module_name}: {str(e)}")

    def list_models(self) -> List[ImplantInfo]:
        return [plugin.get_info() for plugin in self.plugins.values()]

    def get_plugin(self, name: str) -> IImplantPlugin:
        if name not in self.plugins:
            raise KeyError(f"Implant plugin '{name}' is not registered in the system.")
        return self.plugins[name]
