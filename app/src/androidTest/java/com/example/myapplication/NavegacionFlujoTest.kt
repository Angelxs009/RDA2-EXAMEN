package com.example.myapplication

import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Lab 8.1: verifica el flujo Login → Dashboard → Login y que el Back Stack no conserve pantallas. */
@RunWith(AndroidJUnit4::class)
class NavegacionFlujoTest {

    @get:Rule
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun login_navegaAlDashboard() {
        composeRule.onNodeWithText("Pantalla de Autenticación").assertExists()
        composeRule.onNodeWithText("Ingresar al Dashboard").performClick()
        composeRule.onNodeWithText("¡Bienvenido al Dashboard Principal!").assertExists()
        composeRule.onNodeWithText("Pantalla de Autenticación").assertDoesNotExist()
    }

    @Test
    fun cerrarSesion_regresaAlLogin() {
        composeRule.onNodeWithText("Ingresar al Dashboard").performClick()
        composeRule.onNodeWithText("Cerrar Sesión").performClick()
        composeRule.onNodeWithText("Pantalla de Autenticación").assertExists()
        composeRule.onNodeWithText("¡Bienvenido al Dashboard Principal!").assertDoesNotExist()
    }
}
