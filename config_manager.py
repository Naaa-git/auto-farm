import json
import threading
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CONFIG_PATH = Path("config.json")
logger = logging.getLogger(__name__)


class ConfigReloadHandler(FileSystemEventHandler):
    def __init__(self, manager):
        self.manager = manager

    def on_modified(self, event):
        if Path(event.src_path).name == CONFIG_PATH.name:
            logger.info("config.json changed, reloading...")
            self.manager.reload()


class ConfigManager:
    def __init__(self):
        self._config = {}
        self._lock = threading.Lock()
        self.reload()
        self._start_watcher()

    def reload(self):
        try:
            with open(CONFIG_PATH, "r") as f:
                new_config = json.load(f)
            with self._lock:
                self._config = new_config
            logger.info("Config loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to reload config: {e}")

    def get(self, *keys, default=None):
        with self._lock:
            val = self._config
            for k in keys:
                if isinstance(val, dict) and k in val:
                    val = val[k]
                else:
                    return default
            return val

    def get_capture_mode(self, creature_name: str) -> str:
        """
        Returns:
          'manual' - stop and notify user
          'auto'   - auto attack then capture at threshold
          'kill'   - not in capture list, kill it
        """
        capture_list = self.get("capture_list", default={})
        name_lower = creature_name.strip().lower()
        for listed_name, mode in capture_list.items():
            if listed_name.strip().lower() == name_lower:
                return mode
        return "kill"

    def save_capture_list(self, capture_list: dict):
        with self._lock:
            self._config["capture_list"] = capture_list
        try:
            with open(CONFIG_PATH, "r") as f:
                raw = json.load(f)
            raw["capture_list"] = capture_list
            with open(CONFIG_PATH, "w") as f:
                json.dump(raw, f, indent=2)
            logger.info("Capture list saved.")
        except Exception as e:
            logger.error(f"Failed to save capture list: {e}")

    def _start_watcher(self):
        handler = ConfigReloadHandler(self)
        observer = Observer()
        observer.schedule(handler, path=str(CONFIG_PATH.parent.resolve()), recursive=False)
        observer.daemon = True
        observer.start()

    @property
    def capture_threshold(self) -> int:
        return self.get("capture_threshold", default=80)

    @property
    def keys(self) -> dict:
        return self.get("keys", default={})

    @property
    def timing(self) -> dict:
        return self.get("timing", default={})

    @property
    def regions(self) -> dict:
        return self.get("regions", default={})

    @property
    def assets(self) -> dict:
        return self.get("assets", default={})
