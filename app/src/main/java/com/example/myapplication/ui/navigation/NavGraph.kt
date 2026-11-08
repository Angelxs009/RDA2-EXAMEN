package com.example.myapplication.ui.navigation

import android.app.Application
import android.net.Uri
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.myapplication.navigation.EcoTripNavHost
import com.example.myapplication.ui.screens.AssistantListScreen
import com.example.myapplication.ui.screens.DashboardScreen
import com.example.myapplication.ui.screens.DetailScreen
import com.example.myapplication.ui.screens.LoginScreen
import com.example.myapplication.ui.viewmodel.EcoTripViewModel

@Composable
fun AppNavigation(ecoTripViewModel: EcoTripViewModel) {
    // 1. El NavController es el "conductor" de la aplicación.
    val navController = rememberNavController()

    // 2. El NavHost es el mapa de rutas; startDestination define la primera pantalla.
    NavHost(navController = navController, startDestination = "auth") {

        // Destino 1: Login
        composable("auth") {
            LoginScreen(
                onLoginSuccess = {
                    // POR QUÉ: se navega a 'main' y se elimina 'auth' de la pila, para que el
                    // botón "Atrás" no devuelva al login.
                    navController.navigate("main") {
                        popUpTo("auth") { inclusive = true }
                    }
                }
            )
        }

        // Destino 2: Dashboard
        composable("main") {
            DashboardScreen(
                onLogout = {
                    navController.navigate("auth") {
                        popUpTo("main") { inclusive = true } // Destruye el dashboard
                    }
                },
                onAbrirEcoTrip = { navController.navigate("ecotrip") },
                onAbrirAsistentes = { navController.navigate("list") }
            )
        }

        // Destino 3: flujo EcoTrip (formulario y resumen). "Atrás" regresa al Dashboard.
        composable("ecotrip") {
            // Caso 4: el ViewModel pertenece a esta entrada del back stack, así que se destruye
            // (y se llama onCleared) al salir del flujo EcoTrip, no al rotar la pantalla.
            val application = LocalContext.current.applicationContext as Application
            val flujoViewModel: EcoTripViewModel = viewModel(
                factory = EcoTripViewModel.factory(application)
            )
            EcoTripNavHost(viewModel = flujoViewModel)
        }

        // Destino 4 (Lab 8.2): lista de asistentes (Master).
        composable("list") {
            AssistantListScreen(
                onAsistenteClick = { id, nombre ->
                    // Navegación con argumentos dinámicos. Uri.encode protege los caracteres
                    // reservados (espacios, "/", "&", "?") para que no rompan la ruta.
                    navController.navigate("detail/${Uri.encode(id)}?nombre=${Uri.encode(nombre)}")
                },
                onSinNombreClick = { id ->
                    // Desafío extra: el argumento opcional «nombre» se omite.
                    navController.navigate("detail/${Uri.encode(id)}")
                },
                onVolver = { navController.popBackStack() }
            )
        }

        // Destino 5 (Lab 8.2): detalle (Detail). «asistenteId» es obligatorio y
        // «nombre» es un argumento de consulta opcional.
        composable(
            route = "detail/{asistenteId}?nombre={asistenteNombre}",
            arguments = listOf(
                navArgument("asistenteId") { type = NavType.StringType },
                navArgument("asistenteNombre") {
                    type = NavType.StringType
                    nullable = true
                    defaultValue = null
                }
            )
        ) { backStackEntry ->
            // Recuperamos los argumentos del Bundle de navegación.
            val id = backStackEntry.arguments?.getString("asistenteId")
            val nombre = backStackEntry.arguments?.getString("asistenteNombre")

            DetailScreen(
                asistenteId = id,
                asistenteNombre = nombre,
                onVolver = { navController.popBackStack() }
            )
        }
    }
}
