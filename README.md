# MobPulse & Laptop Health Suite Pro 📱💻

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Android](https://img.shields.io/badge/Android-Jetpack%20Compose-green.svg?logo=android&logoColor=white)](https://developer.android.com/jetpack/compose)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9%2B-purple.svg?logo=kotlin&logoColor=white)](https://kotlinlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A unified hardware vitals, battery wear, system diagnostics, and performance optimization suite designed for both **Laptops (Desktop Python Suite)** and **Mobile Devices (Android Jetpack Compose)**.

---

## 🏛️ System Architecture Diagram

```mermaid
graph TB
    subgraph Hardware_Kernel ["🖥️ Hardware & Windows Kernel Layer"]
        H1["Motherboard ACPI Sensors<br/>(Win32_PerfThermal)"]
        H2["Battery Microcontroller<br/>(powercfg & CIM)"]
        H3["Physical Storage Devices<br/>(NVMe / SSD / HDD)"]
        H4["Network & Wi-Fi NIC<br/>(netsh & ICMP)"]
        H5["Memory Controller<br/>(psapi.dll WorkingSet)"]
    end

    subgraph Telemetry_Engine ["⚙️ Core Telemetry & Diagnostics Engine (analyzer.py)"]
        T1["Background Poller Thread (3s Cycle)"]
        T2["Battery Lab & Degradation Index"]
        T3["Multi-Tier Thermal Pipeline"]
        T4["Disk I/O & SSD Benchmark"]
        T5["Wi-Fi Signal & Bandwidth Radar"]
        T6["Turbo RAM Clean (EmptyWorkingSet)"]
        T7["Multi-Core CPU Stress Benchmark"]
        T8["Weighted Health Scoring Algorithm"]
        T9["Predictive Maintenance Advisories"]
    end

    subgraph Presentation_Layer ["🎨 Presentation Layer (CustomTkinter GUI)"]
        UI1["📊 Dashboard (Circular Health Gauge)"]
        UI2["💻 Hardware Hub & Process Manager"]
        UI3["🔋 Battery Lab & Power Plan Switcher"]
        UI4["🗄️ Storage & Temp Junk Cleaner"]
        UI5["🌐 Network Radar & Speedometer"]
        UI6["📈 Live Analytics Vector Waveform"]
        UI7["⚙️ Settings & Diagnostic Reports"]
    end

    subgraph Data_Export ["💾 Persistence & Export Layer"]
        D1["Settings JSON (lap_health_settings.json)"]
        D2["Metrics CSV Log (health_history.csv)"]
        D3["🌐 Dark-Mode HTML Report (.html)"]
        D4["📝 Full System Audit Log (.txt)"]
    end

    H1 --> T3
    H2 --> T2
    H3 --> T4
    H4 --> T5
    H5 --> T6

    T1 --> T2 & T3 & T4 & T5 & T6
    T2 & T3 & T4 & T5 --> T8
    T8 --> T9

    T8 --> UI1
    T6 --> UI2
    T2 --> UI3
    T4 --> UI4
    T5 --> UI5
    T7 --> UI6
    T9 --> UI1 & UI7

    T8 --> D2
    UI7 --> D3 & D4
    UI7 --> D1
```

---

## 🔄 Core Telemetry & Health Scoring Workflow

```mermaid
sequenceDiagram
    autonumber
    participant Poller as ⏱️ Background Thread
    participant Analyzer as ⚙️ LaptopHealthAnalyzer
    participant Kernel as 🪟 Windows Kernel / WMI
    participant ScoreEngine as 🧠 Health Score Engine
    participant GUI as 🎨 CustomTkinter UI

    loop Every 3 Seconds
        Poller->>Analyzer: Poll hardware metrics
        par Parallel Hardware Telemetry
            Analyzer->>Kernel: Query ACPI / MSAcpi Thermals
            Analyzer->>Kernel: Read powercfg Battery Capacity & Cycles
            Analyzer->>Kernel: Sample Disk I/O & Network Throughput
            Analyzer->>Kernel: Inspect Process Footprints & RAM
        end
        Kernel-->>Analyzer: Return Raw Telemetry Data
        Analyzer->>ScoreEngine: Compute Weighted Composite Score
        Note over ScoreEngine: Battery (25%) + Temp (20%) + RAM (20%) + Disk (20%) + Net (15%)
        ScoreEngine-->>Analyzer: Score (0-100), Grade (A+ to F), Rating
        Analyzer->>Analyzer: Generate Predictive Alerts & Advisories
        Analyzer->>Analyzer: Stream snapshot to health_history.csv
        Analyzer->>GUI: Thread-Safe Dispatch (root.after)
        GUI->>GUI: Update Circular Gauge, Metric Cards & Vector Waveform
    end
```

---

## ⚡ Turbo RAM Purge Engine Workflow

```mermaid
flowchart TD
    A["User clicks '⚡ Turbo RAM Purge'"] --> B["Enumerate Active PIDs via psutil"]
    B --> C{"PID <= 4 (System/Idle)?"}
    C -- Yes --> D["Skip Protected Process"]
    C -- No --> E["Open Process Handle<br/>(PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION)"]
    E --> F["Invoke ctypes.windll.psapi.EmptyWorkingSet"]
    F --> G["Windows OS trims standby & unused working set memory"]
    G --> H["Close Process Handle"]
    H --> I["Iterate Next PID"]
    I --> J{"All PIDs Processed?"}
    J -- No --> B
    J -- Yes --> K["Measure delta: Before Used GB vs After Used GB"]
    K --> L["Display Toast Dialog: Freed XXX MB RAM across N apps"]
    L --> M["Refresh RAM allocation bar on GUI"]
```

---

## 🚀 Key Features & Capabilities

### 1. 📊 Hardware Vitals & Health Score Dashboard
- **Overall Health Score (0–100):** Weighted multi-variable scoring model:
  $$\text{Score} = (0.25 \times \text{Bat}) + (0.20 \times \text{Temp}) + (0.20 \times \text{RAM}) + (0.20 \times \text{Disk}) + (0.15 \times \text{Net})$$
- **Live Vitals Grid:** Real-time CPU load %, Frequency (GHz), RAM allocation %, Battery charge %, and Primary Storage space.
- **Predictive Diagnostics Feed:** Real-time actionable alerts with step-by-step recommendations.

### 2. 💻 Hardware Hub & Interactive Process Manager
- **Deep System Specs Inspector:** Full hardware profile including Processor details (Cores/Threads/Arch), GPU model, VRAM & Driver version, RAM total, Primary storage device, OS build, and exact System Uptime.
- **Per-Core CPU Load Matrix:** Live visual progress bars tracking load across every logical core.
- **Interactive Process Manager:** Searchable and filterable process table showing PID, Application Name, Memory Footprint (MB), CPU %, and User Account.
- **⚡ Turbo RAM Purge Engine:** Windows API (`EmptyWorkingSet`) working set memory optimizer that frees hundreds of megabytes of standby RAM in a single click without closing apps.
- **Process Killer:** Terminate unresponsive or heavy processes directly with safety confirmation.

### 3. 🔋 Battery Lab & Wear Analysis
- **Hardware Degradation Calculator:** Extracts Design Capacity (mWh) vs. Full Charge Capacity (mWh) to compute true cell wear percentage.
- **Cycle Count & Chemistry Telemetry:** Reads hardware cycle counts, manufacturer, and battery chemistry.
- **Live Discharge & Runtime Estimator:** Calculates battery runtime based on dynamic system draw.
- **Windows Power Plan Switcher:** 1-click switching between *Balanced*, *High Performance*, *Power Saver*, and *Ultimate Power*.
- **Battery Preservation Guide:** Tips on 80% charging limits and thermal protection.

### 4. 🗄️ Storage Deep Dive, SSD Benchmark & Junk Cleaner
- **Multi-Drive Volume Mapping:** Dynamic space monitoring across all mounted partitions (`C:\`, `D:\`, etc.) with file system and drive type detection.
- **Real-Time Disk I/O Speeds:** Live Read MB/s and Write MB/s throughput monitors.
- **⚡ Quick SSD Speed Benchmark:** Non-destructive 32MB sequential write & read test measuring actual disk throughput.
- **🧹 Smart Temp & Junk Cleaner:** Scans and cleans `%TEMP%` and Windows temporary junk with a live byte counter.

### 5. 🌐 Network & Wi-Fi Radar
- **Ping & Jitter Stability Radar:** Active ping latency and micro-stutter jitter measurements to ensure smooth video calls and low-latency gaming.
- **Wi-Fi Signal & Link Rates:** Live SSID, Signal Strength (%), Radio Type (802.11ax/ac), and Transmit/Receive link speeds (Mbps).
- **Real-Time Bandwidth Speedometer:** Instantaneous Download (KB/s) and Upload (KB/s) throughput.
- **Network Recovery Toolkit:** One-click DNS cache flush (`ipconfig /flushdns`) and DHCP IP renewal (`ipconfig /renew`).

### 6. 📈 Live Analytics & Multi-Core CPU Stress Benchmark
- **Real-Time Waveform Graph:** Multi-metric vector chart with custom checkbox filters for CPU %, RAM %, Battery %, Thermals (°C), and Ping (ms).
- **🔥 CPU Stress Benchmark:** Multi-threaded mathematical benchmark (3s / 5s / 10s) testing 100% processor load, reporting operations score and thermal delta.

### 7. 📑 Report Generation & Diagnostics Audit
- **🌐 Modern HTML Dashboard Report:** Generates a complete dark-mode HTML report on your Desktop ready to open in any web browser.
- **📝 Text Audit Log (.TXT):** Detailed timestamped hardware log for technicians and diagnostics.

---

## 📱 Mobile App — MobPulse (Android)

Built with **Kotlin** and **Jetpack Compose**, this app provides deep mobile hardware telemetry, battery degradation tracking, and lag diagnostics.

```mermaid
graph LR
    subgraph Mobile_Architecture ["📱 MobPulse Android Architecture"]
        M1["Jetpack Compose UI"] --> M2["ViewModel & StateFlow"]
        M2 --> M3["Battery & Hardware Sensors"]
        M2 --> M4["WorkManager (15-min background sync)"]
        M4 --> M5["SharedPreferences (Historical Log)"]
    end
```

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
└── README.md                      # Root Project Documentation (with Flowcharts & Architecture)
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
