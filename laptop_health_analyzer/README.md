# ⚡ Laptop Health Suite Pro — Ultimate Edition 💻

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A multi-threaded native Windows hardware telemetry, diagnostics, and system optimization suite built with **CustomTkinter** and **Python 3.12**.

Equipped with low-level kernel hooks (`MSAcpi_ThermalZoneTemperature`, CIM/WMI hardware counters, `powercfg`, and Windows Working Set memory optimization APIs), this suite delivers real-time hardware telemetry, automated health scoring, deep battery degradation analysis, active memory purging, SSD speed benchmarking, network radar, and professional dark-mode HTML audit reports.

---

## 🏛️ System Architecture

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

## 🔄 Real-Time Telemetry & Health Scoring Workflow

```mermaid
sequenceDiagram
    autonumber
    participant Poller as ⏱️ Background Poller
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

## 🚀 Key Features

- **📊 Hardware Vitals Dashboard:** Real-time monitoring of CPU core load %, frequencies, RAM allocation, battery level %, and storage space.
- **⚡ Overall Laptop Health Score (0–100):** Weighted multi-variable scoring model evaluating Battery Wear (25%), CPU Thermals (20%), Memory Pressure (20%), Disk Space (20%), and Network Latency (15%).
- **🧠 Interactive Process Manager & Turbo RAM Purge:** Live sortable process table with process termination and 1-click `EmptyWorkingSet` memory optimization.
- **🔋 Battery Lab & Wear Analysis:** Design vs. Full Charge capacity wear degradation index (%), cycle count, and Windows Power Plan switcher (*Balanced*, *High Performance*, *Power Saver*, *Ultimate Power*).
- **🗄️ Storage Deep Dive & SSD Benchmark:** Live Disk I/O throughput (MB/s), sequential speed benchmark test, and temporary junk file cleaner.
- **🌐 Network & Wi-Fi Radar:** Ping latency, micro-stutter jitter stability, Wi-Fi signal %, and live upload/download bandwidth.
- **📈 Real-Time Analytics & CPU Stress Test:** Multi-metric vector waveform graph and multi-core CPU stress benchmark.
- **📑 HTML & Text Diagnostic Audit Reports:** Generates professional reports directly to the Desktop.

---

## 🏃 Quick Start

```bash
cd laptop_health_analyzer
pip install -r requirements.txt
python main.py
```
