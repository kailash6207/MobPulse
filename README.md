# MobPulse & Laptop Health Suite Pro 📱💻

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Android](https://img.shields.io/badge/Android-Jetpack%20Compose-green.svg?logo=android&logoColor=white)](https://developer.android.com/jetpack/compose)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9%2B-purple.svg?logo=kotlin&logoColor=white)](https://kotlinlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A unified hardware vitals, battery wear, system diagnostics, and performance optimization suite designed for both **Laptops (Desktop Python Suite)** and **Mobile Devices (Android Jetpack Compose)**.

---

## 💻 Laptop Health Suite Pro — Ultimate Edition (Python)

An advanced multi-threaded native Windows hardware telemetry, diagnostics, and system optimization suite built with **CustomTkinter** and **Python 3.12**.

Equipped with low-level kernel hooks (`MSAcpi_ThermalZoneTemperature`, CIM/WMI hardware counters, `powercfg`, and Windows Working Set memory optimization APIs), this suite delivers real-time hardware telemetry, automated health scoring, deep battery degradation analysis, active memory purging, SSD speed benchmarking, network radar, and professional dark-mode HTML audit reports.

### 🌟 Key Laptop Suite Features:

* **📊 Live Hardware Dashboard & Overall Health Score (0–100):**
  * Automated composite scoring factoring in **Battery Wear (25%)**, **CPU Thermals (20%)**, **RAM Pressure (20%)**, **Disk Capacity (20%)**, and **Network Latency (15%)**.
  * Visualized with an animated glowing circular gauge, grade badges (**A+**, **A**, **B**, **C**, **F**), and quick-glance vitals cards.

* **💻 Deep Hardware Specs Hub & Interactive Process Manager:**
  * Complete hardware profiling: Processor model, Cores/Threads/Architecture, GPU model, VRAM & Driver version, RAM total, Storage device, OS build, and exact Uptime.
  * **Per-Core CPU Load Matrix:** Live visual progress bars tracking individual logical core loads.
  * **⚡ Turbo RAM Purge Engine:** Directly invokes the Windows API (`EmptyWorkingSet`) across background processes to safely reclaim hundreds of MBs of standby memory without closing applications.
  * **Process Killer:** Search, sort by memory/CPU, and terminate selected processes.

* **🔋 Battery Lab & Wear Analysis:**
  * Extracts factory Design Capacity (mWh) vs. Full Charge Capacity (mWh) to compute true cell wear percentage and cycle counts via `powercfg` and CIM classes.
  * Live discharge rate and remaining battery runtime estimator.
  * **Windows Power Plan Switcher:** 1-click switching between *Balanced*, *High Performance*, *Power Saver*, and *Ultimate Power*.

* **🗄️ Storage Deep Dive, SSD Benchmark & Junk Cleaner:**
  * Multi-partition space tracking with SSD / NVMe / HDD drive type detection.
  * Real-time Disk I/O throughput (Read & Write MB/s).
  * **⚡ Quick SSD Speed Benchmark:** Non-destructive 32MB sequential read & write throughput test.
  * **🧹 Smart Temp & Junk Cleaner:** Scans and cleans `%TEMP%` and Windows temporary caches with a live byte counter.

* **🌐 Network & Wi-Fi Radar:**
  * Ping latency, micro-stutter jitter variation, and Wi-Fi signal quality (%).
  * Connected SSID, Radio Type (802.11ax/ac), and link negotiation rates (Rx/Tx Mbps).
  * Instantaneous Download & Upload bandwidth speedometers.
  * One-click DNS resolver cache flush (`ipconfig /flushdns`) and DHCP IP renewal (`ipconfig /renew`).

* **📈 Live Analytics & Multi-Core CPU Stress Benchmark:**
  * Multi-metric vector waveform chart with metric toggles (CPU %, RAM %, Battery %, Thermals °C, Ping ms).
  * **🔥 Multi-Core CPU Stress Benchmark:** Stresses 100% of all processor threads (3s / 5s / 10s), calculating total operations score and recording thermal delta.

* **📑 Diagnostic Reports:**
  * **🌐 Responsive Dark-Mode HTML Report:** Generates a full interactive diagnostic report on the Desktop ready to open in any web browser.
  * **📝 System Audit Log (.TXT):** Timestamped hardware audit log for technicians.

---

## 📱 Mobile App — MobPulse (Android)

Built with **Kotlin** and **Jetpack Compose**, this app provides deep mobile hardware telemetry, battery degradation tracking, and lag diagnostics.

### 🌟 Key Mobile Features:
- **🔋 Battery Trend Graph:** Visualizes battery level and charge curves over time with custom Canvas charts.
- **🕒 Automated Background Tracking:** Records device health stats every 15 minutes using Android `WorkManager`.
- **🌐 Network Quality Radar:** Real-time Wi-Fi signal strength and Ping latency testing.
- **🧠 Lag & Throttling Diagnostics:** Identifies performance bottlenecks, high background task counts, and thermal constraints.
- **💾 Resource Monitors:** Real-time RAM allocation and internal storage utilization.

---

## 📂 Project Structure

```
D:\lap_Health/
│
├── app/                           # Android MobPulse Application (Jetpack Compose & Kotlin)
│   ├── src/
│   ├── build.gradle.kts
│   └── ...
│
├── laptop_health_analyzer/        # Laptop Health Suite Pro (CustomTkinter & Python)
│   ├── analyzer.py                # Hardware telemetry, RAM purge, SSD bench & diagnostics engine
│   ├── config.py                  # Settings management & configurable alert thresholds
│   ├── main.py                    # Modern CustomTkinter multi-tab GUI application
│   ├── requirements.txt           # Python package dependencies
│   └── README.md                  # Laptop module documentation
│
└── README.md                      # Root Project Documentation
```

---

## 🚀 Quick Start & Installation

### Running the Laptop Suite (Python)

1. **Navigate to the analyzer directory:**
   ```bash
   cd laptop_health_analyzer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   python main.py
   ```

4. **(Optional) Build Standalone Windows Executable (.exe):**
   ```bash
   pip install pyinstaller
   python -m PyInstaller --noconsole --onefile main.py
   ```

### Running the Mobile App (Android)

1. Open the project root in **Android Studio** (Giraffe or newer).
2. Sync Gradle dependencies.
3. Deploy to your physical Android device or emulator.

---

## 🛠️ Tech Stack

| Platform | Technology | Description |
| :--- | :--- | :--- |
| **Laptop (GUI)** | CustomTkinter 5.2+ | Modern Dark/Light Fluent interface with high-DPI scaling |
| **Laptop (Core)** | Python 3.12, `psutil` | Low-level hardware sensors, memory and disk I/O queries |
| **Laptop (Hooks)**| Windows API (`psapi`), WMI, CIM, `powercfg` | WorkingSet RAM trim, thermal counters, battery reports |
| **Mobile (UI)** | Jetpack Compose | Declarative native Android UI |
| **Mobile (Core)**| Kotlin, WorkManager, Coroutines | Periodic background telemetry logging |

---

## 📄 License

This project is licensed under the **MIT License**.
Created with ❤️ by [kailash6207](https://github.com/kailash6207).
