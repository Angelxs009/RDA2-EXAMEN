package com.example.myapplication

import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Lab 8.2: argumentos dinámicos de navegación (Master-Detail). */
@RunWith(AndroidJUnit4::class)
class ArgumentosNavegacionTest {

    @get:Rule
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun abrirListaDeAsistentes() {
        composeRule.onNodeWithText("Ingresar al Dashboard").performClick()
        composeRule.onNodeWithText("Ver asistentes").performClick()
    }

    @Test
    fun clicEnAna_muestraTarjetaConNombreAna() {
        composeRule.onNodeWithText("Ana").performClick()
        composeRule.onNodeWithText("Nombre: Ana").assertExists()
        composeRule.onNodeWithText("ID de Asistente: A-001").assertExists()
    }

    @Test
    fun nombreConCaracteresReservados_seRecuperaIntacto() {
        composeRule.onNodeWithText("Sofía & Pablo / Equipo QA").performClick()
        composeRule.onNodeWithText("Nombre: Sofía & Pablo / Equipo QA").assertExists()
    }

    @Test
    fun rotacion_conservaDatosDelDetalle() {
        composeRule.onNodeWithText("Luis Fernando Mora").performClick()
        composeRule.activityRule.scenario.recreate()
        composeRule.onNodeWithText("Nombre: Luis Fernando Mora").assertExists()
        composeRule.onNodeWithText("ID de Asistente: A-002").assertExists()
    }

    @Test
    fun sinNombre_muestraUsuarioInvitado() {
        composeRule.onNodeWithText("Abrir detalle sin nombre").performClick()
        composeRule.onNodeWithText("Nombre: Usuario Invitado").assertExists()
        composeRule.onNodeWithText("ID de Asistente: INVITADO-000").assertExists()
    }
}
