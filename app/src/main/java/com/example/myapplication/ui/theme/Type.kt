package com.example.myapplication.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.googlefonts.Font
import androidx.compose.ui.text.googlefonts.GoogleFont
import androidx.compose.ui.unit.sp
import com.example.myapplication.R

// Proveedor de fuentes: Google Play Services descarga y cachea la fuente bajo demanda.
val provider = GoogleFont.Provider(
    providerAuthority = "com.google.android.gms.fonts",
    providerPackage = "com.google.android.gms",
    certificates = R.array.com_google_android_gms_fonts_certs
)

val fontName = GoogleFont("Poppins")

val poppinsFontFamily = FontFamily(
    Font(googleFont = fontName, fontProvider = provider, weight = FontWeight.Normal),
    Font(googleFont = fontName, fontProvider = provider, weight = FontWeight.Medium),
    Font(googleFont = fontName, fontProvider = provider, weight = FontWeight.SemiBold),
    Font(googleFont = fontName, fontProvider = provider, weight = FontWeight.Bold)
)

private val base = Typography()

// Poppins en toda la jerarquía de Material 3; titleLarge y bodyLarge fijan los valores del laboratorio.
val Typography = Typography(
    displayLarge = base.displayLarge.copy(fontFamily = poppinsFontFamily),
    displayMedium = base.displayMedium.copy(fontFamily = poppinsFontFamily),
    displaySmall = base.displaySmall.copy(fontFamily = poppinsFontFamily),
    headlineLarge = base.headlineLarge.copy(fontFamily = poppinsFontFamily),
    headlineMedium = base.headlineMedium.copy(fontFamily = poppinsFontFamily),
    headlineSmall = base.headlineSmall.copy(fontFamily = poppinsFontFamily),
    titleLarge = TextStyle(
        fontFamily = poppinsFontFamily,
        fontWeight = FontWeight.Bold,
        fontSize = 22.sp
    ),
    titleMedium = base.titleMedium.copy(fontFamily = poppinsFontFamily),
    titleSmall = base.titleSmall.copy(fontFamily = poppinsFontFamily),
    bodyLarge = TextStyle(
        fontFamily = poppinsFontFamily,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp
    ),
    bodyMedium = base.bodyMedium.copy(fontFamily = poppinsFontFamily),
    bodySmall = base.bodySmall.copy(fontFamily = poppinsFontFamily),
    labelLarge = base.labelLarge.copy(fontFamily = poppinsFontFamily),
    labelMedium = base.labelMedium.copy(fontFamily = poppinsFontFamily),
    labelSmall = base.labelSmall.copy(fontFamily = poppinsFontFamily)
)
