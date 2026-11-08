package com.example.myapplication.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.toRoute
import com.example.myapplication.ConfigScreen
import com.example.myapplication.ui.screens.FormularioScreen
import com.example.myapplication.ui.screens.ResumenScreen
import com.example.myapplication.ui.viewmodel.EcoTripViewModel

@Composable
fun EcoTripNavHost(
    viewModel: EcoTripViewModel,
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = FormularioRoute
    ) {
        composable<FormularioRoute> {
            FormularioScreen(
                viewModel = viewModel,
                onAbrirIdentidad = { navController.navigate(ConfigRoute) },
                onNavigateToResumen = {
                    val state = viewModel.uiState.value
                    val diasDuracion = state.diasDuracionTexto.trim().toIntOrNull()

                    if (state.destino.isNotBlank() && diasDuracion != null && diasDuracion > 0) {
                        navController.navigate(
                            ResumenRoute(
                                nombreViajero = state.nombreViajero,
                                transporte = state.transporteSeleccionado.name,
                                soloBajaHuella = state.soloBajaHuella,
                                destino = state.destino.trim(),
                                diasDuracion = diasDuracion,
                                esViajeGrupal = state.esViajeGrupal
                            )
                        )
                    }
                }
            )
        }

        composable<ConfigRoute> {
            ConfigScreen(onVolver = { navController.popBackStack() })
        }

        composable<ResumenRoute> { backStackEntry ->
            val route = backStackEntry.toRoute<ResumenRoute>()
            ResumenScreen(
                route = route,
                onVolver = {
                    navController.navigate(FormularioRoute) {
                        popUpTo<FormularioRoute> {
                            inclusive = false
                        }
                        launchSingleTop = true
                    }
                }
            )
        }
    }
}
