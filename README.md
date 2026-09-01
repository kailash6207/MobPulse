# MobPulse & Laptop Health Suite Pro 📱💻

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Android](https://img.shields.io/badge/Android-Jetpack%20Compose-green.svg?logo=android&logoColor=white)](https://developer.android.com/jetpack/compose)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9%2B-purple.svg?logo=kotlin&logoColor=white)](https://kotlinlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A unified hardware vitals, battery wear, system diagnostics, and performance optimization suite for **Laptops (Desktop Python Suite)** and **Mobile Devices (Android Jetpack Compose)**.

---

## 🏛️ System Architecture

```mermaid
graph TD
    A["Windows Hardware and Kernel<br/>ACPI Thermals, Battery, RAM, Disks, Wi-Fi"]
    B["Telemetry and Scoring Engine<br/>Health Score, Turbo RAM Purge, SSD Benchmark"]
    C["CustomTkinter Dashboard<br/>Circular Health Gauge, Vitals Cards, Vector Waveform"]
    D["Persistence and Export<br/>HTML Dashboard Report, CSV Logs, Text Audit"]

    A -->|Raw Telemetry Data| B
    B -->|Live Metrics and Health Score| C
    B -->|Export and Stream Logs| D
```

---

## 🔄 Real-Time Telemetry Workflow

```mermaid
sequenceDiagram
    autonumber
    participant Kernel as Windows Hardware
    participant Engine as Telemetry Engine
    participant GUI as Dashboard UI

    loop Every 3 Seconds
        Engine->>Kernel: 1. Poll Vitals: CPU, Battery, RAM, Disk, Ping
        Kernel-->>Engine: 2. Return Hardware Telemetry
        Engine->>Engine: 3. Compute Health Score and Advisories
        Engine->>GUI: 4. Update Health Gauge, Cards and Waveform
    end
```

---

## ⚡ Turbo RAM Purge Workflow

```mermaid
flowchart LR
    A["Click Turbo RAM Purge"] --> B["Trims Working Sets via Windows API"] --> C["Frees Standby RAM: 900+ MB"]
```

---

## 🚀 Key Laptop Features

- **📊 0–100 Health Score:** Weighted index of Battery Wear (25%), CPU Thermals (20%), RAM (20%), Disk (20%), and Network (15%).
- **⚡ Turbo RAM Purge:** Windows API (`EmptyWorkingSet`) frees standby memory without closing apps.
- **🔋 Battery Lab:** True wear degradation index (%), cycle count, and 1-click Power Plan switcher.
- **🗄️ Storage & Benchmark:** Real-time Disk I/O, 32MB SSD speed test, and temporary junk cleaner.
- **🌐 Network Radar:** Ping latency, micro-jitter stability, Wi-Fi signal %, and live throughput.
- **📈 Live Analytics & Stress Test:** Multi-metric vector chart and multi-core CPU stress benchmark.
- **📑 Diagnostic Reports:** Generates dark-mode HTML dashboard and text audit logs on Desktop.

---

## 📱 Mobile App — MobPulse (Android)

- **🔋 Battery Trend Graph:** Charge/discharge curves over time.
- **🕒 Background Tracking:** Health logging every 15 mins via `WorkManager`.
- **🌐 Network Radar & 🧠 Lag Diagnostics:** Wi-Fi signal, latency tests, and thermal throttling checks.

---

## 🏃 Quick Start (Laptop Suite)

```bash
cd laptop_health_analyzer
pip install -r requirements.txt
python main.py
```

---

## 📄 License
MIT License. Created by [kailash6207](https://github.com/kailash6207).
