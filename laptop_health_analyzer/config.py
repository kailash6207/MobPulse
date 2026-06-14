# config.py

# Storage threshold (Percentage used)
STORAGE_WARNING_THRESHOLD = 85.0  # Alert if disk is more than 85% full

# Temperature thresholds (in Celsius)
TEMP_WARNING_THRESHOLD = 75.0     # Warm, keep an eye on it
TEMP_CRITICAL_THRESHOLD = 85.0    # Hot, throttling or damage risk

# Battery threshold
BATTERY_LOW_THRESHOLD = 20.0      # Alert if unplugged and below 20%
