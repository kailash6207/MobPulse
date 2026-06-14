# MobPulse 📱💻

A comprehensive health and performance monitoring tool for both **Laptops (Python)** and **Mobile Devices (Android)**.

## 📱 Mobile App (MobPulse)

Built with **Jetpack Compose**, this app provides a deep dive into your phone's status and helps diagnose performance issues.

### Key Features:
- **🔋 Battery Trend Graph**: Visualizes battery level over time using a custom Canvas chart.
- **🕒 Background Tracking**: Automatically records health stats every 15 minutes using `WorkManager`.
- **🌐 Network Health**: Real-time Wi-Fi signal strength and Ping latency tests.
- **🧠 Lag Diagnostics**: Identifies causes of slowdowns, including Thermal Throttling and high background process counts.
- **💾 Resource Monitoring**: Live tracking of RAM usage and Storage utilization.

### Technical Stack:
- **Kotlin** & **Jetpack Compose**
- **WorkManager** for background tasks
- **SharedPreferences** for persistent data history

---

## 💻 Laptop Tool (Python)

A lightweight CLI dashboard for quick hardware checks on your computer.

### Key Features:
- **Real-time Stats**: Battery, Storage, and CPU Temperature.
- **Predictive Alerts**: Notifies you when hardware exceeds safe thresholds.
- **Compatibility**: Optimized for Windows terminals with ASCII fallback.

### Prerequisites:
```bash
pip install psutil
```

### Usage:
```bash
cd laptop_health_analyzer
python main.py
```

---

## 📂 Project Structure
- `app/`: The Android project source code.
- `laptop_health_analyzer/`: The Python CLI tool source code.

## 🚀 Getting Started
1. **Mobile**: Open the `app` folder in Android Studio and deploy to your device.
2. **Laptop**: Run the Python script as described above.

---

## 📄 License
MIT License
