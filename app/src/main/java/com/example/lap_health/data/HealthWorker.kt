package com.example.lap_health.data

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.lap_health.MobileHealthAnalyzer

class HealthWorker(appContext: Context, workerParams: WorkerParameters) :
    CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): androidx.work.ListenableWorker.Result {
        val analyzer = MobileHealthAnalyzer(applicationContext)
        val prefs = HealthPrefs(applicationContext)
        
        val batteryInfo = analyzer.getBatteryInfo()
        val now = System.currentTimeMillis()
        
        val entry = HealthEntry(now, batteryInfo.level, batteryInfo.temperature)
        prefs.saveEntry(entry)
        
        return androidx.work.ListenableWorker.Result.success()
    }
}