package com.example.myapplication

import android.content.Context
import androidx.compose.ui.test.hasSetTextAction
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performTextInput
import androidx.lifecycle.SavedStateHandle
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.example.myapplication.data.local.EcoTripDataStore
import com.example.myapplication.data.model.TipoTransporte
import com.example.myapplication.ui.viewmodel.EcoTripViewModel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Pruebas de resiliencia (QA).
 *
 * - Rotación: recrea la Activity (igual que girar el dispositivo) y verifica que el formulario conserve los datos.
 * - Muerte de proceso: simula la restauración entregando al ViewModel un SavedStateHandle con los datos
 *   guardados, que es lo que el sistema reconstruye tras matar el proceso.
 */
@RunWith(AndroidJUnit4::class)
class ResilienciaTest {

    @get:Rule
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun rotacion_conservaDestinoYDias() {
        // La app inicia en el Login (Lab 8.1): se ingresa y se abre el formulario de EcoTrip.
        composeRule.onNodeWithText("Ingresar al Dashboard").performClick()
        composeRule.onNodeWithText("Planificar viaje (EcoTrip)").performClick()
        composeRule.onNode(hasText("Destino") and hasSetTextAction()).performTextInput("Quito")
        composeRule.onNode(hasText("Días de duración") and hasSetTextAction()).performTextInput("4")

        composeRule.activityRule.scenario.recreate()

        composeRule.onNodeWithText("Quito").assertExists()
        composeRule.onNodeWithText("4").assertExists()
    }

    @Test
    fun procesoMuerto_viewModelRestauraFormularioDesdeSavedStateHandle() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val estadoRestaurado = SavedStateHandle(
            mapOf(
                EcoTripViewModel.KEY_DESTINO to "Galápagos",
                EcoTripViewModel.KEY_DIAS to "7",
                EcoTripViewModel.KEY_ES_GRUPAL to true,
                EcoTripViewModel.KEY_NOMBRE to "Ángel",
                EcoTripViewModel.KEY_TRANSPORTE to TipoTransporte.BICICLETA.name,
                EcoTripViewModel.KEY_BAJA_HUELLA to true
            )
        )

        val viewModel = EcoTripViewModel(estadoRestaurado, EcoTripDataStore(context))
        val state = viewModel.uiState.value

        assertEquals("Galápagos", state.destino)
        assertEquals("7", state.diasDuracionTexto)
        assertTrue(state.esViajeGrupal)
        assertEquals("Ángel", state.nombreViajero)
        assertEquals(TipoTransporte.BICICLETA, state.transporteSeleccionado)
        assertTrue(state.soloBajaHuella)
    }

    @Test
    fun savedStateHandle_seActualizaConCadaCambioDelFormulario() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val handle = SavedStateHandle()
        val viewModel = EcoTripViewModel(handle, EcoTripDataStore(context))

        viewModel.onDestinoChange("Cuenca")
        viewModel.onDiasChange("3")
        viewModel.onModoGrupalChange(true)

        assertEquals("Cuenca", handle.get<String>(EcoTripViewModel.KEY_DESTINO))
        assertEquals("3", handle.get<String>(EcoTripViewModel.KEY_DIAS))
        assertEquals(true, handle.get<Boolean>(EcoTripViewModel.KEY_ES_GRUPAL))
    }

    @Test
    fun validacion_diasInvalidosGeneranError() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val viewModel = EcoTripViewModel(SavedStateHandle(), EcoTripDataStore(context))

        viewModel.onDiasChange("abc")
        assertNotNull(viewModel.uiState.value.errorDias)

        viewModel.onDiasChange("0")
        assertNotNull(viewModel.uiState.value.errorDias)

        viewModel.onDiasChange("")
        assertNotNull(viewModel.uiState.value.errorDias)

        viewModel.onDiasChange("5")
        assertNull(viewModel.uiState.value.errorDias)
    }

    @Test
    fun validacion_destinoVacioGeneraError() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val viewModel = EcoTripViewModel(SavedStateHandle(), EcoTripDataStore(context))

        viewModel.onDestinoChange("   ")
        assertNotNull(viewModel.uiState.value.errorDestino)

        viewModel.onDestinoChange("Loja")
        assertNull(viewModel.uiState.value.errorDestino)
        assertFalse(viewModel.uiState.value.destino.isBlank())
    }
}
