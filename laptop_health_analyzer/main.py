# main.py
import os
import time
from analyzer import LaptopHealthAnalyzer

def clear_screen():
    """Clears the terminal screen for a clean dashboard look."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_dashboard():
    analyzer = LaptopHealthAnalyzer()
    
    # Gather hardware data
    battery = analyzer.get_battery_health()
    storage = analyzer.get_storage_usage()
    temp = analyzer.get_temperature()
    alerts = analyzer.generate_predictive_alerts(battery, storage, temp)
    
    # Render dashboard
    print("=" * 60)
    print("      LAPTOP HEALTH ANALYZER & MAINTENANCE PORTAL      ")
    print("=" * 60)
    
    # 1. Battery Section
    print("\n[1] BATTERY HEALTH & STATUS")
    if "percent" in battery:
        status_str = "Charging/Plugged-in" if battery["power_plugged"] else "Discharging"
        print(f"  * Charge Level: {battery['percent']}%")
        print(f"  * Status:       {status_str}")
    else:
        print(f"  * Status:       {battery['message']}")

    # 2. Storage Section
    print("\n[2] STORAGE SPACE UTILIZATION")
    print(f"  * Total Size:   {storage['total_gb']} GB")
    print(f"  * Used Space:   {storage['used_gb']} GB ({storage['percent_used']}%)")
    print(f"  * Free Space:   {storage['free_gb']} GB")
    
    # Simple visual progress bar for storage
    bar_length = 20
    filled_length = int(round(bar_length * storage['percent_used'] / 100))
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    print(f"  * Progress:     [{bar}]")

    # 3. Temperature Section
    print("\n[3] TEMPERATURE MONITORING")
    if temp["status"] == "Success":
        print(f"  * CPU Core Temp: {temp['current']} C")
    else:
        print(f"  * CPU Core Temp: {temp['message']}")

    # 4. Predictive Maintenance Alerts Section
    print("\n" + "=" * 60)
    print("PREDICTIVE MAINTENANCE & ALERTS")
    print("=" * 60)
    for alert in alerts:
        print(f" {alert}")
    print("=" * 60)

def main():
    try:
        while True:
            clear_screen()
            display_dashboard()
            print("\nPress Ctrl+C to exit. (Auto-refreshing every 5 seconds...)")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nExiting Laptop Health Analyzer. Keep your hardware safe!")

if __name__ == "__main__":
    main()
