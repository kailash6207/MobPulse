# analyzer.py
import psutil
import shutil
from config import STORAGE_WARNING_THRESHOLD, TEMP_WARNING_THRESHOLD, TEMP_CRITICAL_THRESHOLD, BATTERY_LOW_THRESHOLD

class LaptopHealthAnalyzer:
    def __init__(self):
        pass

    def get_battery_health(self):
        """Fetches battery charge, plugged-in status, and remaining time."""
        battery = psutil.sensors_battery()
        if not battery:
            return {"status": "Error", "message": "No battery detected (likely a desktop)."}
        
        return {
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "secsleft": battery.secsleft
        }

    def get_storage_usage(self):
        """Fetches storage statistics for the primary partition."""
        # Focuses on the root/primary drive
        total, used, free = shutil.disk_usage("/")
        
        # Convert bytes to Gigabytes
        gb = 1024 ** 3
        return {
            "total_gb": round(total / gb, 2),
            "used_gb": round(used / gb, 2),
            "free_gb": round(free / gb, 2),
            "percent_used": round((used / total) * 100, 2)
        }

    def get_temperature(self):
        """Fetches CPU temperature. Falls back gracefully if OS restricts access."""
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return {"status": "Unsupported", "current": None, "message": "Temperature sensors not accessible."}
            
            # Look for common CPU temperature keys
            for key in ['coretemp', 'cpu_thermal', 'acpitz', 'amd_sensors']:
                if key in temps:
                    return {"status": "Success", "current": temps[key][0].current}
            
            # If specific key not found, grab the first available sensor
            first_key = list(temps.keys())[0]
            return {"status": "Success", "current": temps[first_key][0].current}
            
        except AttributeError:
            # High probability of happening on Windows standard command lines without admin rights
            return {"status": "Unsupported", "current": None, "message": "Temperature reading unsupported on this OS/permission level."}

    def generate_predictive_alerts(self, battery, storage, temp):
        """Analyzes data against config thresholds to predict maintenance issues."""
        alerts = []

        # 1. Storage Analysis
        if storage["percent_used"] >= STORAGE_WARNING_THRESHOLD:
            alerts.append(f"[!] PREDICTIVE ALERT: Storage is at {storage['percent_used']}%. High disk usage can degrade SSD lifespan and system swap file performance. Clean up space.")

        # 2. Temperature Analysis
        if temp["status"] == "Success" and temp["current"]:
            current_temp = temp["current"]
            if current_temp >= TEMP_CRITICAL_THRESHOLD:
                alerts.append(f"[!!!] CRITICAL ALERT: CPU Temp is {current_temp}C! Extreme thermal throttling active. Check fan vents immediately.")
            elif current_temp >= TEMP_WARNING_THRESHOLD:
                alerts.append(f"[!] WARNING: CPU Temp is elevated ({current_temp}C). Close heavy background applications.")

        # 3. Battery Analysis
        if "percent" in battery:
            if battery["percent"] <= BATTERY_LOW_THRESHOLD and not battery["power_plugged"]:
                alerts.append(f"[!] BATTERY ALERT: Battery is low ({battery['percent']}%). Plug in to avoid sudden shutdown.")
        
        if not alerts:
            alerts.append("[v] System health nominal. No predictive maintenance required.")
            
        return alerts
