package com.example.myapplication.data.model

// POR QUÉ: data class para aprovechar la inmutabilidad y el método copy().
data class Asistente(
    val id: String,
    val nombre: String,
    val tipo: String
)

/** Datos de ejemplo para la lista Master-Detail (Lab 8.2). */
val asistentesDemo = listOf(
    Asistente(id = "A-001", nombre = "Ana", tipo = "Ponente"),
    Asistente(id = "A-002", nombre = "Luis Fernando Mora", tipo = "Organizador"),
    Asistente(id = "A-003", nombre = "María José O'Neill", tipo = "Asistente"),
    Asistente(id = "A-004", nombre = "Carlos Galarza", tipo = "Voluntario"),
    Asistente(id = "A-005", nombre = "Sofía & Pablo / Equipo QA", tipo = "Patrocinador")
)
