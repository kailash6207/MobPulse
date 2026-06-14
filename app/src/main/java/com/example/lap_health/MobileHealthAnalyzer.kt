package com.example.lap_health

import android.app.ActivityManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.wifi.WifiManager
import android.os.BatteryManager
import android.os.Build
import android.os.Environment
import android.os.PowerManager
import android.os.StatFs
import java.io.File
import java.net.InetAddress

data class BatteryInfo(
    val level: Int,
    val isCharging: Boolean,
    val temperature: Float, // in Celsius
    val health: String
)

data class StorageInfo(
    val totalGb: Double,
    val usedGb: Double,
    val freeGb: Double,
    val percentUsed: Double
)

data class RamInfo(
    val totalGb: Double,
    val availableGb: Double,
    val percentUsed: Double
)

data class LagDiagnostics(
    val thermalStatus: String,
    val isThrottling: Boolean,
    val backgroundProcessCount: Int,
    val recommendation: String
)

data class NetworkInfo(
    val type: String,
    val signalStrength: Int, // 0 to 100
    val pingMs: Long,
    val status: String
)

class MobileHealthAnalyzer(private val context: Context) {

    fun getBatteryInfo(): BatteryInfo {
        val batteryStatus: Intent? = IntentFilter(Intent.ACTION_BATTERY_CHANGED).let { filter ->
            context.registerReceiver(null, filter)
        }

        val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        val batteryPct = (level * 100 / scale.toFloat()).toInt()

        val status = batteryStatus?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: -1
        val isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING ||
                status == BatteryManager.BATTERY_STATUS_FULL

        val temp = (batteryStatus?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, 0) ?: 0) / 10f

        val healthInt = batteryStatus?.getIntExtra(BatteryManager.EXTRA_HEALTH, BatteryManager.BATTERY_HEALTH_UNKNOWN)
        val health = when (healthInt) {
            BatteryManager.BATTERY_HEALTH_GOOD -> "Good"
            BatteryManager.BATTERY_HEALTH_OVERHEAT -> "Overheat"
            BatteryManager.BATTERY_HEALTH_DEAD -> "Dead"
            BatteryManager.BATTERY_HEALTH_OVER_VOLTAGE -> "Over Voltage"
            BatteryManager.BATTERY_HEALTH_UNSPECIFIED_FAILURE -> "Failure"
            BatteryManager.BATTERY_HEALTH_COLD -> "Cold"
            else -> "Unknown"
        }

        return BatteryInfo(batteryPct, isCharging, temp, health)
    }

    fun getStorageInfo(): StorageInfo {
        val path: File = Environment.getDataDirectory()
        val stat = StatFs(path.path)
        val blockSize = stat.blockSizeLong
        val totalBlocks = stat.blockCountLong
        val availableBlocks = stat.availableBlocksLong

        val totalSize = totalBlocks * blockSize
        val availableSize = availableBlocks * blockSize
        val usedSize = totalSize - availableSize

        val gb = 1024.0 * 1024.0 * 1024.0

        return StorageInfo(
            totalGb = Math.round(totalSize / gb * 100.0) / 100.0,
            usedGb = Math.round(usedSize / gb * 100.0) / 100.0,
            freeGb = Math.round(availableSize / gb * 100.0) / 100.0,
            percentUsed = Math.round((usedSize.toDouble() / totalSize * 100.0) * 100.0) / 100.0
        )
    }

    fun getRamInfo(): RamInfo {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val memoryInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memoryInfo)

        val gb = 1024.0 * 1024.0 * 1024.0
        val totalMemory = memoryInfo.totalMem
        val availableMemory = memoryInfo.availMem
        val usedMemory = totalMemory - availableMemory

        return RamInfo(
            totalGb = Math.round(totalMemory / gb * 100.0) / 100.0,
            availableGb = Math.round(availableMemory / gb * 100.0) / 100.0,
            percentUsed = Math.round((usedMemory.toDouble() / totalMemory * 100.0) * 100.0) / 100.0
        )
    }

    fun getLagDiagnostics(): LagDiagnostics {
        val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        
        val thermalStatusInt = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            powerManager.currentThermalStatus
        } else {
            -1 
        }

        val thermalStatus = when (thermalStatusInt) {
            PowerManager.THERMAL_STATUS_NONE -> "None (Cool)"
            PowerManager.THERMAL_STATUS_LIGHT -> "Light (Warm)"
            PowerManager.THERMAL_STATUS_MODERATE -> "Moderate (Throttling)"
            PowerManager.THERMAL_STATUS_SEVERE -> "Severe (Heavy Throttling)"
            PowerManager.THERMAL_STATUS_CRITICAL -> "Critical (Extreme Throttling)"
            PowerManager.THERMAL_STATUS_EMERGENCY -> "Emergency (Shutdown Risk)"
            PowerManager.THERMAL_STATUS_SHUTDOWN -> "Shutdown"
            else -> "Unsupported"
        }

        val isThrottling = thermalStatusInt >= PowerManager.THERMAL_STATUS_MODERATE
        val runningProcesses = activityManager.runningAppProcesses?.size ?: 0

        val recommendation = when {
            isThrottling -> "Overheating: CPU is throttled. Stop heavy tasks."
            runningProcesses > 50 -> "High Load: Too many processes ($runningProcesses)."
            else -> "Stable: Hardware resources are nominal."
        }

        return LagDiagnostics(thermalStatus, isThrottling, runningProcesses, recommendation)
    }

    fun getNetworkInfo(): NetworkInfo {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val wifiManager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        
        val network = connectivityManager.activeNetwork
        val capabilities = connectivityManager.getNetworkCapabilities(network)
        
        var type = "None"
        var signalPercent = 0
        
        if (capabilities != null) {
            when {
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> {
                    type = "Wi-Fi"
                    val rssi = wifiManager.connectionInfo.rssi
                    signalPercent = WifiManager.calculateSignalLevel(rssi, 100)
                }
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> {
                    type = "Cellular"
                    signalPercent = 50 // Simplified for cellular
                }
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> {
                    type = "Ethernet"
                    signalPercent = 100
                }
            }
        }

        // Fast ping check (Non-blocking usually done in ViewModel, but we can do a quick check here)
        val startTime = System.currentTimeMillis()
        val pingMs: Long = try {
            val address = InetAddress.getByName("8.8.8.8")
            if (address.isReachable(1000)) {
                System.currentTimeMillis() - startTime
            } else {
                -1
            }
        } catch (e: Exception) {
            -1
        }

        val status = when {
            type == "None" -> "Offline"
            pingMs > 200 -> "High Latency (Laggy)"
            signalPercent < 30 -> "Weak Signal"
            else -> "Healthy Connection"
        }

        return NetworkInfo(type, signalPercent, pingMs, status)
    }
}