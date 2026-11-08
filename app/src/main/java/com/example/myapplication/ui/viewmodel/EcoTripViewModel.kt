package com.example.myapplication.ui.viewmodel

import android.app.Application
import android.util.Log
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.createSavedStateHandle
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.example.myapplication.data.local.EcoTripDataStore
import com.example.myapplication.data.model.PreferenciaViaje
import com.example.myapplication.data.model.TipoTransporte
import com.example.myapplication.ui.state.FormularioUiState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class EcoTripViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val dataStore: EcoTripDataStore
) : ViewModel() {

    companion object {
        const val KEY_DESTINO = "destino"
        const val KEY_DIAS = "dias"
        const val KEY_ES_GRUPAL = "esGrupal"
        const val KEY_NOMBRE = "nombreViajero"
        const val KEY_TRANSPORTE = "transporte"
        const val KEY_BAJA_HUELLA = "soloBajaHuella"

        fun factory(application: Application): ViewModelProvider.Factory = viewModelFactory {
            initializer {
                EcoTripViewModel(
                    savedStateHandle = createSavedStateHandle(),
                    dataStore = EcoTripDataStore(application.applicationContext)
                )
            }
        }
    }

    // Estado inicial restaurado desde SavedStateHandle (sobrevive a process death)
    private val _uiState = MutableStateFlow(
        FormularioUiState(
            destino = savedStateHandle.get<String>(KEY_DESTINO) ?: "",
            diasDuracionTexto = savedStateHandle.get<String>(KEY_DIAS) ?: "",
            esViajeGrupal = savedStateHandle.get<Boolean>(KEY_ES_GRUPAL) ?: false,
            nombreViajero = savedStateHandle.get<String>(KEY_NOMBRE) ?: "",
            transporteSeleccionado = savedStateHandle.get<String>(KEY_TRANSPORTE)
                ?.let { runCatching { TipoTransporte.valueOf(it) }.getOrNull() }
                ?: TipoTransporte.TREN,
            soloBajaHuella = savedStateHandle.get<Boolean>(KEY_BAJA_HUELLA) ?: false
        )
    )
    val uiState: StateFlow<FormularioUiState> = _uiState.asStateFlow()

    init {
        cargarPreferencias()
    }

    fun onDestinoChange(nuevoDestino: String) {
        savedStateHandle[KEY_DESTINO] = nuevoDestino
        _uiState.update {
            it.copy(
                destino = nuevoDestino,
                errorDestino = if (nuevoDestino.isBlank()) "El destino es obligatorio" else null
            )
        }
    }

    fun onDiasChange(nuevosDias: String) {
        val texto = nuevosDias.trim()
        savedStateHandle[KEY_DIAS] = texto
        val dias = texto.toIntOrNull() ?: 0
        val error = when {
            texto.isEmpty() -> "Ingresa los días de duración"
            texto.toIntOrNull() == null -> "Ingresa un número válido"
            dias <= 0 -> "Debe ser mayor a 0"
            else -> null
        }
        _uiState.update { it.copy(diasDuracionTexto = texto, errorDias = error) }
    }

    fun onModoGrupalChange(esGrupal: Boolean) {
        savedStateHandle[KEY_ES_GRUPAL] = esGrupal
        _uiState.update { it.copy(esViajeGrupal = esGrupal) }
    }

    fun onNombreChange(nuevoNombre: String) {
        savedStateHandle[KEY_NOMBRE] = nuevoNombre
        _uiState.update { it.copy(nombreViajero = nuevoNombre) }
    }

    fun onTransporteChange(transporte: TipoTransporte) {
        savedStateHandle[KEY_TRANSPORTE] = transporte.name
        _uiState.update { it.copy(transporteSeleccionado = transporte) }
    }

    fun onSoloBajaHuellaChange(soloBajaHuella: Boolean) {
        savedStateHandle[KEY_BAJA_HUELLA] = soloBajaHuella
        _uiState.update { it.copy(soloBajaHuella = soloBajaHuella) }
    }

    fun guardarPreferencias() {
        val estado = _uiState.value
        viewModelScope.launch {
            dataStore.guardarPreferenciasGlobales(
                PreferenciaViaje(
                    nombreViajero = estado.nombreViajero,
                    transporteSeleccionado = estado.transporteSeleccionado,
                    soloBajaHuella = estado.soloBajaHuella
                )
            )
        }
    }

    /** Caso 4: se invoca justo antes de destruir definitivamente este ViewModel. */
    override fun onCleared() {
        super.onCleared()
        Log.d("EcoTrip_Lifecycle", "Memoria del viaje liberada.")
    }

    /** Sincroniza el estado de UI con lo guardado en DataStore. */
    private fun cargarPreferencias() {
        viewModelScope.launch {
            dataStore.preferenciaViajeFlow.collect { pref ->
                _uiState.update {
                    // Lo que el usuario ya escribió (SavedStateHandle) prevalece sobre el disco.
                    it.copy(
                        nombreViajero = if (savedStateHandle.contains(KEY_NOMBRE)) it.nombreViajero else pref.nombreViajero,
                        transporteSeleccionado = if (savedStateHandle.contains(KEY_TRANSPORTE)) it.transporteSeleccionado else pref.transporteSeleccionado,
                        soloBajaHuella = if (savedStateHandle.contains(KEY_BAJA_HUELLA)) it.soloBajaHuella else pref.soloBajaHuella
                    )
                }
            }
        }
    }
}
