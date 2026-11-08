package com.example.myapplication.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.TipoTransporte
import com.example.myapplication.ui.state.FormularioUiState
import com.example.myapplication.ui.viewmodel.EcoTripViewModel

/** Contenedor con estado: conecta el ViewModel con la UI sin estado. */
@Composable
fun FormularioScreen(
    viewModel: EcoTripViewModel,
    onNavigateToResumen: () -> Unit,
    onAbrirIdentidad: (() -> Unit)? = null
) {
    val state by viewModel.uiState.collectAsState()

    FormularioContent(
        state = state,
        onNombreChange = viewModel::onNombreChange,
        onDestinoChange = viewModel::onDestinoChange,
        onDiasChange = viewModel::onDiasChange,
        onTransporteChange = viewModel::onTransporteChange,
        onSoloBajaHuellaChange = viewModel::onSoloBajaHuellaChange,
        onModoGrupalChange = viewModel::onModoGrupalChange,
        onAbrirIdentidad = onAbrirIdentidad,
        onGuardar = {
            // Fuerza la validación de los campos obligatorios aún no tocados.
            viewModel.onDestinoChange(state.destino)
            viewModel.onDiasChange(state.diasDuracionTexto)
            val dias = state.diasDuracionTexto.trim().toIntOrNull()
            if (state.destino.isNotBlank() && dias != null && dias > 0) {
                viewModel.guardarPreferencias()
                onNavigateToResumen()
            }
        }
    )
}

/** UI sin estado: solo recibe el estado inmutable y callbacks. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FormularioContent(
    state: FormularioUiState,
    onNombreChange: (String) -> Unit,
    onDestinoChange: (String) -> Unit,
    onDiasChange: (String) -> Unit,
    onTransporteChange: (TipoTransporte) -> Unit,
    onSoloBajaHuellaChange: (Boolean) -> Unit,
    onModoGrupalChange: (Boolean) -> Unit,
    onGuardar: () -> Unit,
    modifier: Modifier = Modifier,
    onAbrirIdentidad: (() -> Unit)? = null
) {
    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text("EcoTrip 2026") },
                actions = {
                    if (onAbrirIdentidad != null) {
                        IconButton(onClick = onAbrirIdentidad) {
                            Icon(Icons.Filled.Settings, contentDescription = "Identidad visual")
                        }
                    }
                }
            )
        },
        floatingActionButton = {
            FloatingActionButton(onClick = onGuardar) {
                Icon(Icons.Filled.Check, contentDescription = "Guardar y ver resumen")
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            OutlinedTextField(
                value = state.nombreViajero,
                onValueChange = onNombreChange,
                label = { Text("Nombre del viajero") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )

            OutlinedTextField(
                value = state.destino,
                onValueChange = onDestinoChange,
                label = { Text("Destino") },
                isError = state.errorDestino != null,
                supportingText = state.errorDestino?.let { { Text(it) } },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )

            OutlinedTextField(
                value = state.diasDuracionTexto,
                onValueChange = onDiasChange,
                label = { Text("Días de duración") },
                isError = state.errorDias != null,
                supportingText = state.errorDias?.let { { Text(it) } },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )

            Text(
                text = "Medio de transporte ecológico",
                style = MaterialTheme.typography.titleMedium
            )
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                TipoTransporte.entries.forEach { transporte ->
                    FilterChip(
                        selected = state.transporteSeleccionado == transporte,
                        onClick = { onTransporteChange(transporte) },
                        label = { Text(transporte.etiqueta()) }
                    )
                }
            }

            SwitchRow(
                texto = "Modo ecológico (solo opciones de baja huella de carbono)",
                checked = state.soloBajaHuella,
                onCheckedChange = onSoloBajaHuellaChange
            )

            SwitchRow(
                texto = "Viaje grupal",
                checked = state.esViajeGrupal,
                onCheckedChange = onModoGrupalChange
            )
        }
    }
}

@Composable
private fun SwitchRow(
    texto: String,
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = texto,
            style = MaterialTheme.typography.bodyLarge,
            modifier = Modifier
                .weight(1f)
                .padding(end = 16.dp)
        )
        Switch(checked = checked, onCheckedChange = onCheckedChange)
    }
}

private fun TipoTransporte.etiqueta(): String = when (this) {
    TipoTransporte.TREN -> "Tren"
    TipoTransporte.BICICLETA -> "Bicicleta"
    TipoTransporte.VEHICULO_ELECTRICO -> "EV"
}

@Preview(showBackground = true)
@Composable
private fun FormularioContentPreview() {
    FormularioContent(
        state = FormularioUiState(destino = "Quito", diasDuracionTexto = "3"),
        onNombreChange = {},
        onDestinoChange = {},
        onDiasChange = {},
        onTransporteChange = {},
        onSoloBajaHuellaChange = {},
        onModoGrupalChange = {},
        onGuardar = {}
    )
}
