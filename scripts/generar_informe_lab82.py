"""Genera docs/informe/Informe_Lab8.2_Navegacion_Argumentos.pdf (HTML -> PDF con Chrome/Edge headless).

Uso: python scripts/generar_informe_lab82.py
Reutiliza estilos y utilidades de generar_informe.py. Capturas en docs/evidencias/ (18 a 22).
"""
import base64
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_informe import CSS, EVID, INTEGRANTES, RAIZ, SALIDA, esc  # noqa: E402

CODIGO = [
    "app/src/main/java/com/example/myapplication/ui/navigation/NavGraph.kt",
    "app/src/main/java/com/example/myapplication/data/model/Asistente.kt",
    "app/src/main/java/com/example/myapplication/ui/screens/AssistantListScreen.kt",
    "app/src/main/java/com/example/myapplication/ui/screens/DetailScreen.kt",
    "app/src/main/java/com/example/myapplication/ui/screens/DashboardScreen.kt",
    "app/src/androidTest/java/com/example/myapplication/ArgumentosNavegacionTest.kt",
]

CSS_EXTRA = """
.fila { display: flex; gap: 10px; justify-content: center; align-items: flex-start; }
.fila img { max-height: 8.5cm; border: 1px solid #999; }
.fila.n3 img { max-width: 31%; }
.fila.n2 img { max-width: 48%; }
pre.dest { font-size: 8.5pt; }
h2, h3 { break-after: avoid; }
"""


def img64(nombre):
    ruta = EVID / nombre
    if not ruta.exists():
        print(f"AVISO: falta {nombre}", file=sys.stderr)
        return ""
    return base64.b64encode(ruta.read_bytes()).decode()


def figura_fila(nombres, pie):
    imgs = ''.join(f'<img src="data:image/png;base64,{img64(n)}">' for n in nombres)
    return (f'<figure><div class="fila n{len(nombres)}">{imgs}</div>'
            f'<figcaption>{esc(pie)}</figcaption></figure>')


def tabla(titulo, numero, cabecera, filas):
    t = [f'<p class="tabla-t">Tabla {numero}</p><p class="tabla-n">{esc(titulo)}</p><table><tr>']
    t += [f'<th>{c}</th>' for c in cabecera]
    t.append('</tr>')
    for f in filas:
        t.append('<tr>' + ''.join(f'<td>{c}</td>' for c in f) + '</tr>')
    t.append('</table>')
    return ''.join(t)


def fragmento(rel, ini, fin):
    """Devuelve las líneas de un archivo entre dos marcadores (inclusive)."""
    lineas = (RAIZ / rel).read_text(encoding="utf-8").splitlines()
    a = next(i for i, l in enumerate(lineas) if ini in l)
    b = next(i for i, l in enumerate(lineas) if i > a and l.rstrip() == fin)
    return "\n".join(lineas[a:b + 1])




NAV = "app/src/main/java/com/example/myapplication/ui/navigation/NavGraph.kt"


def cuerpo():
    p = []
    # Portada
    p.append('<div class="portada">')
    p.append('<p><b>Universidad / Facultad (completar)</b></p><p>Carrera de Ingeniería (completar)</p><br><br>')
    p.append('<p><b>Laboratorio 8.2: Navegación Dinámica con Paso de Argumentos</b></p>')
    p.append('<p><b>Patrón Master-Detail con Navigation Compose y Material 3 en la aplicación EcoTrip 2026</b></p><br>')
    p.append('<p>Desarrollo de Aplicaciones Móviles · RDA-2 · Grupo 4</p><br>')
    for n, _ in INTEGRANTES:
        p.append(f'<p>{esc(n)}</p>')
    p.append('<br><p>Asignatura (completar)</p><p>Docente (completar)</p><p>Octubre de 2026</p>')
    p.append('</div>')

    # Introducción
    p.append('<h1 class="sin-salto">Introducción</h1>')
    p.append("""<p>Casi toda aplicación que muestra datos tiene una pantalla de lista y otra de detalle: el usuario elige un
elemento y espera ver, exactamente, la información de ese elemento. Este patrón se conoce como Master-Detail y obliga a
resolver una pregunta técnica: ¿cómo sabe la pantalla de destino qué mostrar? En Navigation Compose la respuesta es la ruta:
el origen la construye con valores y el destino los recupera del <i>NavBackStackEntry</i> (Android Developers, s. f.-a).</p>
<p>Este laboratorio continúa los anteriores. Sobre el flujo Login → Dashboard del Laboratorio 8.1 se añade una lista de
asistentes que, al pulsar un elemento, navega a un detalle con el identificador y el nombre del asistente. Se resuelve
también el desafío extra, que vuelve opcional el nombre y usa el operador Elvis para un valor por defecto. Las pruebas se
hicieron en un emulador con Android 16 (API 36).</p>""")

    p.append('<h2>Objetivos</h2>')
    p.append("""<p>1. Configurar rutas de navegación dinámicas con parámetros múltiples.</p>
<p>2. Recuperar y procesar argumentos desde el <i>NavBackStackEntry</i>.</p>
<p>3. Mostrar los datos en un componente <i>Card</i> de Material 3 con elevación.</p>
<p>4. Verificar la persistencia de los datos del detalle ante la rotación de pantalla.</p>""")

    # Marco teórico
    p.append('<h1>Marco teórico</h1>')
    p.append("""<p><b>Argumentos en la ruta.</b> Una ruta de Navigation Compose puede declarar marcadores entre llaves, como
<i>detail/{asistenteId}</i>. Los argumentos de ruta (<i>path</i>) son obligatorios; los de consulta
(<i>?nombre={asistenteNombre}</i>) son opcionales y exigen un valor por defecto o aceptar nulos. Cada argumento se declara
con <i>navArgument</i>, indicando su tipo (<i>NavType</i>), si admite nulos y su valor por defecto, y se lee desde
<i>backStackEntry.arguments</i> (Android Developers, s. f.-a).</p>
<p><b>Datos mínimos entre pantallas.</b> La guía oficial recomienda pasar solo la información necesaria para que el destino
la obtenga, normalmente un identificador, y no objetos completos (Android Developers, s. f.-a). Este principio se retoma en
las recomendaciones, pues el laboratorio pasa además el nombre para practicar los parámetros múltiples.</p>
<p><b>Modelo inmutable.</b> Una <i>data class</i> de Kotlin con propiedades <i>val</i> genera de forma automática
<i>equals</i>, <i>hashCode</i>, <i>toString</i> y <i>copy</i>, lo que la hace adecuada para modelar datos que no cambian
(JetBrains, s. f.-a).</p>
<p><b>Nulabilidad y operador Elvis.</b> En Kotlin, un tipo <i>String?</i> admite nulos y el operador <i>?:</i> devuelve el
valor de la derecha si el de la izquierda es nulo, lo que permite declarar un valor por defecto en una sola expresión
(JetBrains, s. f.-b).</p>
<p><b>Card.</b> El componente <i>Card</i> de Material 3 agrupa contenido relacionado en una superficie con forma y
elevación configurables mediante <i>CardDefaults.cardElevation</i> (Android Developers, s. f.-b).</p>""")

    # Desarrollo
    p.append('<h1>Desarrollo</h1>')
    p.append('<h2>Adaptaciones respecto a la guía</h2>')
    p.append("""<p>La guía usa el paquete <i>com.puce.safepass</i> y un proyecto con lista de asistentes previa. El repositorio
del grupo es EcoTrip 2026 (<i>com.example.myapplication</i>) y no contenía esa lista, por lo que se creó junto con el
modelo. El modelo se ubicó en <i>data/model</i>, junto a los demás modelos del proyecto, en lugar de <i>models</i>. El
destino se integró al flujo del Laboratorio 8.1: Login → Dashboard → «Ver asistentes» → Detalle.</p>""")

    p.append('<h2>Paso 1. Modelo de datos</h2>')
    p.append("""<p><i>Asistente</i> es una <i>data class</i> con <i>id</i>, <i>nombre</i> y <i>tipo</i>, todos <i>val</i>. Se
agregó una lista de cinco asistentes de ejemplo. Uno se llama «Ana», para reproducir el caso de la guía; otro incluye
apóstrofo, y otro contiene «&amp;» y «/», caracteres reservados en una URL, para comprobar que los argumentos viajan intactos.</p>""")

    p.append('<h2>Paso 2. Pantalla de detalle</h2>')
    p.append("""<p><i>DetailScreen</i> recibe <i>asistenteId</i> y <i>asistenteNombre</i> como <i>String?</i> y los muestra en
una <i>Card</i> con elevación de 8 dp, con las etiquetas «ID de Asistente» y «Nombre». Además de lo pedido, se añadió una
barra superior con botón de retorno, para que la pantalla no quede aislada y se pueda volver a la lista desde la interfaz.</p>""")

    p.append('<h2>Paso 3. Lista clicable</h2>')
    p.append("""<p><i>AssistantListScreen</i> muestra los asistentes en un <i>LazyColumn</i> con <i>ListItem</i>. Cada elemento
usa <i>Modifier.clickable</i> y llama a la lambda <i>onAsistenteClick(id, nombre)</i>, de modo que la pantalla no conoce el
<i>NavController</i>. Se añadió una clave estable por elemento (<i>key = id</i>) para que la lista se recomponga con
eficiencia.</p>""")

    p.append('<h2>Paso 4. Ruta con argumentos en el NavGraph</h2>')
    p.append("""<p>El archivo <i>NavGraph.kt</i> registra dos destinos nuevos. Los fragmentos clave son los siguientes (el
listado completo está en el Anexo):</p>""")
    p.append('<p class="codigo-t">NavGraph.kt: origen de la navegación (lista)</p><pre class="dest">'
             + esc(fragmento(NAV, '// Destino 4', '        }')) + '</pre>')
    p.append('<p class="codigo-t">NavGraph.kt: destino con argumentos (detalle)</p><pre class="dest">'
             + esc(fragmento(NAV, '// Destino 5', '        }')) + '</pre>')
    p.append("""<p>La guía propone primero la ruta <i>detail/{id}/{nombre}</i> y, en el desafío extra, la versión con nombre
opcional <i>detail/{asistenteId}?nombre={asistenteNombre}</i>. La entrega usa esta segunda forma, que incluye la primera: con
nombre, el comportamiento es idéntico, y sin nombre la ruta sigue siendo válida. El argumento <i>asistenteId</i> es obligatorio
y <i>asistenteNombre</i> es <i>String</i> anulable con valor por defecto <i>null</i>.</p>
<p>Al construir la ruta se aplica <i>Uri.encode</i> a los valores. Sin ese paso, un nombre como «Sofía &amp; Pablo / Equipo
QA» introduciría caracteres con significado propio en una URL (espacio, «/», «&amp;»), que pueden alterar cómo se interpreta la
ruta. Con la codificación, la prueba recupera el texto completo sin alteraciones (ver Resultados).</p>""")

    p.append('<h2>Desafío extra. Nombre opcional y operador Elvis</h2>')
    p.append("""<p>En <i>DetailScreen</i>, el texto del nombre se arma con
<i>asistenteNombre ?: "Usuario Invitado"</i>. Para poder probarlo desde la interfaz, la lista incluye el botón «Abrir detalle
sin nombre», que navega a <i>detail/INVITADO-000</i> sin el argumento de consulta. Es un artefacto de prueba que se retiraría
en una versión final.</p>""")

    # Resultados
    p.append('<h1>Resultados</h1>')
    p.append("""<p>Se compiló sin errores y se ejecutó la aplicación en el emulador Pixel 8 con Android 16 (API 36). La Figura 1
muestra la lista y la tarjeta de detalle para el asistente «Ana», que es la evidencia exigida por el laboratorio.</p>""")
    p.append(figura_fila(
        ["18-lab82-lista-asistentes.png", "19-lab82-detalle-ana.png"],
        "Figura 1. Master-Detail: (izquierda) lista de asistentes; (derecha) tarjeta de detalle tras pulsar «Ana», "
        "con «ID de Asistente: A-001» y «Nombre: Ana»."))
    p.append("""<p>El resultado coincide con el esperado: al pulsar «Ana», la tarjeta muestra «Nombre: Ana». El identificador
también llega, lo que confirma que los dos parámetros de la ruta se recuperan correctamente.</p>""")

    p.append('<h2>Persistencia ante rotación</h2>')
    p.append(figura_fila(
        ["20-lab82-detalle-ana-rotado.png"],
        "Figura 2. El detalle de «Ana» tras girar el emulador a horizontal: los datos permanecen visibles."))
    p.append("""<p>Al girar el emulador, la <i>Activity</i> se recrea, pero los argumentos pertenecen al
<i>NavBackStackEntry</i>, que el <i>NavController</i> restaura, por lo que la tarjeta conserva «Nombre: Ana»
(Figura 2). No fue necesario guardar estado adicional: los argumentos de navegación ya son estado persistente de la pantalla.</p>""")

    p.append('<h2>Casos límite y desafío extra</h2>')
    p.append(figura_fila(
        ["21-lab82-detalle-caracteres-reservados.png", "22-lab82-detalle-sin-nombre-invitado.png"],
        "Figura 3. (Izquierda) nombre con «&» y «/» recuperado intacto; (derecha) ruta sin nombre: se muestra "
        "«Usuario Invitado» por el operador Elvis."))
    p.append("""<p>La Figura 3 resume los dos casos adicionales. A la izquierda, el nombre «Sofía &amp; Pablo / Equipo QA»
llega completo gracias a la codificación. A la derecha, la ruta sin el argumento opcional muestra «Nombre: Usuario Invitado»
y el identificador «INVITADO-000», verificando el valor por defecto.</p>""")

    p.append('<h2>Pruebas automatizadas</h2>')
    p.append("""<p>Se añadió la clase <i>ArgumentosNavegacionTest</i> con cuatro pruebas instrumentadas de Compose (Android
Developers, s. f.-c), que cubren los resultados esperados de la guía y los casos límite de este informe. La ejecución de
<i>connectedDebugAndroidTest</i> en el emulador API 36 terminó con 12 de 12 pruebas aprobadas.</p>""")
    p.append(tabla(
        "Pruebas instrumentadas del Laboratorio 8.2 y su resultado en el emulador (API 36)",
        1,
        ["Prueba", "Qué verifica", "Resultado"],
        [
            ["clicEnAna_muestraTarjetaConNombreAna", "«Nombre: Ana» e ID «A-001» en la tarjeta", "Aprobada"],
            ["nombreConCaracteresReservados_seRecuperaIntacto", "Nombre con «&» y «/» sin alteraciones", "Aprobada"],
            ["rotacion_conservaDatosDelDetalle", "Los datos permanecen tras recrear la Activity", "Aprobada"],
            ["sinNombre_muestraUsuarioInvitado", "Valor por defecto con el operador Elvis", "Aprobada"],
        ]))
    p.append("""<p>El total de 12 pruebas incluye las ocho de laboratorios anteriores (resiliencia, flujo de Login y prueba de
ejemplo), por lo que la incorporación de la lista no rompió el comportamiento previo.</p>""")

    # Análisis
    p.append('<h1>Análisis</h1>')
    p.append("""<p><b>Por qué la ruta es el contrato.</b> La ruta <i>detail/{asistenteId}?nombre={asistenteNombre}</i> describe
qué necesita el destino y qué es opcional. Esto hace el flujo predecible y depurable, como plantea el contexto del
laboratorio: basta con leer la ruta para saber qué recibe la pantalla, sin rastrear variables compartidas.</p>
<p><b>Argumentos de ruta frente a estado compartido.</b> Una alternativa sería guardar el asistente seleccionado en un
<i>ViewModel</i> y leerlo desde el detalle. Funciona, pero acopla ambas pantallas a un estado oculto y complica los enlaces
profundos y las pruebas. El paso por argumentos mantiene cada pantalla autocontenida.</p>
<p><b>Duplicación del dato.</b> Pasar el nombre además del identificador replica información que el destino podría
obtener del repositorio por su ID. Es didáctico para practicar parámetros múltiples, pero si el nombre cambiara
mientras el detalle está abierto, la tarjeta mostraría un valor desactualizado.</p>
<p><b>Alcance de lo verificado.</b> Los datos son una lista fija de ejemplo; no hay repositorio, red ni carga asíncrona. Los
resultados demuestran el paso y la recuperación de argumentos, no el manejo de estados de carga o error de un detalle real.</p>""")

    # Conclusiones
    p.append('<h1>Conclusiones</h1>')
    p.append("""<p>El laboratorio mostró que el paso de argumentos en Navigation Compose es sencillo de implementar y, a la vez,
tiene detalles que se pasan por alto: los argumentos opcionales requieren valor por defecto o nulabilidad, y los valores con
caracteres reservados exigen codificación. Con esas dos precauciones, la ruta <i>detail/{asistenteId}?nombre={…}</i> permitió
mostrar en una <i>Card</i> los datos del asistente elegido, conservarlos al rotar la pantalla y degradar con elegancia
cuando falta el nombre.</p>
<p>En mi opinión, lo más valioso fue el caso del nombre con «&amp;» y «/»: la guía no lo menciona y es justo el tipo de dato
real que rompe una ruta en producción. Probarlo desde el principio evitó un defecto que, con nombres de prueba sencillos como
«Ana», habría pasado inadvertido. También me pareció acertado que la rotación no exigiera código extra, porque confirma que
conviene apoyarse en el estado que el framework ya conserva antes de inventar mecanismos propios.</p>
<p>Por último, el laboratorio sugiere una regla práctica: pasar identificadores en la ruta y obtener los datos desde una única
fuente. Pasar el nombre es válido como ejercicio, pero en una aplicación con datos cambiantes es una duplicación que conviene
evitar.</p>""")

    # Recomendaciones
    p.append('<h1>Recomendaciones</h1>')
    p.append("""<p>1. Pasar solo el identificador en la ruta y recuperar el resto desde un repositorio, para evitar datos
duplicados y desactualizados.</p>
<p>2. Codificar siempre con <i>Uri.encode</i> los valores de texto libre incluidos en la ruta, y probar con nombres que
contengan espacios, «/», «&amp;», «?» y acentos.</p>
<p>3. Migrar a rutas tipadas serializables (como en el flujo de EcoTrip), que convierten los argumentos en propiedades
tipadas y eliminan las cadenas de nombre de argumento.</p>
<p>4. Retirar el botón «Abrir detalle sin nombre» antes de publicar, o moverlo a una variante de depuración.</p>
<p>5. Cuando el detalle dependa de datos remotos, modelar los estados de carga y error con una clase sellada en el
<i>ViewModel</i>.</p>
<p>6. Mantener pruebas de navegación con argumentos en la integración continua para detectar regresiones al cambiar la
ruta.</p>""")

    # Referencias
    p.append('<h1>Referencias</h1>')
    refs = [
        "Android Developers. (s. f.-a). <i>Navigation with Compose</i>. Google. https://developer.android.com/develop/ui/compose/navigation",
        "Android Developers. (s. f.-b). <i>Card</i>. Google. https://developer.android.com/develop/ui/compose/components/card",
        "Android Developers. (s. f.-c). <i>Testing your Compose layout</i>. Google. https://developer.android.com/develop/ui/compose/testing",
        "JetBrains. (s. f.-a). <i>Data classes</i>. Kotlin Documentation. https://kotlinlang.org/docs/data-classes.html",
        "JetBrains. (s. f.-b). <i>Null safety</i>. Kotlin Documentation. https://kotlinlang.org/docs/null-safety.html",
    ]
    for r in refs:
        p.append(f'<p class="ref">{r}</p>')

    # Anexo
    p.append('<h1>Anexo. Código fuente del laboratorio</h1>')
    for rel in CODIGO:
        ruta = RAIZ / rel
        if not ruta.exists():
            print(f"AVISO: no existe {rel}", file=sys.stderr)
            continue
        p.append(f'<p class="codigo-t">{esc(rel)}</p><pre>{esc(ruta.read_text(encoding="utf-8"))}</pre>')
    return "\n".join(p)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    html_path = SALIDA / "informe_lab82.html"
    html_path.write_text(
        f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Laboratorio 8.2 Argumentos de navegación</title>'
        f'<style>{CSS}{CSS_EXTRA}</style></head><body>{cuerpo()}</body></html>', encoding="utf-8")
    pdf = SALIDA / "Informe_Lab8.2_Navegacion_Argumentos.pdf"
    navegadores = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    exe = next((n for n in navegadores if Path(n).exists()), None)
    if not exe:
        sys.exit("No se encontró Chrome ni Edge; abre informe_lab82.html e imprime a PDF.")
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html_path.as_uri()], check=True)
    print(f"PDF generado: {pdf}")


if __name__ == "__main__":
    main()
