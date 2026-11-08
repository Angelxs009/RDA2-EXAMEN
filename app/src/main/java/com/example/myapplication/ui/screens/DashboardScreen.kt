package com.example.myapplication.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

@Composable
fun DashboardScreen(
    onLogout: () -> Unit,
    onAbrirEcoTrip: () -> Unit,
    onAbrirAsistentes: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "¡Bienvenido al Dashboard Principal!",
            style = MaterialTheme.typography.titleLarge,
            textAlign = TextAlign.Center
        )
        Spacer(modifier = Modifier.height(24.dp))
        Button(onClick = { onAbrirEcoTrip() }) {
            Text("Planificar viaje (EcoTrip)")
        }
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = { onAbrirAsistentes() }) {
            Text("Ver asistentes")
        }
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedButton(onClick = { onLogout() }) {
            Text("Cerrar Sesión")
        }
    }
}
