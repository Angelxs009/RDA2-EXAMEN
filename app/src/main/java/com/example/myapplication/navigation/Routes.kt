package com.example.myapplication.navigation

import kotlinx.serialization.Serializable

@Serializable
object FormularioRoute

@Serializable
object ConfigRoute

@Serializable
data class ResumenRoute(
    val nombreViajero: String,
    val transporte: String,
    val soloBajaHuella: Boolean,
    val destino: String,
    val diasDuracion: Int,
    val esViajeGrupal: Boolean
)