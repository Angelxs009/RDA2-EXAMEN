package com.example.myapplication.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ListItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.Asistente
import com.example.myapplication.data.model.asistentesDemo

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AssistantListScreen(
    onAsistenteClick: (id: String, nombre: String) -> Unit,
    onSinNombreClick: (id: String) -> Unit,
    onVolver: () -> Unit,
    asistentes: List<Asistente> = asistentesDemo
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Asistentes") },
                navigationIcon = {
                    IconButton(onClick = onVolver) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Volver al Dashboard"
                        )
                    }
                }
            )
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(asistentes, key = { it.id }) { asistente ->
                    ListItem(
                        headlineContent = { Text(asistente.nombre) },
                        supportingContent = { Text("${asistente.tipo} · ${asistente.id}") },
                        trailingContent = {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                                contentDescription = null
                            )
                        },
                        modifier = Modifier.clickable {
                            // Esta lambda se define en el NavGraph.
                            onAsistenteClick(asistente.id, asistente.nombre)
                        }
                    )
                    HorizontalDivider()
                }
            }
            // Prueba del desafío extra: ruta de detalle sin el argumento opcional «nombre».
            OutlinedButton(
                onClick = { onSinNombreClick("INVITADO-000") },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Text(
                    text = "Abrir detalle sin nombre",
                    style = MaterialTheme.typography.labelLarge
                )
            }
        }
    }
}
