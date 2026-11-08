package com.example.myapplication

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.myapplication.ui.navigation.AppNavigation
import com.example.myapplication.ui.theme.MyApplicationTheme
import com.example.myapplication.ui.viewmodel.EcoTripViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                val ecoTripViewModel: EcoTripViewModel = viewModel(
                    factory = EcoTripViewModel.factory(application)
                )
                AppNavigation(ecoTripViewModel = ecoTripViewModel)
            }
        }
    }
}

/** Pantalla del Laboratorio 7.2: muestra cómo reacciona la interfaz al Color Dinámico y a Poppins. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ConfigScreen(onVolver: (() -> Unit)? = null) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text("EcoTrip 2026 - Identidad", style = MaterialTheme.typography.titleLarge)
                },
                navigationIcon = {
                    if (onVolver != null) {
                        IconButton(onClick = onVolver) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "Volver al formulario"
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = { /* Acción */ },
                containerColor = MaterialTheme.colorScheme.secondaryContainer,
                contentColor = MaterialTheme.colorScheme.onSecondaryContainer
            ) {
                Icon(Icons.Default.Add, contentDescription = "Agregar")
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Bienvenido al futuro de la seguridad móvil.",
                style = MaterialTheme.typography.bodyLarge
            )
            Text(
                text = "Roles de color tomados del fondo de pantalla",
                style = MaterialTheme.typography.titleMedium
            )
            val colores = MaterialTheme.colorScheme
            ColorRole("primary", colores.primary, colores.onPrimary)
            ColorRole("primaryContainer", colores.primaryContainer, colores.onPrimaryContainer)
            ColorRole("secondaryContainer", colores.secondaryContainer, colores.onSecondaryContainer)
            ColorRole("tertiaryContainer", colores.tertiaryContainer, colores.onTertiaryContainer)
            ColorRole("surfaceVariant", colores.surfaceVariant, colores.onSurfaceVariant)
        }
    }
}

@Composable
private fun ColorRole(nombre: String, fondo: Color, contenido: Color) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(56.dp)
            .background(fondo, RoundedCornerShape(16.dp))
            .padding(horizontal = 16.dp),
        contentAlignment = Alignment.CenterStart
    ) {
        Text(text = nombre, color = contenido, style = MaterialTheme.typography.bodyLarge)
    }
}
