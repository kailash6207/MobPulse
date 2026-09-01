# config.py
import json
import os

CONFIG_FILE = "lap_health_settings.json"

DEFAULT_CONFIG = {
    "storage_warning_threshold": 85.0,  # % disk used
    "temp_warning_threshold": 75.0,     # °C warm
    "temp_critical_threshold": 85.0,    # °C dangerous
    "battery_low_threshold": 20.0,      # % battery remaining
    "ram_warning_threshold": 80.0,      # % RAM allocated
    "ping_warning_threshold": 120.0,    # ms ping
    "jitter_warning_threshold": 20.0,   # ms jitter
    "refresh_interval_sec": 3,          # Seconds between polling loops
    "appearance_mode": "Dark",          # "Dark", "Light", "System"
    "color_theme": "blue",              # "blue", "green", "dark-blue"
    "enable_sound_alerts": False,
    "enable_desktop_notifs": True,
    "stress_test_duration": 5           # Seconds for CPU benchmark
}

def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(saved)
                return config
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_settings(config_dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4)
        return True
    except Exception:
        return False

# Direct threshold constants for backward compatibility and fast access
current_cfg = load_settings()
STORAGE_WARNING_THRESHOLD = current_cfg.get("storage_warning_threshold", 85.0)
TEMP_WARNING_THRESHOLD = current_cfg.get("temp_warning_threshold", 75.0)
TEMP_CRITICAL_THRESHOLD = current_cfg.get("temp_critical_threshold", 85.0)
BATTERY_LOW_THRESHOLD = current_cfg.get("battery_low_threshold", 20.0)
RAM_WARNING_THRESHOLD = current_cfg.get("ram_warning_threshold", 80.0)
