# analyzer.py
import psutil
import shutil
import os
import subprocess
import csv
import re
import time
import math
import ctypes
import platform
import tempfile
import threading
from datetime import datetime, timedelta
from config import load_settings

class LaptopHealthAnalyzer:
    def __init__(self):
        self.history_file = "health_history.csv"
        self.settings = load_settings()
        self.initialize_history_log()
        
        # Rolling metrics history for live waveform graphs (max 30 data points)
        self.history_buffer = []
        self.ping_history = []
        
        # IO Tracking for throughput rates (MB/s and KB/s)
        self.last_disk_io = psutil.disk_io_counters()
        self.last_disk_time = time.time()
        self.last_net_io = psutil.net_io_counters()
        self.last_net_time = time.time()
        
        # Cached static hardware specifications
        self.cached_specs = None
        self._load_static_specs()

    def _load_static_specs(self):
        """Loads static hardware specs once on startup to ensure instant GUI rendering."""
        def fetch():
            specs = {
                "cpu_name": platform.processor() or "Multi-Core x64 Processor",
                "cpu_cores_physical": psutil.cpu_count(logical=False) or 2,
                "cpu_cores_logical": psutil.cpu_count(logical=True) or 4,
                "cpu_arch": platform.machine(),
                "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 1),
                "gpu_name": "Integrated Graphics Adapter",
                "gpu_driver": "N/A",
                "gpu_vram_gb": "Shared",
                "os_name": f"{platform.system()} {platform.release()}",
                "os_build": platform.version(),
                "hostname": platform.node(),
                "disk_model": "Primary High-Speed Storage",
                "disk_type": "SSD"
            }
            
            if os.name == 'nt':
                # CPU Name Query via CIM
                try:
                    out = subprocess.check_output(
                        ["powershell", "-Command", "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"],
                        creationflags=0x08000000, stderr=subprocess.DEVNULL
                    ).decode().strip()
                    if out:
                        specs["cpu_name"] = out.splitlines()[0].strip()
                except Exception:
                    pass
                
                # GPU Query via CIM
                try:
                    out = subprocess.check_output(
                        ["powershell", "-Command", "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion | ConvertTo-Json"],
                        creationflags=0x08000000, stderr=subprocess.DEVNULL
                    ).decode().strip()
                    if out:
                        import json
                        data = json.loads(out)
                        if isinstance(data, list) and len(data) > 0:
                            item = data[-1]
                            for gpu in data:
                                if "Intel" not in gpu.get("Name", "") and "Parsec" not in gpu.get("Name", ""):
                                    item = gpu
                                    break
                            specs["gpu_name"] = item.get("Name", specs["gpu_name"])
                            specs["gpu_driver"] = item.get("DriverVersion", "N/A")
                            if item.get("AdapterRAM"):
                                specs["gpu_vram_gb"] = f"{round(int(item['AdapterRAM']) / (1024**3), 1)} GB"
                        elif isinstance(data, dict):
                            specs["gpu_name"] = data.get("Name", specs["gpu_name"])
                            specs["gpu_driver"] = data.get("DriverVersion", "N/A")
                except Exception:
                    pass

                # Physical Disk Query
                try:
                    out = subprocess.check_output(
                        ["powershell", "-Command", "Get-PhysicalDisk | Select-Object FriendlyName, MediaType | ConvertTo-Json"],
                        creationflags=0x08000000, stderr=subprocess.DEVNULL
                    ).decode().strip()
                    if out:
                        import json
                        d_data = json.loads(out)
                        if isinstance(d_data, list) and len(d_data) > 0:
                            specs["disk_model"] = d_data[0].get("FriendlyName", "Solid State Drive")
                            specs["disk_type"] = d_data[0].get("MediaType", "SSD")
                        elif isinstance(d_data, dict):
                            specs["disk_model"] = d_data.get("FriendlyName", "Solid State Drive")
                            specs["disk_type"] = d_data.get("MediaType", "SSD")
                except Exception:
                    pass

                # OS Caption Query
                try:
                    out = subprocess.check_output(
                        ["powershell", "-Command", "Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption"],
                        creationflags=0x08000000, stderr=subprocess.DEVNULL
                    ).decode().strip()
                    if out:
                        specs["os_name"] = out.strip()
                except Exception:
                    pass

            self.cached_specs = specs

        t = threading.Thread(target=fetch, daemon=True)
        t.start()

    def get_system_specs(self):
        if self.cached_specs:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            mins, secs = divmod(remainder, 60)
            
            uptime_str = f"{days}d {hours}h {mins}m" if days > 0 else f"{hours}h {mins}m {secs}s"
            
            res = self.cached_specs.copy()
            res["uptime"] = uptime_str
            res["boot_time"] = boot_time.strftime("%Y-%m-%d %H:%M:%S")
            return res
            
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        return {
            "cpu_name": platform.processor() or "x64 Processor",
            "cpu_cores_physical": psutil.cpu_count(logical=False) or 2,
            "cpu_cores_logical": psutil.cpu_count(logical=True) or 4,
            "cpu_arch": platform.machine(),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 1),
            "gpu_name": "Graphics Processor",
            "gpu_driver": "N/A",
            "gpu_vram_gb": "Dynamic",
            "os_name": platform.platform(),
            "os_build": platform.version(),
            "hostname": platform.node(),
            "disk_model": "Storage Drive",
            "disk_type": "SSD",
            "uptime": "Calculating...",
            "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def initialize_history_log(self):
        if not os.path.exists(self.history_file):
            try:
                with open(self.history_file, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Battery_Percent", "RAM_Percent", "CPU_Percent", "CPU_Temp", "Ping_ms"])
            except Exception:
                pass

    def log_current_metrics(self, battery_pct, ram_pct, cpu_pct, cpu_temp, ping_ms=0):
        temp_val = cpu_temp if cpu_temp is not None else 0
        bat_val = battery_pct if battery_pct is not None else 0
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        point = {
            "time": timestamp,
            "battery": float(bat_val),
            "ram": float(ram_pct),
            "cpu": float(cpu_pct),
            "temp": float(temp_val),
            "ping": float(ping_ms if ping_ms < 999 else 0)
        }
        self.history_buffer.append(point)
        if len(self.history_buffer) > 30:
            self.history_buffer.pop(0)

        try:
            with open(self.history_file, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, bat_val, ram_pct, cpu_pct, temp_val, ping_ms])
        except Exception:
            pass

    def get_historical_data(self):
        if self.history_buffer:
            return self.history_buffer
        points = []
        if not os.path.exists(self.history_file):
            return points
        try:
            with open(self.history_file, mode='r', encoding='utf-8') as f:
                reader = list(csv.DictReader(f))
                last_entries = reader[-25:]
                for row in last_entries:
                    points.append({
                        "time": row.get("Timestamp", "--:--"),
                        "battery": float(row.get("Battery_Percent", 0)),
                        "ram": float(row.get("RAM_Percent", 0)),
                        "cpu": float(row.get("CPU_Percent", 0)),
                        "temp": float(row.get("CPU_Temp", 0)),
                        "ping": float(row.get("Ping_ms", 0))
                    })
        except Exception:
            pass
        return points

    def get_cpu_metrics(self):
        """Fetches detailed multi-core CPU metrics and frequencies."""
        overall_load = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(interval=None, percpu=True)
        freq = psutil.cpu_freq()
        cur_freq_ghz = round(freq.current / 1000.0, 2) if freq and freq.current else None
        
        return {
            "overall_percent": overall_load,
            "per_core_percent": per_core,
            "current_freq_ghz": cur_freq_ghz,
            "process_count": len(psutil.pids()),
            "thread_count": sum([p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info.get('num_threads')]) if hasattr(psutil.Process, 'num_threads') else 0
        }

    def get_ram_usage(self):
        virtual_mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        gb = 1024 ** 3
        mb = 1024 ** 2
        
        top_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    info = proc.info
                    mem_mb = info['memory_info'].rss / mb if info.get('memory_info') else 0
                    cpu_p = info.get('cpu_percent') or 0.0
                    top_processes.append({
                        "pid": info['pid'],
                        "name": info['name'] or "Unknown",
                        "memory_mb": round(mem_mb, 1),
                        "cpu_percent": round(cpu_p, 1)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            top_processes = sorted(top_processes, key=lambda x: x["memory_mb"], reverse=True)[:5]
        except Exception:
            top_processes = [{"pid": 0, "name": "System Process", "memory_mb": 0.0, "cpu_percent": 0.0}]

        return {
            "total_gb": round(virtual_mem.total / gb, 1),
            "used_gb": round(virtual_mem.used / gb, 1),
            "free_gb": round(virtual_mem.free / gb, 1),
            "available_gb": round(virtual_mem.available / gb, 1),
            "percent_used": virtual_mem.percent,
            "swap_total_gb": round(swap.total / gb, 1),
            "swap_used_gb": round(swap.used / gb, 1),
            "swap_percent": swap.percent,
            "top_apps": top_processes
        }

    def get_processes_list(self, limit=40, search_query=""):
        """Returns sorted list of active processes for the interactive process manager."""
        procs = []
        mb = 1024 ** 2
        query = search_query.lower().strip()
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'status', 'username']):
            try:
                p_info = proc.info
                name = p_info.get('name') or 'Unknown'
                if query and query not in name.lower() and str(p_info.get('pid')) not in query:
                    continue
                
                rss = p_info['memory_info'].rss / mb if p_info.get('memory_info') else 0
                procs.append({
                    "pid": p_info.get('pid'),
                    "name": name,
                    "memory_mb": round(rss, 1),
                    "cpu_percent": round(p_info.get('cpu_percent') or 0.0, 1),
                    "status": p_info.get('status') or "running",
                    "user": (p_info.get('username') or "").split('\\')[-1]
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        procs = sorted(procs, key=lambda x: x["memory_mb"], reverse=True)[:limit]
        return procs

    def kill_process(self, pid):
        """Safely terminates a process by PID."""
        try:
            p = psutil.Process(pid)
            p_name = p.name()
            p.terminate()
            p.wait(timeout=2)
            return True, f"Successfully terminated {p_name} (PID: {pid})"
        except psutil.TimeoutExpired:
            try:
                p.kill()
                return True, f"Force killed {pid}"
            except Exception as e:
                return False, f"Could not force kill: {e}"
        except Exception as e:
            return False, f"Failed to terminate process: {e}"

    def turbo_ram_clean(self):
        """Uses Windows API EmptyWorkingSet across safe processes to purge memory."""
        before_mem = psutil.virtual_memory().used
        trimmed_count = 0
        
        if os.name == 'nt':
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_SET_QUOTA = 0x0100
            
            for proc in psutil.process_iter(['pid']):
                try:
                    pid = proc.info['pid']
                    if pid <= 4:
                        continue
                    h_process = ctypes.windll.kernel32.OpenProcess(
                        PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, pid
                    )
                    if h_process:
                        res = ctypes.windll.psapi.EmptyWorkingSet(h_process)
                        ctypes.windll.kernel32.CloseHandle(h_process)
                        if res:
                            trimmed_count += 1
                except Exception:
                    pass

        time.sleep(0.3)
        after_mem = psutil.virtual_memory().used
        freed_mb = max(0.0, (before_mem - after_mem) / (1024 * 1024))
        
        return {
            "freed_mb": round(freed_mb, 1),
            "processes_trimmed": trimmed_count,
            "new_ram_percent": psutil.virtual_memory().percent
        }

    def get_storage_usage(self):
        drive_reports = []
        partitions = psutil.disk_partitions(all=False)
        gb = 1024 ** 3
        
        for partition in partitions:
            if 'cdrom' in partition.opts or not partition.mountpoint:
                continue
            try:
                usage = shutil.disk_usage(partition.mountpoint)
                percent_used = round((usage.used / usage.total) * 100, 1)
                
                drive_type = "Local Disk"
                if "removable" in partition.opts.lower():
                    drive_type = "USB / Removable"
                elif partition.mountpoint.upper().startswith("C:"):
                    drive_type = "System Primary Drive (SSD/NVMe)"
                else:
                    drive_type = "Secondary Partition"

                drive_reports.append({
                    "drive": partition.mountpoint,
                    "fstype": partition.fstype or "NTFS",
                    "type": drive_type,
                    "total_gb": round(usage.total / gb, 1),
                    "used_gb": round(usage.used / gb, 1),
                    "free_gb": round(usage.free / gb, 1),
                    "percent_used": percent_used
                })
            except PermissionError:
                continue
            except Exception:
                continue
        return drive_reports

    def get_disk_io_throughput(self):
        """Calculates instantaneous Read & Write speeds in MB/s."""
        now = time.time()
        current_io = psutil.disk_io_counters()
        dt = max(0.1, now - self.last_disk_time)
        
        read_mb_s = 0.0
        write_mb_s = 0.0
        
        if self.last_disk_io and current_io:
            read_bytes = current_io.read_bytes - self.last_disk_io.read_bytes
            write_bytes = current_io.write_bytes - self.last_disk_io.write_bytes
            read_mb_s = max(0.0, round((read_bytes / (1024 ** 2)) / dt, 2))
            write_mb_s = max(0.0, round((write_bytes / (1024 ** 2)) / dt, 2))
            
        self.last_disk_io = current_io
        self.last_disk_time = now
        
        return {"read_mb_s": read_mb_s, "write_mb_s": write_mb_s}

    def benchmark_disk_speed(self, size_mb=64):
        """Non-destructive sequential disk read/write throughput speed test."""
        data = os.urandom(1024 * 1024)
        temp_dir = tempfile.gettempdir()
        test_file = os.path.join(temp_dir, f"lh_disk_bench_{int(time.time())}.tmp")
        
        try:
            # Sequential Write Test
            t0 = time.perf_counter()
            with open(test_file, 'wb') as f:
                for _ in range(size_mb):
                    f.write(data)
                f.flush()
                os.fsync(f.fileno())
            t_write = max(0.001, time.perf_counter() - t0)
            write_speed = round(size_mb / t_write, 1)

            # Sequential Read Test
            t0 = time.perf_counter()
            with open(test_file, 'rb') as f:
                while f.read(1024 * 1024):
                    pass
            t_read = max(0.001, time.perf_counter() - t0)
            read_speed = round(size_mb / t_read, 1)

            # Rating
            if read_speed >= 1000:
                rating = "Ultra-Fast NVMe Gen4 SSD"
            elif read_speed >= 450:
                rating = "High-Speed SATA/NVMe SSD"
            elif read_speed >= 150:
                rating = "Standard SSD"
            else:
                rating = "Mechanical HDD / Legacy Disk"

            return {
                "success": True,
                "write_mb_s": write_speed,
                "read_mb_s": read_speed,
                "rating": rating,
                "test_size_mb": size_mb
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if os.path.exists(test_file):
                try:
                    os.remove(test_file)
                except Exception:
                    pass

    def scan_junk_files(self):
        """Scans temporary directories for cleanable junk files."""
        user_temp = os.environ.get('TEMP', tempfile.gettempdir())
        win_temp = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')
        
        targets = [user_temp]
        if os.path.exists(win_temp):
            targets.append(win_temp)
            
        total_bytes = 0
        file_count = 0
        
        for folder in targets:
            try:
                for root, dirs, files in os.walk(folder):
                    for f in files:
                        try:
                            fp = os.path.join(root, f)
                            total_bytes += os.path.getsize(fp)
                            file_count += 1
                        except Exception:
                            pass
            except Exception:
                pass
                
        return {
            "total_mb": round(total_bytes / (1024 ** 2), 1),
            "file_count": file_count
        }

    def clean_junk_files(self):
        """Safely cleans unlocked temporary junk files."""
        user_temp = os.environ.get('TEMP', tempfile.gettempdir())
        win_temp = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')
        
        targets = [user_temp]
        if os.path.exists(win_temp):
            targets.append(win_temp)
            
        cleaned_bytes = 0
        deleted_count = 0
        
        for folder in targets:
            try:
                for root, dirs, files in os.walk(folder, topdown=False):
                    for f in files:
                        try:
                            fp = os.path.join(root, f)
                            sz = os.path.getsize(fp)
                            os.remove(fp)
                            cleaned_bytes += sz
                            deleted_count += 1
                        except Exception:
                            pass
                    for d in dirs:
                        try:
                            dp = os.path.join(root, d)
                            os.rmdir(dp)
                        except Exception:
                            pass
            except Exception:
                pass
                
        return {
            "cleaned_mb": round(cleaned_bytes / (1024 ** 2), 1),
            "deleted_count": deleted_count
        }

    def get_temperature(self):
        """Advanced 5-strategy thermal pipeline for accurate CPU core temperatures."""
        # Strategy 1: psutil native sensors
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for key in ['coretemp', 'cpu_thermal', 'acpitz', 'amd_sensors', 'k10temp']:
                    if key in temps and temps[key]:
                        return {"status": "Success", "current": round(temps[key][0].current, 1), "source": "Hardware Sensor"}
        except Exception:
            pass

        # Strategy 2: ACPI HighPrecisionTemperature via Windows Performance Counters
        if os.name == 'nt':
            try:
                cmd = "Get-CimInstance -ClassName Win32_PerfFormattedData_Counters_ThermalZoneInformation -ErrorAction SilentlyContinue | Select-Object -ExpandProperty HighPrecisionTemperature"
                output = subprocess.check_output(["powershell", "-Command", cmd], creationflags=0x08000000, stderr=subprocess.DEVNULL).decode().strip()
                if output and float(output) > 0:
                    celsius = (float(output) / 10.0) - 273.15
                    if 15 < celsius < 110:
                        return {"status": "Success", "current": round(celsius, 1), "source": "ACPI Thermal Zone"}
            except Exception:
                pass

            # Strategy 3: MSAcpi_ThermalZoneTemperature Direct WMI
            try:
                cmd = "Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CurrentTemperature"
                output = subprocess.check_output(["powershell", "-Command", cmd], creationflags=0x08000000, stderr=subprocess.DEVNULL).decode().strip()
                if output:
                    celsius = (float(output) / 10.0) - 273.15
                    if 15 < celsius < 110:
                        return {"status": "Success", "current": round(celsius, 1), "source": "MSAcpi WMI"}
            except Exception:
                pass

            # Strategy 4: LibreHardwareMonitor / OpenHardwareMonitor Hooks
            for ns in ['root/LibreHardwareMonitor', 'root/OpenHardwareMonitor']:
                try:
                    cmd = f"Get-CimInstance -Namespace {ns} -ClassName Sensor -ErrorAction SilentlyContinue | Where-Object {{$_.SensorType -eq 'Temperature' -and $_.Name -like '*CPU*'}} | Select-Object -ExpandProperty Value"
                    output = subprocess.check_output(["powershell", "-Command", cmd], creationflags=0x08000000, stderr=subprocess.DEVNULL).decode().strip()
                    if output:
                        first_val = float(output.splitlines()[0].strip())
                        if 15 < first_val < 110:
                            return {"status": "Success", "current": round(first_val, 1), "source": "Hardware Monitor Driver"}
                except Exception:
                    pass

        return {
            "status": "Unsupported",
            "current": None,
            "source": "N/A",
            "message": "Thermal Sensors Restricted by OEM BIOS"
        }

    def get_battery_hardware_score(self):
        """Extracts factory design capacity, full charge capacity, and cycle count from Windows powercfg."""
        default_return = {
            "score": 90,
            "text": "Good (Estimated 90% Max Capacity)",
            "design": "N/A",
            "full": "N/A",
            "cycle_count": "N/A",
            "chemistry": "Li-Ion",
            "manufacturer": "OEM Factory",
            "wear_percent": 10
        }
        
        if os.name != 'nt':
            return default_return

        try:
            report_path = os.path.join(tempfile.gettempdir(), f"bat_rep_{os.getpid()}.xml")
            subprocess.run(
                f'powercfg /batteryreport /xml /output "{report_path}"',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=0x08000000
            )
            
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                try:
                    os.remove(report_path)
                except Exception:
                    pass

                design_match = re.search(r'<DesignCapacity>(\d+)</DesignCapacity>', content)
                full_match = re.search(r'<FullChargeCapacity>(\d+)</FullChargeCapacity>', content)
                cycle_match = re.search(r'<CycleCount>(\d+)</CycleCount>', content)
                chem_match = re.search(r'<Chemistry>([^<]+)</Chemistry>', content)
                mfg_match = re.search(r'<Manufacturer>([^<]+)</Manufacturer>', content)

                if design_match and full_match:
                    design_cap = int(design_match.group(1))
                    full_cap = int(full_match.group(1))
                    
                    if design_cap > 0:
                        true_health_pct = min(100, round((full_cap / design_cap) * 100))
                        wear_pct = max(0, 100 - true_health_pct)
                        
                        if true_health_pct >= 85:
                            status = "Excellent"
                        elif true_health_pct >= 70:
                            status = "Good (Normal Wear)"
                        elif true_health_pct >= 50:
                            status = "Moderate (Degraded Capacity)"
                        else:
                            status = "Critical (Replacement Recommended)"
                            
                        return {
                            "score": true_health_pct,
                            "text": f"{status} ({true_health_pct}% Health)",
                            "design": f"{design_cap:,} mWh",
                            "full": f"{full_cap:,} mWh",
                            "cycle_count": cycle_match.group(1) if cycle_match and cycle_match.group(1) != "0" else "N/A",
                            "chemistry": chem_match.group(1).strip() if chem_match else "Li-Ion",
                            "manufacturer": mfg_match.group(1).strip() if mfg_match else "OEM Battery",
                            "wear_percent": wear_pct
                        }
        except Exception:
            pass
        return default_return

    def get_battery_health(self):
        battery = psutil.sensors_battery()
        if not battery:
            return {
                "status": "Desktop / No Battery",
                "percent": 100,
                "power_plugged": True,
                "secsleft": -1,
                "time_left_str": "AC Power Mode (Wall Outlet)",
                "wear_health": "N/A (Desktop / AC Only)",
                "design_cap": "N/A",
                "full_cap": "N/A",
                "cycle_count": "N/A",
                "chemistry": "N/A",
                "manufacturer": "N/A",
                "wear_percent": 0,
                "score": 100
            }
        
        hardware_info = self.get_battery_hardware_score()
        
        secs = battery.secsleft
        if battery.power_plugged:
            time_str = "Charging on AC Power"
        elif secs and 0 < secs < 86400 * 2:
            hrs, rem = divmod(secs, 3600)
            mins = rem // 60
            time_str = f"{hrs}h {mins}m Remaining"
        else:
            time_str = "Calculating Battery Drain..."

        return {
            "status": "Connected",
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "secsleft": battery.secsleft,
            "time_left_str": time_str,
            "wear_health": hardware_info["text"],
            "design_cap": hardware_info["design"],
            "full_cap": hardware_info["full"],
            "cycle_count": hardware_info["cycle_count"],
            "chemistry": hardware_info["chemistry"],
            "manufacturer": hardware_info["manufacturer"],
            "wear_percent": hardware_info["wear_percent"],
            "score": hardware_info["score"]
        }

    def set_power_plan(self, plan_name="balanced"):
        """Switches Windows Power Plan (balanced, high_performance, power_saver, ultimate)."""
        if os.name != 'nt':
            return False, "Not supported on non-Windows OS"
            
        plans = {
            "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
            "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
            "power_saver": "a1841308-3541-4fab-bc81-f71556f20b4a",
            "ultimate": "e9a42b02-d5df-448d-aa00-03f14749eb61"
        }
        
        guid = plans.get(plan_name.lower().replace(" ", "_"), plans["balanced"])
        try:
            res = subprocess.run(f"powercfg /setactive {guid}", shell=True, capture_output=True, creationflags=0x08000000)
            if res.returncode == 0:
                return True, f"Active Power Plan switched to {plan_name.title()}"
            else:
                return False, "Power scheme not directly available on this Windows edition."
        except Exception as e:
            return False, str(e)

    def get_network_metrics(self):
        """Collects Ping, Jitter, Packet Loss, Wi-Fi SSID, Signal %, and Real-time Throughput."""
        current_ping = 999
        status = "Offline"
        
        if os.name == 'nt':
            cmd = ["ping", "-n", "1", "8.8.8.8"]
            try:
                output = subprocess.check_output(cmd, creationflags=0x08000000, stderr=subprocess.DEVNULL).decode()
                if "time=" in output:
                    time_part = output.split("time=")[1].split("ms")[0].strip()
                    current_ping = int(time_part)
                    status = "Online"
            except Exception:
                pass

        if status == "Online":
            self.ping_history.append(current_ping)
            if len(self.ping_history) > 8:
                self.ping_history.pop(0)
        else:
            self.ping_history = []

        jitter = 0.0
        if len(self.ping_history) >= 2:
            diffs = [abs(self.ping_history[i] - self.ping_history[i-1]) for i in range(1, len(self.ping_history))]
            jitter = round(sum(diffs) / len(diffs), 1)

        wifi_info = {
            "ssid": "Ethernet / Local Network",
            "signal_pct": 100,
            "adapter": "Ethernet Adapter",
            "radio_type": "Gigabit LAN",
            "rx_rate": "1000 Mbps",
            "tx_rate": "1000 Mbps"
        }
        
        if os.name == 'nt':
            try:
                net_out = subprocess.check_output(
                    'netsh wlan show interfaces', shell=True, creationflags=0x08000000, stderr=subprocess.DEVNULL
                ).decode('utf-8', errors='ignore')
                
                for line in net_out.splitlines():
                    line = line.strip()
                    if line.startswith("SSID") and not line.startswith("BSSID"):
                        wifi_info["ssid"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Signal"):
                        sig = line.split(":", 1)[1].strip().replace("%", "")
                        wifi_info["signal_pct"] = int(sig) if sig.isdigit() else 100
                    elif line.startswith("Description"):
                        wifi_info["adapter"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Radio type"):
                        wifi_info["radio_type"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Receive rate"):
                        wifi_info["rx_rate"] = line.split(":", 1)[1].strip() + " Mbps"
                    elif line.startswith("Transmit rate"):
                        wifi_info["tx_rate"] = line.split(":", 1)[1].strip() + " Mbps"
            except Exception:
                pass

        now = time.time()
        current_net = psutil.net_io_counters()
        dt = max(0.1, now - self.last_net_time)
        down_kb_s = 0.0
        up_kb_s = 0.0
        
        if self.last_net_io and current_net:
            down_bytes = current_net.bytes_recv - self.last_net_io.bytes_recv
            up_bytes = current_net.bytes_sent - self.last_net_io.bytes_sent
            down_kb_s = max(0.0, round((down_bytes / 1024.0) / dt, 1))
            up_kb_s = max(0.0, round((up_bytes / 1024.0) / dt, 1))
            
        self.last_net_io = current_net
        self.last_net_time = now

        return {
            "status": status,
            "ping_ms": current_ping,
            "jitter_ms": jitter,
            "wifi": wifi_info,
            "down_kb_s": down_kb_s,
            "up_kb_s": up_kb_s
        }

    def flush_dns(self):
        if os.name == 'nt':
            try:
                subprocess.run(["ipconfig", "/flushdns"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                return True
            except Exception:
                return False
        return False

    def renew_ip(self):
        if os.name == 'nt':
            try:
                subprocess.run(["ipconfig", "/renew"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
                return True
            except Exception:
                return False
        return False

    def run_cpu_stress_test(self, duration_sec=5):
        """Runs a multi-threaded mathematical benchmark, measuring ops/sec and thermal change."""
        start_temp = self.get_temperature().get("current") or 50.0
        cores = psutil.cpu_count(logical=True) or 4
        
        total_ops = [0] * cores
        stop_event = threading.Event()
        
        def worker(thread_idx):
            cnt = 0
            while not stop_event.is_set():
                _ = math.sqrt(987654321.123) * math.tan(0.456)
                cnt += 1
            total_ops[thread_idx] = cnt

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(cores)]
        t0 = time.perf_counter()
        for t in threads:
            t.start()
            
        time.sleep(duration_sec)
        stop_event.set()
        
        for t in threads:
            t.join()
            
        elapsed = max(0.1, time.perf_counter() - t0)
        peak_temp = self.get_temperature().get("current") or start_temp
        
        combined_ops = sum(total_ops)
        score = int((combined_ops / elapsed) / 1000)
        
        return {
            "score": score,
            "total_ops": combined_ops,
            "duration": round(elapsed, 1),
            "start_temp": start_temp,
            "peak_temp": peak_temp,
            "temp_delta": round(peak_temp - start_temp, 1)
        }

    def get_overall_health_score(self, battery, storage_list, temp, ram, ping, cpu):
        """Computes a balanced 0-100 overall laptop health score and letter grade."""
        bat_score = battery.get("score", 90)
        
        t_val = temp.get("current") if temp.get("status") == "Success" else 55
        if t_val is None:
            t_score = 90
        elif t_val <= 60:
            t_score = 100
        elif t_val <= 75:
            t_score = 85 - (t_val - 60) * 1.5
        elif t_val <= 85:
            t_score = 65 - (t_val - 75) * 2.5
        else:
            t_score = max(10, 40 - (t_val - 85) * 3)

        ram_p = ram.get("percent_used", 50)
        if ram_p <= 60:
            ram_score = 100
        elif ram_p <= 80:
            ram_score = 85 - (ram_p - 60) * 1.0
        else:
            ram_score = max(20, 65 - (ram_p - 80) * 2.5)

        if storage_list:
            avg_used = sum([d["percent_used"] for d in storage_list]) / len(storage_list)
            if avg_used <= 70:
                storage_score = 100
            elif avg_used <= 85:
                storage_score = 85 - (avg_used - 70) * 2.0
            else:
                storage_score = max(20, 55 - (avg_used - 85) * 3.0)
        else:
            storage_score = 90

        if ping.get("status") == "Online":
            p_ms = ping.get("ping_ms", 30)
            jit = ping.get("jitter_ms", 2)
            if p_ms < 50 and jit < 10:
                net_score = 100
            elif p_ms < 100 and jit < 20:
                net_score = 85
            else:
                net_score = 65
        else:
            net_score = 40

        total_score = round(
            (bat_score * 0.25) +
            (t_score * 0.20) +
            (ram_score * 0.20) +
            (storage_score * 0.20) +
            (net_score * 0.15)
        )
        total_score = max(5, min(100, total_score))

        if total_score >= 90:
            grade = "A+"
            rating = "Optimal & Healthy"
            color = "#00E676"
        elif total_score >= 80:
            grade = "A"
            rating = "Very Good Condition"
            color = "#00E5FF"
        elif total_score >= 70:
            grade = "B"
            rating = "Fair (Maintenance Advised)"
            color = "#FFD600"
        elif total_score >= 50:
            grade = "C"
            rating = "Degraded (Attention Required)"
            color = "#FF9100"
        else:
            grade = "F"
            rating = "Critical Risk"
            color = "#FF5252"

        return {
            "score": total_score,
            "grade": grade,
            "rating": rating,
            "color": color,
            "components": {
                "battery": round(bat_score),
                "thermals": round(t_score),
                "ram": round(ram_score),
                "storage": round(storage_score),
                "network": round(net_score)
            }
        }

    def generate_predictive_alerts(self, battery, storage_list, temp, ram, ping, cpu):
        alerts = []
        cfg = load_settings()
        
        # Network Alerts
        if ping.get("status") != "Online":
            alerts.append({
                "type": "warning",
                "title": "🌐 Network Offline",
                "msg": "No active internet link detected. Check Wi-Fi connection or ethernet cable."
            })
        else:
            if ping.get("ping_ms", 0) >= cfg.get("ping_warning_threshold", 120.0):
                alerts.append({
                    "type": "warning",
                    "title": "🐢 Elevated Network Latency",
                    "msg": f"Ping is high ({ping['ping_ms']} ms). Online video calls and multiplayer gaming may experience lag."
                })
            if ping.get("jitter_ms", 0) >= cfg.get("jitter_warning_threshold", 20.0):
                alerts.append({
                    "type": "info",
                    "title": "📡 High Network Jitter",
                    "msg": f"Ping variation is {ping['jitter_ms']} ms. This causes voice stuttering in Discord/Zoom. Move closer to your router."
                })

        # Storage Alerts
        for s in storage_list:
            if s["percent_used"] >= cfg.get("storage_warning_threshold", 85.0):
                alerts.append({
                    "type": "critical",
                    "title": f"⚠️ Storage Pressure ({s['drive']})",
                    "msg": f"Drive is {s['percent_used']}% full! Low free space severely degrades SSD performance and lifespan."
                })

        # RAM Alerts
        if ram.get("percent_used", 0) >= cfg.get("ram_warning_threshold", 80.0):
            top_name = ram["top_apps"][0]["name"] if ram["top_apps"] else "Background apps"
            alerts.append({
                "type": "critical",
                "title": "⚡ High RAM Pressure",
                "msg": f"RAM is at {ram['percent_used']}%. Highest consumer is '{top_name}'. Click 'Turbo RAM Clean' to purge unused memory."
            })

        # Thermal Alerts
        if temp.get("status") == "Success" and temp.get("current"):
            cur_t = temp["current"]
            if cur_t >= cfg.get("temp_critical_threshold", 85.0):
                alerts.append({
                    "type": "critical",
                    "title": "🔥 Critical CPU Thermals",
                    "msg": f"CPU core is at {cur_t}°C! Thermal throttling is actively capping CPU clock speed. Elevate laptop base."
                })
            elif cur_t >= cfg.get("temp_warning_threshold", 75.0):
                alerts.append({
                    "type": "warning",
                    "title": "⚠️ CPU Running Warm",
                    "msg": f"CPU temperature is {cur_t}°C. Consider closing intense background compiler tasks or game tabs."
                })

        # Battery Alerts
        if "percent" in battery:
            if battery["percent"] <= cfg.get("battery_low_threshold", 20.0) and not battery["power_plugged"]:
                alerts.append({
                    "type": "critical",
                    "title": "🔋 Low Battery Warning",
                    "msg": f"Battery is at {battery['percent']}%. Plug in charger immediately to prevent sudden hibernation."
                })
            if battery.get("wear_percent", 0) >= 30:
                alerts.append({
                    "type": "info",
                    "title": "🔋 Battery Wear Detected",
                    "msg": f"Battery capacity is degraded by {battery['wear_percent']}%. Enable 80% charging limit to extend remaining battery life."
                })

        if not alerts:
            alerts.append({
                "type": "success",
                "title": "✅ System Running in Peak Health",
                "msg": "All hardware telemetry points, thermals, storage volumes, and network layers are within optimal operating thresholds."
            })

        return alerts

    def export_text_log(self, battery, storage_list, temp, ram, ping, cpu, health_score, alerts):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"Laptop_Health_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        full_filepath = os.path.join(desktop_path, filename)
        specs = self.get_system_specs()
        
        with open(full_filepath, "w", encoding="utf-8") as file:
            file.write("=" * 65 + "\n")
            file.write("       LAPTOP HEALTH SUITE PRO — DIAGNOSTIC AUDIT LOG\n")
            file.write(f"       Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"       Health Score: {health_score['score']}/100 (Grade: {health_score['grade']} - {health_score['rating']})\n")
            file.write("=" * 65 + "\n\n")
            
            file.write("[1] HARDWARE SPECIFICATIONS & VITALS\n")
            file.write(f"  • Device Hostname: {specs['hostname']}\n")
            file.write(f"  • Operating System: {specs['os_name']} (Build: {specs['os_build']})\n")
            file.write(f"  • Processor: {specs['cpu_name']} ({specs['cpu_cores_physical']}C / {specs['cpu_cores_logical']}T)\n")
            file.write(f"  • Graphics Adapter: {specs['gpu_name']} (Driver: {specs['gpu_driver']})\n")
            file.write(f"  • System Uptime: {specs['uptime']} (Boot: {specs['boot_time']})\n\n")

            file.write("[2] BATTERY & POWER SUBSYSTEM\n")
            file.write(f"  • Charge Level: {battery.get('percent', 'N/A')}%\n")
            file.write(f"  • Power Connection: {'Plugged In (AC)' if battery.get('power_plugged') else 'On Battery'}\n")
            file.write(f"  • Health Index: {battery.get('wear_health', 'N/A')}\n")
            file.write(f"  • Factory Design Capacity: {battery.get('design_cap', 'N/A')}\n")
            file.write(f"  • Current Full Capacity: {battery.get('full_cap', 'N/A')}\n")
            file.write(f"  • Cycle Count: {battery.get('cycle_count', 'N/A')}\n\n")

            file.write("[3] MEMORY & ACTIVE PROCESS FOOTPRINT\n")
            file.write(f"  • Total RAM: {ram.get('total_gb', 'N/A')} GB\n")
            file.write(f"  • Used RAM: {ram.get('used_gb', 'N/A')} GB ({ram.get('percent_used', 'N/A')}%)\n")
            file.write("  • Top Memory Consuming Applications:\n")
            for proc in ram.get("top_apps", []):
                file.write(f"    - {proc['name']} (PID {proc['pid']}): {proc['memory_mb']} MB RAM | {proc['cpu_percent']}% CPU\n")
            file.write("\n")

            file.write("[4] STORAGE PARTITIONS\n")
            for d in storage_list:
                file.write(f"  • Drive {d['drive']} [{d['fstype']}]: {d['used_gb']} GB Used / {d['total_gb']} GB Total ({d['percent_used']}% used)\n")
            file.write("\n")

            file.write("[5] THERMALS & NETWORK RADAR\n")
            t_str = f"{temp['current']}°C ({temp.get('source', '')})" if temp.get("status") == "Success" else temp.get("message", "N/A")
            file.write(f"  • CPU Temperature: {t_str}\n")
            file.write(f"  • Network State: {ping.get('status', 'N/A')} | Ping: {ping.get('ping_ms', 'N/A')} ms | Jitter: {ping.get('jitter_ms', 'N/A')} ms\n")
            file.write(f"  • Wi-Fi Connection: {ping.get('wifi', {}).get('ssid', 'N/A')} (Signal: {ping.get('wifi', {}).get('signal_pct', 100)}%)\n\n")

            file.write("=" * 65 + "\n")
            file.write("📋 DIAGNOSTIC ALERTS & PROACTIVE MAINTENANCE ADVISORY\n")
            file.write("=" * 65 + "\n")
            for a in alerts:
                file.write(f"- [{a['title']}] {a['msg']}\n\n")

        return full_filepath

    def export_html_report(self, battery, storage_list, temp, ram, ping, cpu, health_score, alerts):
        """Generates a modern, responsive dark-mode HTML diagnostic report on the Desktop."""
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"Laptop_Health_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        full_filepath = os.path.join(desktop_path, filename)
        specs = self.get_system_specs()
        
        drive_rows = ""
        for d in storage_list:
            bar_color = "#FF5252" if d['percent_used'] >= 85 else "#00E5FF"
            drive_rows += f"""
            <tr>
                <td><strong>{d['drive']}</strong></td>
                <td>{d['type']}</td>
                <td>{d['used_gb']} GB / {d['total_gb']} GB</td>
                <td>
                    <div style="background:#2A2D34; border-radius:6px; overflow:hidden; height:12px; width:100%;">
                        <div style="background:{bar_color}; width:{d['percent_used']}%; height:100%;"></div>
                    </div>
                    <small>{d['percent_used']}%</small>
                </td>
            </tr>
            """

        proc_rows = ""
        for p in ram.get("top_apps", []):
            proc_rows += f"""
            <tr>
                <td>{p['name']}</td>
                <td><code>{p['pid']}</code></td>
                <td><strong>{p['memory_mb']} MB</strong></td>
                <td>{p['cpu_percent']}%</td>
            </tr>
            """

        alert_html = ""
        for a in alerts:
            border_c = "#00E676" if a['type'] == "success" else ("#FF5252" if a['type'] == "critical" else "#FFD600")
            alert_html += f"""
            <div style="background:#1E222B; border-left:4px solid {border_c}; padding:12px 16px; margin-bottom:10px; border-radius:0 8px 8px 0;">
                <h4 style="margin:0 0 4px 0; color:#FFFFFF;">{a['title']}</h4>
                <p style="margin:0; color:#A0AEC0; font-size:14px;">{a['msg']}</p>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laptop Health Pro Diagnostic Report</title>
    <style>
        * {{ box-sizing: border-box; margin:0; padding:0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        body {{ background: #0D1117; color: #E6EDF3; padding: 30px 20px; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363D; padding-bottom: 20px; margin-bottom: 25px; }}
        .header-title h1 {{ font-size: 24px; color: #FFFFFF; font-weight: 700; }}
        .header-title p {{ color: #8B949E; font-size: 14px; margin-top: 4px; }}
        .score-pill {{ background: #161B22; border: 2px solid {health_score['color']}; padding: 12px 24px; border-radius: 12px; text-align: center; }}
        .score-val {{ font-size: 28px; font-weight: 800; color: {health_score['color']}; }}
        .score-label {{ font-size: 12px; color: #8B949E; text-transform: uppercase; letter-spacing: 1px; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-bottom: 25px; }}
        .card {{ background: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 18px; }}
        .card h3 {{ font-size: 13px; color: #8B949E; text-transform: uppercase; margin-bottom: 8px; font-weight: 600; }}
        .card .metric {{ font-size: 22px; font-weight: 700; color: #FFFFFF; }}
        .card .sub {{ font-size: 12px; color: #7EE787; margin-top: 4px; }}
        
        .section {{ background: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 20px; margin-bottom: 25px; }}
        .section h2 {{ font-size: 18px; margin-bottom: 15px; color: #58A6FF; border-bottom: 1px solid #21262D; padding-bottom: 8px; }}
        
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px 12px; text-align: left; font-size: 14px; }}
        th {{ color: #8B949E; font-weight: 600; border-bottom: 1px solid #30363D; }}
        td {{ border-bottom: 1px solid #21262D; color: #C9D1D9; }}
        code {{ background: #21262D; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 12px; }}
        
        .footer {{ text-align: center; color: #8B949E; font-size: 12px; margin-top: 40px; padding-top: 15px; border-top: 1px solid #21262D; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-title">
                <h1>⚡ Laptop Health Suite Pro — Diagnostic Report</h1>
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')} | Host: <strong>{specs['hostname']}</strong></p>
            </div>
            <div class="score-pill">
                <div class="score-val">{health_score['score']} / 100</div>
                <div class="score-label">Grade: {health_score['grade']} ({health_score['rating']})</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Processor (CPU)</h3>
                <div class="metric">{cpu.get('overall_percent', 0)}% Load</div>
                <div class="sub">{specs['cpu_name']}</div>
            </div>
            <div class="card">
                <h3>Memory (RAM)</h3>
                <div class="metric">{ram.get('used_gb', 0)} / {ram.get('total_gb', 0)} GB</div>
                <div class="sub">{ram.get('percent_used', 0)}% Allocated</div>
            </div>
            <div class="card">
                <h3>Battery Vitals</h3>
                <div class="metric">{battery.get('percent', 100)}%</div>
                <div class="sub">{battery.get('wear_health', 'Optimal')}</div>
            </div>
            <div class="card">
                <h3>Thermals & Network</h3>
                <div class="metric">{temp.get('current', 'N/A')}°C</div>
                <div class="sub">Ping: {ping.get('ping_ms', 'N/A')} ms | Jitter: {ping.get('jitter_ms', 0)} ms</div>
            </div>
        </div>

        <div class="section">
            <h2>💻 System Specifications</h2>
            <table>
                <tr><td width="30%"><strong>Operating System</strong></td><td>{specs['os_name']} (Build {specs['os_build']})</td></tr>
                <tr><td><strong>Processor Details</strong></td><td>{specs['cpu_name']} ({specs['cpu_cores_physical']} Cores / {specs['cpu_cores_logical']} Threads)</td></tr>
                <tr><td><strong>Graphics Adapter</strong></td><td>{specs['gpu_name']} (Driver: {specs['gpu_driver']})</td></tr>
                <tr><td><strong>Primary Storage Device</strong></td><td>{specs['disk_model']} ({specs['disk_type']})</td></tr>
                <tr><td><strong>System Uptime</strong></td><td>{specs['uptime']} (Last Boot: {specs['boot_time']})</td></tr>
            </table>
        </div>

        <div class="section">
            <h2>🗄️ Storage Volumes & Partition Health</h2>
            <table>
                <thead>
                    <tr><th>Drive</th><th>Type</th><th>Space Allocation</th><th>Usage Bar</th></tr>
                </thead>
                <tbody>
                    {drive_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>🧠 Top Memory & Process Consumers</h2>
            <table>
                <thead>
                    <tr><th>Application Name</th><th>PID</th><th>Memory Footprint</th><th>CPU Usage</th></tr>
                </thead>
                <tbody>
                    {proc_rows}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2>📋 Diagnostic Alerts & Proactive Recommendations</h2>
            {alert_html}
        </div>

        <div class="footer">
            Laptop Health Suite Pro — Native Windows Telemetry Engine & System Optimizer
        </div>
    </div>
</body>
</html>"""

        with open(full_filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        return full_filepath
