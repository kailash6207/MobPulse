package com.example.lap_health

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.example.lap_health.data.HealthWorker
import com.example.lap_health.ui.HealthDashboard
import com.example.lap_health.ui.theme.Lap_HealthTheme
import java.util.concurrent.TimeUnit

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        setupBackgroundWorker()

        setContent {
            Lap_HealthTheme {
                // A surface container using the 'background' color from the theme
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background,
                ) {
                    HealthDashboard()
                }
            }
        }
    }

    private fun setupBackgroundWorker() {
        val workRequest = PeriodicWorkRequestBuilder<HealthWorker>(15, TimeUnit.MINUTES)
            .build()

        WorkManager.getInstance(applicationContext).enqueueUniquePeriodicWork(
            "HealthTracking",
            ExistingPeriodicWorkPolicy.KEEP,
            workRequest
        )
    }
}