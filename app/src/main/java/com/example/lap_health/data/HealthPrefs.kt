package com.example.lap_health.data

import android.content.Context
import android.content.SharedPreferences
import org.json.JSONArray
import org.json.JSONObject

data class HealthEntry(
    val timestamp: Long,
    val batteryLevel: Int,
    val temperature: Float
)

class HealthPrefs(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("health_history", Context.MODE_PRIVATE)

    fun saveEntry(entry: HealthEntry) {
        val history = getHistory().toMutableList()
        history.add(0, entry) // Add to start
        val limited = history.take(50) // Increased limit for background tracking
        
        val array = JSONArray()
        limited.forEach {
            val obj = JSONObject()
            obj.put("t", it.timestamp)
            obj.put("b", it.batteryLevel)
            obj.put("temp", it.temperature.toDouble())
            array.put(obj)
        }
        prefs.edit().putString("data", array.toString()).apply()
    }

    fun getHistory(): List<HealthEntry> {
        val data = prefs.getString("data", null) ?: return emptyList()
        val history = mutableListOf<HealthEntry>()
        try {
            val array = JSONArray(data)
            for (i in 0 until array.length()) {
                val obj = array.getJSONObject(i)
                history.add(HealthEntry(
                    timestamp = obj.getLong("t"),
                    batteryLevel = obj.getInt("b"),
                    temperature = obj.getDouble("temp").toFloat()
                ))
            }
        } catch (e: Exception) {}
        return history
    }
}