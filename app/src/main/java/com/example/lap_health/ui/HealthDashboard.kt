package com.example.lap_health.ui

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Divider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.lap_health.BatteryInfo
import com.example.lap_health.LagDiagnostics
import com.example.lap_health.MobileHealthAnalyzer
import com.example.lap_health.NetworkInfo
import com.example.lap_health.RamInfo
import com.example.lap_health.StorageInfo
import com.example.lap_health.data.HealthEntry
import com.example.lap_health.data.HealthPrefs
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

@Composable
fun HealthDashboard() {
    val context = LocalContext.current
    val analyzer = remember { MobileHealthAnalyzer(context) }
    val prefs = remember { HealthPrefs(context) }
    
    var batteryInfo by remember { mutableStateOf<BatteryInfo?>(null) }
    var storageInfo by remember { mutableStateOf<StorageInfo?>(null) }
    var ramInfo by remember { mutableStateOf<RamInfo?>(null) }
    var lagInfo by remember { mutableStateOf<LagDiagnostics?>(null) }
    var networkInfo by remember { mutableStateOf<NetworkInfo?>(null) }
    var history by remember { mutableStateOf(prefs.getHistory()) }

    LaunchedEffect(Unit) {
        var lastSaveTime = 0L
        while (true) {
            val b = analyzer.getBatteryInfo()
            batteryInfo = b
            storageInfo = analyzer.getStorageInfo()
            ramInfo = analyzer.getRamInfo()
            lagInfo = analyzer.getLagDiagnostics()
            
            withContext(Dispatchers.IO) {
                val net = analyzer.getNetworkInfo()
                withContext(Dispatchers.Main) {
                    networkInfo = net
                }
                
                // Save to History every 1 minute
                val now = System.currentTimeMillis()
                if (now - lastSaveTime > 60000) {
                    val entry = HealthEntry(now, b.level, b.temperature)
                    prefs.saveEntry(entry)
                    lastSaveTime = now
                    withContext(Dispatchers.Main) {
                        history = prefs.getHistory()
                    }
                }
            }
            delay(5000) 
        }
    }

    Scaffold { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .fillMaxSize()
                .padding(16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Text(
                text = "MOBPULSE HEALTH ANALYZER",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 16.dp)
            )

            // Battery Section
            HealthSection(title = "Battery Status") {
                batteryInfo?.let {
                    MetricRow(label = "Charge Level", value = "${it.level}%")
                    MetricRow(label = "Status", value = if (it.isCharging) "Charging" else "Discharging")
                    MetricRow(label = "Temperature", value = "${it.temperature} C")
                    MetricRow(label = "Health", value = it.health)
                } ?: Text("Loading battery info...")
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Historical Trend Graph (NEW)
            HealthSection(title = "Battery Trend (Last 20m)") {
                if (history.size < 2) {
                    Text("Collecting data points for graph...", fontSize = 12.sp, color = Color.Gray)
                } else {
                    BatteryTrendGraph(history)
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Network Section
            HealthSection(title = "Network Health") {
                networkInfo?.let {
                    MetricRow(label = "Connection", value = it.type)
                    MetricRow(label = "Signal Strength", value = "${it.signalStrength}%")
                    MetricRow(label = "Latency (Ping)", value = if (it.pingMs >= 0) "${it.pingMs} ms" else "Timeout")
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "STATUS: ${it.status}",
                        style = MaterialTheme.typography.labelLarge,
                        fontWeight = FontWeight.Bold,
                        color = when (it.status) {
                            "Healthy Connection" -> Color(0xFF4CAF50)
                            "Offline" -> Color.Red
                            else -> Color(0xFFFF9800)
                        }
                    )
                } ?: Text("Testing network...")
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Storage Section
            HealthSection(title = "Storage Utilization") {
                storageInfo?.let {
                    MetricRow(label = "Total Space", value = "${it.totalGb} GB")
                    MetricRow(label = "Used Space", value = "${it.usedGb} GB (${it.percentUsed}%)")
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = { (it.percentUsed / 100f).toFloat() },
                        modifier = Modifier.fillMaxWidth().height(8.dp),
                        color = if (it.percentUsed > 85) Color.Red else MaterialTheme.colorScheme.primary
                    )
                } ?: Text("Loading storage info...")
            }

            Spacer(modifier = Modifier.height(16.dp))

            // RAM Section
            HealthSection(title = "RAM Usage") {
                ramInfo?.let {
                    MetricRow(label = "Total RAM", value = "${it.totalGb} GB")
                    MetricRow(label = "Used", value = "${it.percentUsed}%")

                    Spacer(modifier = Modifier.height(8.dp))
                    LinearProgressIndicator(
                        progress = { (it.percentUsed / 100f).toFloat() },
                        modifier = Modifier.fillMaxWidth().height(8.dp),
                        color = if (it.percentUsed > 90) Color.Red else MaterialTheme.colorScheme.secondary
                    )
                } ?: Text("Loading RAM info...")
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Lag Diagnostics Section
            HealthSection(title = "Lag Diagnostics") {
                lagInfo?.let {
                    MetricRow(label = "Thermal State", value = it.thermalStatus)
                    MetricRow(label = "CPU Throttling", value = if (it.isThrottling) "YES (Lag active)" else "None")
                    MetricRow(label = "Active Processes", value = "${it.backgroundProcessCount}")
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "DIAGNOSIS:",
                        style = MaterialTheme.typography.labelLarge,
                        fontWeight = FontWeight.Bold,
                        color = if (it.isThrottling) Color.Red else MaterialTheme.colorScheme.tertiary
                    )
                    Text(
                        text = it.recommendation,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                } ?: Text("Loading diagnostics...")
            }

            Spacer(modifier = Modifier.height(24.dp))
            
            // Maintenance Alerts
            Text(
                text = "PREDICTIVE ALERTS",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.error
            )
            Divider(color = MaterialTheme.colorScheme.error, thickness = 2.dp)
            Spacer(modifier = Modifier.height(8.dp))

            val alerts = mutableListOf<String>()
            storageInfo?.let {
                if (it.percentUsed > 85) alerts.add("[!] WARNING: Low storage space (${it.percentUsed}%).")
            }
            batteryInfo?.let {
                if (it.level < 20 && !it.isCharging) alerts.add("[!] BATTERY ALERT: Charge is low (${it.level}%).")
            }
            networkInfo?.let {
                if (it.pingMs > 200) alerts.add("[!] NETWORK ALERT: High latency detected. Games may lag.")
                if (it.type == "None") alerts.add("[!!!] OFFLINE: No internet connection detected.")
            }
            lagInfo?.let {
                if (it.isThrottling) alerts.add("[!!!] THERMAL ALERT: CPU is being throttled due to heat!")
            }

            if (alerts.isEmpty()) {
                Text(text = "[v] All systems nominal.", color = Color.Gray)
            } else {
                alerts.forEach { alert ->
                    Text(text = alert, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.height(4.dp))
                }
            }
        }
    }
}

@Composable
fun BatteryTrendGraph(history: List<HealthEntry>) {
    val data = history.reversed() // Oldest to newest
    val color = MaterialTheme.colorScheme.primary

    Canvas(
        modifier = Modifier
            .fillMaxWidth()
            .height(100.dp)
            .padding(top = 8.dp)
    ) {
        val width = size.width
        val height = size.height
        val spacing = width / (data.size - 1).coerceAtLeast(1)

        val path = Path()
        data.forEachIndexed { index, entry ->
            val x = index * spacing
            val y = height - (entry.batteryLevel / 100f * height)
            if (index == 0) {
                path.moveTo(x, y)
            } else {
                path.lineTo(x, y)
            }
            
            // Draw points
            drawCircle(
                color = color,
                radius = 3.dp.toPx(),
                center = Offset(x, y)
            )
        }

        drawPath(
            path = path,
            color = color,
            style = Stroke(width = 2.dp.toPx())
        )
    }
}

@Composable
fun HealthSection(title: String, content: @Composable () -> Unit) {
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = title.uppercase(),
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.SemiBold,
            color = MaterialTheme.colorScheme.primary
        )
        Divider(modifier = Modifier.padding(vertical = 4.dp))
        content()
    }
}

@Composable
fun MetricRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(text = label, modifier = Modifier.weight(1f), fontSize = 14.sp)
        Text(text = value, fontWeight = FontWeight.Medium, fontSize = 14.sp)
    }
}