"""Genera docs/informe/Informe_Lab8.1_Navegacion_Flujo.pdf (HTML -> PDF con Chrome/Edge headless).

Uso: python scripts/generar_informe_lab81.py
Reutiliza estilos y utilidades de generar_informe.py. Capturas en docs/evidencias/ (13 a 17).
"""
import base64
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_informe import CSS, EVID, INTEGRANTES, RAIZ, SALIDA, esc  # noqa: E402

CODIGO = [
    "app/src/main/java/com/example/myapplication/ui/navigation/NavGraph.kt",
    "app/src/main/java/com/example/myapplication/ui/screens/LoginScreen.kt",
    "app/src/main/java/com/example/myapplication/ui/screens/DashboardScreen.kt",
    "app/src/main/java/com/example/myapplication/MainActivity.kt",
    "app/src/androidTest/java/com/example/myapplication/NavegacionFlujoTest.kt",
]

CSS_EXTRA = """
.fila { display: flex; gap: 10px; justify-content: center; align-items: flex-start; }
.fila img { max-height: 8.5cm; border: 1px solid #999; }
.fila.n3 img { max-width: 31%; }
.fila.n2 img { max-width: 48%; }
pre.dest { font-size: 8.5pt; }
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


def cuerpo():
    p = []
    # Portada
    p.append('<div class="portada">')
    p.append('<p><b>Universidad / Facultad (completar)</b></p><p>Carrera de Ingeniería (completar)</p><br><br>')
    p.append('<p><b>Laboratorio 8.1: Navegación Multitarea y Arquitectura de Flujo (Login a Dashboard)</b></p>')
    p.append('<p><b>Navigation Compose y manejo del Back Stack en la aplicación EcoTrip 2026</b></p><br>')
    p.append('<p>Desarrollo de Aplicaciones Móviles · RDA-2 · Grupo 4</p><br>')
    for n, _ in INTEGRANTES:
        p.append(f'<p>{esc(n)}</p>')
    p.append('<br><p>Asignatura (completar)</p><p>Docente (completar)</p><p>Octubre de 2026</p>')
    p.append('</div>')

    # Introducción
    p.append('<h1 class="sin-salto">Introducción</h1>')
    p.append("""<p>Una aplicación real rara vez es una sola pantalla: el usuario se autentica, llega a un panel principal,
abre detalles y vuelve. Cada una de esas transiciones modifica la pila de retroceso (<i>back stack</i>), la estructura que
decide a dónde lleva el botón «Atrás». Si la pantalla de inicio de sesión permanece en esa pila, una persona que ya ingresó
puede regresar a ella con un solo gesto, lo que en el mejor caso es confuso y en el peor expone un flujo de autenticación que
debería estar cerrado (Android Developers, s. f.-a).</p>
<p>Este laboratorio implementa con Navigation Compose un flujo unidireccional Login → Dashboard sobre la aplicación EcoTrip
2026, controla la pila con <i>popUpTo</i> y verifica con el emulador (Android 16, API 36) que, desde el Dashboard, «Atrás»
cierra la aplicación en lugar de volver al Login. Se resuelve también el desafío extra de cierre de sesión.</p>""")

    p.append('<h2>Objetivos</h2>')
    p.append("""<p>1. Implementar Navigation Compose para estructurar la arquitectura de flujo de la aplicación.</p>
<p>2. Construir un <i>NavHost</i> que gestione varios destinos (autenticación y principal).</p>
<p>3. Manipular el <i>back stack</i> con <i>popUpTo</i> para evitar retornos no deseados.</p>
<p>4. Verificar el comportamiento con evidencia del emulador y con pruebas instrumentadas.</p>""")

    # Marco teórico
    p.append('<h1>Marco teórico</h1>')
    p.append("""<p><b>Componentes de Navigation Compose.</b> El <i>NavController</i> mantiene el <i>back stack</i> y ejecuta las
transiciones; el <i>NavHost</i> asocia cada ruta con un <i>composable</i> y declara el destino inicial
(<i>startDestination</i>); la función <i>composable(ruta)</i> registra un destino (Android Developers, s. f.-b). La ruta es
una cadena en este laboratorio, a diferencia de las rutas tipadas del examen anterior, que usan clases serializables.</p>
<p><b>Back stack y <i>popUpTo</i>.</b> Cada llamada a <i>navigate</i> apila un destino y «Atrás» lo desapila. El
bloque <i>navigate(ruta) { popUpTo(otra) { inclusive = true } }</i> elimina de la pila todos los destinos hasta
<i>otra</i> y, con <i>inclusive = true</i>, también a <i>otra</i>, antes de apilar el nuevo destino (Android Developers,
s. f.-a). Es la forma declarativa de lo que antes se lograba llamando a <i>popBackStack()</i> y luego a <i>navigate()</i>.
Si la pila queda vacía, «Atrás» ya no tiene un destino interno al que volver y la <i>Activity</i> se cierra según las
reglas del sistema (Android Developers, s. f.-c).</p>
<p><b>Estado elevado.</b> Las pantallas reciben lambdas (<i>onLoginSuccess</i>, <i>onLogout</i>) en lugar del
<i>NavController</i>. Así no dependen de la navegación, son más fáciles de probar y de previsualizar, y el único lugar que
conoce las rutas es el grafo.</p>""")

    # Desarrollo
    p.append('<h1>Desarrollo</h1>')
    p.append('<h2>Adaptaciones respecto a la guía</h2>')
    p.append("""<p>La guía parte de «SafePass 2026»; el repositorio del grupo contiene EcoTrip 2026, de modo que se usó el
paquete real <i>com.example.myapplication</i> y el tema <i>MyApplicationTheme</i>. La dependencia
<i>navigation-compose</i> ya estaba declarada (versión 2.8.3 en el catálogo, posterior a la 2.8.0 de la guía), por lo que
el Paso 1 se verificó y no requirió cambios. Además, se conservó el flujo existente de EcoTrip (formulario y resumen) y se
integró como tercer destino, en lugar de eliminarlo.</p>""")

    p.append('<h2>Paso 2. Pantallas</h2>')
    p.append("""<p>Se crearon <i>LoginScreen</i> y <i>DashboardScreen</i> en el paquete <i>ui.screens</i> con los textos exigidos
por la guía. <i>LoginScreen</i> recibe <i>onLoginSuccess</i>; <i>DashboardScreen</i> recibe <i>onLogout</i> (desafío
extra) y <i>onAbrirEcoTrip</i> para llegar al formulario. Ambas usan los estilos de Material 3 del tema, de modo que heredan
Poppins y el color dinámico del laboratorio anterior.</p>""")

    p.append('<h2>Paso 3. Grafo de navegación (NavGraph.kt)</h2>')
    p.append("""<p>El archivo <i>ui/navigation/NavGraph.kt</i> centraliza la navegación. Los fragmentos clave son los que
manipulan la pila:</p>""")
    p.append('<p class="codigo-t">NavGraph.kt: del Login al Dashboard (Paso 3)</p><pre class="dest">'
             + esc(fragmento("app/src/main/java/com/example/myapplication/ui/navigation/NavGraph.kt",
                             'composable("auth")', '        }'))
             + '</pre>')
    p.append('<p class="codigo-t">NavGraph.kt: cierre de sesión (desafío extra)</p><pre class="dest">'
             + esc(fragmento("app/src/main/java/com/example/myapplication/ui/navigation/NavGraph.kt",
                             'composable("main")', '        }'))
             + '</pre>')
    p.append("""<p>En el primer bloque, <i>popUpTo("auth") { inclusive = true }</i> deja la pila con el Dashboard como única
entrada. En el segundo, el cierre de sesión hace la operación inversa: apila <i>auth</i> y elimina <i>main</i>, de modo que
tras salir no se puede volver al panel con «Atrás». El listado completo está en el Anexo.</p>""")

    p.append('<h2>Paso 4. Inyección en MainActivity</h2>')
    p.append("""<p>En <i>setContent</i> se sustituyó la llamada anterior por <i>AppNavigation</i>, dentro de
<i>MyApplicationTheme</i>. El <i>ViewModel</i> de EcoTrip se crea una vez en la <i>Activity</i> y se pasa al grafo,
conservando la resiliencia de estado del examen anterior.</p>""")

    # Resultados
    p.append('<h1>Resultados</h1>')
    p.append("""<p>Se ejecutó la aplicación en el emulador Pixel 8 con Android 16 (API 36). La Figura 1 reproduce
la prueba de fuego del laboratorio.</p>""")
    p.append(figura_fila(
        ["13-lab81-login.png", "14-lab81-dashboard.png", "15-lab81-atras-home.png"],
        "Figura 1. Secuencia de la prueba: (izquierda) pantalla de autenticación al abrir la app; (centro) Dashboard tras "
        "pulsar «Ingresar al Dashboard»; (derecha) pantalla de inicio del sistema tras pulsar «Atrás» en el Dashboard."))
    p.append("""<p>Los tres estados coinciden con los resultados esperados: al abrir, se ve «Pantalla de Autenticación» y su
botón; al pulsarlo, «¡Bienvenido al Dashboard Principal!»; y al presionar «Atrás» el sistema muestra la pantalla de
inicio (<i>Home</i>) sin pasar de vuelta por el Login (Figura 1, derecha).</p>
<p>Para no depender solo de la imagen, se consultó el estado de las tareas con <i>adb shell dumpsys activity
activities</i>. Antes de «Atrás», la actividad en primer plano era <i>com.example.myapplication/.MainActivity</i>;
inmediatamente después, era <i>NexusLauncherActivity</i> y <i>MainActivity</i> ya no figuraba entre los registros de
actividad, es decir, la pila de la aplicación quedó vacía.</p>""")
    p.append(figura_fila(
        ["16-lab81-cerrar-sesion-login.png", "17-lab81-atras-desde-login-home.png"],
        "Figura 2. Desafío extra: (izquierda) tras «Cerrar Sesión» se regresa a la pantalla de autenticación; (derecha) "
        "«Atrás» desde esa pantalla sale de la aplicación, sin reaparecer el Dashboard."))
    p.append("""<p>La Figura 2 comprueba la operación inversa: después de cerrar sesión el Dashboard ya no está en la
pila, por lo que «Atrás» no permite reingresar sin pasar de nuevo por el Login.</p>""")

    p.append('<h2>Pruebas automatizadas</h2>')
    p.append("""<p>Además de la verificación manual se añadió <i>NavegacionFlujoTest</i>, con dos pruebas instrumentadas de
Compose (Android Developers, s. f.-d): una verifica que el Login conduzca al Dashboard y que el Login desaparezca; la otra,
que «Cerrar Sesión» devuelva al Login y que el Dashboard desaparezca. Como la aplicación ahora inicia en el Login, la prueba
de rotación del examen anterior se actualizó para ingresar y abrir el formulario antes de escribir datos. La ejecución de
<i>connectedDebugAndroidTest</i> en el emulador API 36 terminó con 8 de 8 pruebas aprobadas.</p>""")
    p.append(tabla(
        "Resumen de pruebas instrumentadas ejecutadas en el emulador (API 36)",
        1,
        ["Clase", "Pruebas", "Resultado"],
        [
            ["NavegacionFlujoTest (nueva)", "2", "Aprobadas"],
            ["ResilienciaTest (rotación actualizada)", "5", "Aprobadas"],
            ["ExampleInstrumentedTest", "1", "Aprobada"],
        ]))

    # Análisis
    p.append('<h1>Análisis</h1>')
    p.append("""<p><b>Por qué <i>popUpTo</i> y no solo <i>navigate</i>.</b> Sin <i>popUpTo</i>, la pila tras el login sería
[auth, main]; «Atrás» desapilaría <i>main</i> y mostraría <i>auth</i> de nuevo. Con <i>popUpTo("auth") { inclusive = true
}</i> la pila queda [main]. La diferencia se aprecia en un solo gesto, pero cambia la propiedad del flujo: pasa de ser
reversible a unidireccional.</p>
<p><b>Límite de lo que se logró.</b> Este laboratorio simula la autenticación: el botón no valida credenciales y no existe
una sesión real. Quitar el Login de la pila evita volver a él, pero no protege el Dashboard por sí solo; un sistema real
debe, además, validar el estado de sesión en el servidor o en un repositorio y redirigir cuando expire.</p>
<p><b>Observación sobre el estado.</b> El <i>ViewModel</i> de EcoTrip pertenece a la <i>Activity</i>, no al destino
«ecotrip». Por eso los datos del formulario sobreviven a un cierre de sesión dentro de la misma ejecución. En esta
práctica es un efecto aceptable, pero en una aplicación con datos personales los <i>ViewModels</i> de usuario deberían
limpiarse al cerrar sesión.</p>""")

    # Conclusiones
    p.append('<h1>Conclusiones</h1>')
    p.append("""<p>La gestión del <i>back stack</i> es una decisión de diseño, no un detalle técnico: con una sola línea,
<i>popUpTo</i> convirtió un flujo reversible en uno unidireccional, y la prueba con «Atrás» lo demostró con evidencia
visual y con el estado de las tareas del sistema. Navigation Compose concentra esa decisión en un único archivo, lo que hace
el flujo legible y fácil de auditar.</p>
<p>Mi valoración es que el patrón de lambdas hacia las pantallas fue lo más rentable del laboratorio: permitió probar el flujo
sin tocar la interfaz y ampliarlo con el desafío extra cambiando solo el grafo. También fue instructivo que al integrar el
Login como primer destino se rompiera una prueba previa: las pruebas de otros laboratorios dependen del punto de entrada de
la aplicación, y cambiarlo exige actualizarlas.</p>
<p>Finalmente, el laboratorio recuerda que ocultar una pantalla no es lo mismo que proteger un recurso. La navegación
mejora la usabilidad y evita errores del usuario, pero la seguridad real debe apoyarse en la validación de la sesión.</p>""")

    # Recomendaciones
    p.append('<h1>Recomendaciones</h1>')
    p.append("""<p>1. Reemplazar las rutas de cadena por rutas tipadas serializables, como ya se hizo en el flujo de EcoTrip, para
detectar en compilación los errores de nombre.</p>
<p>2. Decidir el destino inicial según el estado de sesión (por ejemplo, leerlo de DataStore) en lugar de iniciar siempre en
el Login.</p>
<p>3. Limpiar los <i>ViewModels</i> con datos de usuario al cerrar sesión, o ligarlos al destino mediante un grafo anidado.</p>
<p>4. Validar credenciales y estado de sesión fuera de la interfaz; el <i>back stack</i> no es un mecanismo de seguridad.</p>
<p>5. Conservar las pruebas de «Atrás» y de cierre de sesión en la integración continua, para detectar regresiones del flujo.</p>
<p>6. Si el flujo crece, extraer cada sección (autenticación, principal, EcoTrip) a su propio grafo anidado con
<i>navigation()</i>, de modo que cada una pueda limpiarse como un bloque.</p>""")

    # Referencias
    p.append('<h1>Referencias</h1>')
    refs = [
        "Android Developers. (s. f.-a). <i>Navigate to a destination</i>. Google. https://developer.android.com/guide/navigation/use-graph/navigate",
        "Android Developers. (s. f.-b). <i>Navigation with Compose</i>. Google. https://developer.android.com/develop/ui/compose/navigation",
        "Android Developers. (s. f.-c). <i>Tasks and the back stack</i>. Google. https://developer.android.com/guide/components/activities/tasks-and-back-stack",
        "Android Developers. (s. f.-d). <i>Testing your Compose layout</i>. Google. https://developer.android.com/develop/ui/compose/testing",
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
    html_path = SALIDA / "informe_lab81.html"
    html_path.write_text(
        f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Laboratorio 8.1 Navegación</title>'
        f'<style>{CSS}{CSS_EXTRA}</style></head><body>{cuerpo()}</body></html>', encoding="utf-8")
    pdf = SALIDA / "Informe_Lab8.1_Navegacion_Flujo.pdf"
    navegadores = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    exe = next((n for n in navegadores if Path(n).exists()), None)
    if not exe:
        sys.exit("No se encontró Chrome ni Edge; abre informe_lab81.html e imprime a PDF.")
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html_path.as_uri()], check=True)
    print(f"PDF generado: {pdf}")


if __name__ == "__main__":
    main()
