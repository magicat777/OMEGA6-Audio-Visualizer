"""
Plugin Manager for OMEGA6
Handles plugin discovery, loading, and management
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, Optional, Type

from .plugin_base import PluginWidget


class PluginManager:
    """Manages OMEGA6 plugins"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.plugins: Dict[str, Type[PluginWidget]] = {}
        self.plugin_instances: Dict[str, PluginWidget] = {}

        # Plugin search paths
        self.plugin_paths = [
            Path(__file__).parent.parent / "plugins",
            Path.home() / ".omega6" / "plugins",  # User plugins
        ]

    def discover_plugins(self):
        """Discover and load all available plugins"""
        self.logger.info("Discovering plugins...")

        for plugin_path in self.plugin_paths:
            if plugin_path.exists():
                self._scan_plugin_directory(plugin_path)

        self.logger.info(f"Discovered {len(self.plugins)} plugins")

    def _scan_plugin_directory(self, directory: Path):
        """Scan a directory for plugins"""
        # Look for plugin directories with __init__.py
        for item in directory.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                self._load_plugin_module(item)

    def _load_plugin_module(self, plugin_dir: Path):
        """Load a plugin module"""
        plugin_name = plugin_dir.name

        try:
            # Add plugin directory to path
            import sys

            if str(plugin_dir.parent) not in sys.path:
                sys.path.insert(0, str(plugin_dir.parent))

            # Import the module
            module = importlib.import_module(plugin_name)

            # Find plugin classes
            for name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, PluginWidget)
                    and obj is not PluginWidget
                    and hasattr(obj, "PLUGIN_NAME")
                ):

                    self.register_plugin(obj.PLUGIN_NAME, obj)

        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")

    def register_plugin(self, name: str, plugin_class: Type[PluginWidget]):
        """Register a plugin class"""
        if name in self.plugins:
            self.logger.warning(f"Plugin {name} already registered, overwriting")

        self.plugins[name] = plugin_class
        self.logger.info(f"Registered plugin: {name} v{plugin_class.PLUGIN_VERSION}")

    def create_plugin_instance(self, name: str) -> Optional[PluginWidget]:
        """Create an instance of a plugin"""
        if name not in self.plugins:
            self.logger.error(f"Plugin {name} not found")
            return None

        try:
            instance = self.plugins[name]()
            self.plugin_instances[name] = instance
            return instance
        except Exception as e:
            self.logger.error(f"Failed to create plugin instance {name}: {e}")
            return None

    def get_plugins(self) -> Dict[str, Type[PluginWidget]]:
        """Get all registered plugins"""
        return self.plugins.copy()

    def get_plugin_instance(self, name: str) -> Optional[PluginWidget]:
        """Get a plugin instance"""
        return self.plugin_instances.get(name)

    def get_all_instances(self) -> Dict[str, PluginWidget]:
        """Get all plugin instances"""
        return self.plugin_instances.copy()

    def update_all_plugins(self, audio_data=None, fft_data=None, frequencies=None):
        """Update all active plugins with new data"""
        if not self.plugin_instances:
            self.logger.warning("No plugin instances to update!")
            return
            
        for name, instance in self.plugin_instances.items():
            try:
                if audio_data is not None:
                    instance.update_audio(audio_data, self.sample_rate if hasattr(self, 'sample_rate') else 48000)
                if fft_data is not None and frequencies is not None:
                    instance.update_fft(fft_data, frequencies)
            except Exception as e:
                self.logger.error(f"Error updating plugin {name}: {e}")

    def save_plugin_settings(self) -> Dict[str, Dict]:
        """Save settings for all plugins"""
        settings = {}
        for name, instance in self.plugin_instances.items():
            try:
                settings[name] = instance.get_settings()
            except Exception as e:
                self.logger.error(f"Error saving settings for {name}: {e}")
        return settings

    def load_plugin_settings(self, settings: Dict[str, Dict]):
        """Load settings for all plugins"""
        for name, plugin_settings in settings.items():
            if name in self.plugin_instances:
                try:
                    self.plugin_instances[name].load_settings(plugin_settings)
                except Exception as e:
                    self.logger.error(f"Error loading settings for {name}: {e}")
