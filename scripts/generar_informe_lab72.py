"""Genera docs/informe/Informe_Lab7.2_Identidad_Visual.pdf (HTML -> PDF con Chrome/Edge headless).

Uso: python scripts/generar_informe_lab72.py
Reutiliza estilos y utilidades de generar_informe.py. Capturas en docs/evidencias/ (07 a 12).
"""
import base64
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generar_informe import CSS, EVID, INTEGRANTES, RAIZ, SALIDA, esc, figura  # noqa: E402

CODIGO = [
    "app/src/main/java/com/example/myapplication/MainActivity.kt",
    "app/src/main/java/com/example/myapplication/ui/theme/Theme.kt",
    "app/src/main/java/com/example/myapplication/ui/theme/Type.kt",
    "app/src/main/res/values/font_certs.xml",
    "app/build.gradle.kts",
    "gradle/libs.versions.toml",
]

CSS_EXTRA = """
.par { display: flex; gap: 12px; justify-content: center; align-items: flex-start; }
.par img { max-height: 9cm; max-width: 48%; border: 1px solid #999; }
.nota { font-size: 10.5pt; line-height: 1.3; text-indent: 0; }
"""


def img64(nombre):
    ruta = EVID / nombre
    if not ruta.exists():
        print(f"AVISO: falta {nombre}", file=sys.stderr)
        return ""
    return base64.b64encode(ruta.read_bytes()).decode()


def figura_par(a, b, pie):
    return (f'<figure><div class="par"><img src="data:image/png;base64,{img64(a)}">'
            f'<img src="data:image/png;base64,{img64(b)}"></div>'
            f'<figcaption>{esc(pie)}</figcaption></figure>')


def tabla(titulo, numero, cabecera, filas):
    t = [f'<p class="tabla-t">Tabla {numero}</p><p class="tabla-n">{esc(titulo)}</p><table><tr>']
    t += [f'<th>{c}</th>' for c in cabecera]
    t.append('</tr>')
    for f in filas:
        t.append('<tr>' + ''.join(f'<td>{c}</td>' for c in f) + '</tr>')
    t.append('</table>')
    return ''.join(t)


def cuerpo():
    p = []
    # Portada
    p.append('<div class="portada">')
    p.append('<p><b>Universidad / Facultad (completar)</b></p><p>Carrera de Ingeniería (completar)</p><br><br>')
    p.append('<p><b>Laboratorio 7.2: Identidad Visual con Material You</b></p>')
    p.append('<p><b>Color dinámico, tipografía Poppins y componentes Material Design 3 en la aplicación EcoTrip 2026</b></p><br>')
    p.append('<p>Desarrollo de Aplicaciones Móviles · RDA-2 · Grupo 4</p><br>')
    for n, _ in INTEGRANTES:
        p.append(f'<p>{esc(n)}</p>')
    p.append('<br><p>Asignatura (completar)</p><p>Docente (completar)</p><p>Octubre de 2026</p>')
    p.append('</div>')

    # Introducción
    p.append('<h1 class="sin-salto">Introducción</h1>')
    p.append("""<p>Una aplicación móvil se juzga, antes que por su lógica, por cómo se ve y cómo se lee. Material Design 3,
conocido como Material You, propone que la interfaz no sea un objeto estático sino un sistema que se adapta a la persona:
a partir del fondo de pantalla del usuario, Android 12 (API 31) y posteriores extraen una paleta tonal y la ofrecen a las
aplicaciones como <i>color dinámico</i> (Google, s. f.-a). Este laboratorio aplica esa idea a la aplicación EcoTrip 2026,
construida en el examen práctico anterior, con tres cambios: activar y verificar el esquema de color dinámico, sustituir
la fuente del sistema por Poppins mediante Google Fonts descargables, y estrenar una pantalla con <i>TopAppBar</i> y
<i>FloatingActionButton</i> que reaccionen a los roles de color del sistema.</p>
<p>El informe documenta cada fase, muestra la evidencia en un emulador con Android 16 (API 36) con dos fondos de
pantalla distintos, mide el contraste resultante frente a los umbrales de accesibilidad WCAG y cierra con conclusiones y
recomendaciones.</p>""")

    # Objetivos
    p.append('<h2>Objetivos</h2>')
    p.append("""<p>1. Configurar el esquema de color dinámico (<i>dynamicColorScheme</i>) para que la aplicación se armonice con
el entorno del usuario.</p>
<p>2. Integrar una fuente de Google Fonts en <i>Type.kt</i> sin incluir archivos binarios en el APK.</p>
<p>3. Implementar componentes Material 3 (<i>TopAppBar</i> y <i>FloatingActionButton</i>) que consuman los roles de color
del tema.</p>
<p>4. Explicar cómo el <i>colorScheme</i> influye en la accesibilidad, con mediciones propias.</p>""")

    # Marco teórico
    p.append('<h1>Marco teórico</h1>')
    p.append("""<p><b>Color dinámico.</b> En Jetpack Compose, <i>dynamicLightColorScheme</i> y <i>dynamicDarkColorScheme</i>
devuelven un <i>ColorScheme</i> generado a partir del fondo de pantalla del dispositivo (Android Developers, s. f.-a). El
esquema no es un color suelto: es un conjunto de roles emparejados (<i>primary</i> con <i>onPrimary</i>,
<i>primaryContainer</i> con <i>onPrimaryContainer</i>, etc.) cuyos tonos Material calcula para mantener una relación de
luminosidad predecible entre el fondo y su contenido (Google, s. f.-b). Por eso, si el código elige siempre el par de
roles correcto, el contraste se conserva aunque la paleta cambie por completo.</p>
<p><b>Fuentes descargables.</b> La biblioteca <i>ui-text-google-fonts</i> permite declarar una <i>GoogleFont</i> y un
<i>GoogleFont.Provider</i> apuntando a Google Play Services, que descarga y cachea la tipografía bajo demanda. El
proveedor se autentica con un arreglo de certificados (<i>font_certs.xml</i>), lo que evita empaquetar archivos TTF en la
aplicación (Android Developers, s. f.-b).</p>
<p><b>Accesibilidad del color.</b> Las Pautas de Accesibilidad para el Contenido Web (WCAG) 2.2 exigen una relación de
contraste mínima de 4,5:1 para texto normal y de 3:1 para texto grande y componentes de interfaz (criterios 1.4.3 y 1.4.11,
nivel AA) (World Wide Web Consortium [W3C], 2023). Aunque nacieron para la web, Android las adopta como referencia en sus
guías de accesibilidad (Android Developers, s. f.-c).</p>""")

    # Desarrollo
    p.append('<h1>Desarrollo</h1>')
    p.append('<h2>Adaptaciones respecto a la guía</h2>')
    p.append("""<p>La guía está escrita para el proyecto «SafePass 2026». El repositorio del grupo contiene EcoTrip 2026, por lo
que se aplicaron los mismos pasos con los nombres reales: el paquete es <i>com.example.myapplication</i> y la función de
tema es <i>MyApplicationTheme</i> (en lugar de <i>SafePass2026Theme</i>). El texto de la pantalla de prueba se conservó
tal como lo pide la guía.</p>""")

    p.append('<h2>Fase 1. Dependencias y certificados</h2>')
    p.append("""<p>Se añadió la biblioteca <i>androidx.compose.ui:ui-text-google-fonts:1.7.0</i> al catálogo de versiones
(<i>libs.versions.toml</i>) y se referenció desde <i>app/build.gradle.kts</i>; el proyecto usa el BOM de Compose 2024.09.03,
que alinea esta biblioteca con el resto de módulos de Compose. El proyecto no incluía <i>font_certs.xml</i>, de modo que se
creó <i>app/src/main/res/values/font_certs.xml</i> con los certificados de desarrollo y producción de Google Play
Services, copiados del archivo de pruebas oficial del repositorio de AndroidX (The Android Open Source Project, 2022).</p>""")

    p.append('<h2>Fase 2. Tipografía Poppins</h2>')
    p.append("""<p>En <i>Type.kt</i> se definió el proveedor, la <i>GoogleFont("Poppins")</i> y una <i>FontFamily</i> con los pesos
Normal, Medium, SemiBold y Bold. A diferencia de la guía, que solo sobrescribe <i>titleLarge</i> y <i>bodyLarge</i>, se
aplicó Poppins a toda la jerarquía de <i>Typography</i> copiando los estilos por defecto de Material 3 con
<i>.copy(fontFamily = …)</i>; así, los campos del formulario, las etiquetas y los títulos de EcoTrip también cambian de
fuente y la aplicación no mezcla dos familias. <i>titleLarge</i> (Bold, 22 sp) y <i>bodyLarge</i> (Normal, 16 sp)
conservan exactamente los valores de la guía.</p>""")

    p.append('<h2>Fase 3. Activación del color dinámico</h2>')
    p.append("""<p><i>Theme.kt</i> ya contenía la lógica pedida y se verificó sin modificarla: el parámetro
<i>dynamicColor</i> vale <i>true</i> por defecto y la selección del esquema usa <i>dynamicDarkColorScheme</i> o
<i>dynamicLightColorScheme</i> cuando <i>Build.VERSION.SDK_INT &gt;= Build.VERSION_CODES.S</i>. En dispositivos anteriores
a Android 12 se cae a <i>LightColorScheme</i> o <i>DarkColorScheme</i>, definidos con la paleta estática de <i>Color.kt</i>.
El resultado se transmite a <i>MaterialTheme</i> junto con la nueva tipografía.</p>""")

    p.append('<h2>Fase 4. Pantalla ConfigScreen con TopAppBar</h2>')
    p.append("""<p>Se agregó <i>ConfigScreen</i> en <i>MainActivity.kt</i>. Su <i>TopAppBar</i> usa
<i>primaryContainer</i> como fondo y <i>onPrimaryContainer</i> para el título, según la guía. Además de la frase de
bienvenida, la pantalla muestra cinco bloques que pintan los roles <i>primary</i>, <i>primaryContainer</i>,
<i>secondaryContainer</i>, <i>tertiaryContainer</i> y <i>surfaceVariant</i> con su color de contenido, para que el cambio de
paleta sea visible de un vistazo. Para poder abrirla desde la aplicación se creó la ruta tipada <i>ConfigRoute</i> y se
añadió un ícono de ajustes en la barra del formulario; el parámetro es opcional, por lo que las pruebas de resiliencia
existentes no se ven afectadas.</p>""")

    p.append('<h2>Desafío extra. FloatingActionButton</h2>')
    p.append("""<p>Dentro del <i>Scaffold</i> de <i>ConfigScreen</i> se añadió un <i>FloatingActionButton</i> con
<i>containerColor = secondaryContainer</i>. Se agregó también <i>contentColor = onSecondaryContainer</i>, porque al
cambiar solo el fondo el ícono mantendría el color de contenido del rol anterior y podría perder contraste.</p>""")

    # Resultados
    p.append('<h1>Resultados</h1>')
    p.append("""<p>Las pruebas se hicieron en el emulador Pixel 8 con Android 16 (API 36). Se generaron dos imágenes de fondo
de pantalla, una degradada en naranja y otra en azul, y se aplicaron con la acción «Establecer como fondo» del sistema.
Tras cada cambio se reinició la aplicación para leer el nuevo esquema.</p>""")
    p.append(figura_par("11-lab72-inicio-fondo-naranja.png", "12-lab72-inicio-fondo-azul.png",
                        "Figura 1. Fondos de pantalla de prueba aplicados al emulador: naranja (izquierda) y azul (derecha)."))
    p.append(figura_par("07-lab72-config-fondo-naranja.png", "10-lab72-config-fondo-azul.png",
                        "Figura 2. ConfigScreen con color dinámico: fondo naranja (izquierda) y fondo azul (derecha). Cambian la barra, "
                        "los bloques de color y el botón flotante; la tipografía Poppins se mantiene."))
    p.append("""<p>La Figura 2 confirma el segundo resultado esperado de la guía: el <i>TopAppBar</i>, el
<i>FloatingActionButton</i> y los textos cambian de tono sin tocar una sola línea de código. Con el fondo naranja la
paleta es salmón y ámbar; con el azul, celeste y lavanda. La tipografía, en cambio, no depende del fondo: en ambas
capturas los títulos se ven en Poppins Bold, con terminaciones redondeadas, que es el primer resultado esperado.</p>""")
    p.append(figura_par("08-lab72-formulario-fondo-naranja.png", "09-lab72-formulario-fondo-azul.png",
                        "Figura 3. El formulario de EcoTrip, sin modificar su código de pantalla, adopta el color dinámico y Poppins: "
                        "fondo naranja (izquierda) y fondo azul (derecha)."))
    p.append("""<p>La Figura 3 muestra un beneficio adicional: como el tema es global, todas las pantallas previas de EcoTrip
heredan la identidad visual (campos, <i>chips</i>, interruptores y botón de guardar) sin cambios individuales.</p>""")

    # Accesibilidad
    p.append('<h1>Influencia del colorScheme en la accesibilidad</h1>')
    p.append("""<p>El <i>colorScheme</i> es la capa donde se decide el contraste, y el contraste es la condición más básica de
legibilidad para personas con baja visión, daltonismo o simplemente con la pantalla bajo el sol. El color dinámico
introduce una incertidumbre nueva: el desarrollador ya no conoce de antemano los colores concretos. Material resuelve esto
con roles emparejados cuyos tonos se calculan para garantizar una diferencia de luminosidad mínima (Google, s. f.-b), pero
la garantía solo se cumple si el código respeta los pares. Poner texto <i>onSurface</i> sobre <i>primaryContainer</i>, o un
color fijo como el negro sobre un fondo dinámico, rompe la garantía.</p>
<p>Para comprobarlo se midió el contraste real sobre las capturas de la Figura 2: se tomó el color del fondo de cada bloque
y el píxel de texto más alejado de él, y se aplicó la fórmula de luminancia relativa de WCAG 2.2 (W3C, 2023). Como las
capturas tienen suavizado de bordes, los valores son aproximaciones por defecto del contraste real.</p>""")
    p.append(tabla(
        "Contraste medido (relación de luminancia) entre cada rol y su color de contenido",
        1,
        ["Rol (fondo / contenido)", "Fondo naranja", "Fondo azul", "Mínimo AA (texto normal)", "Resultado"],
        [
            ["primaryContainer / onPrimaryContainer (TopAppBar)", "6,12 : 1", "6,05 : 1", "4,5 : 1", "Cumple"],
            ["primary / onPrimary", "6,02 : 1", "6,06 : 1", "4,5 : 1", "Cumple"],
            ["secondaryContainer / onSecondaryContainer", "6,14 : 1", "6,10 : 1", "4,5 : 1", "Cumple"],
            ["tertiaryContainer / onTertiaryContainer", "6,12 : 1", "6,05 : 1", "4,5 : 1", "Cumple"],
            ["surfaceVariant / onSurfaceVariant", "4,95 : 1", "4,94 : 1", "4,5 : 1", "Cumple"],
        ]))
    p.append("""<p>Los cinco pares superan 4,5:1 con ambos fondos, y los valores son casi idénticos entre una paleta y otra
(alrededor de 6:1), lo que ilustra la regularidad tonal del sistema. El margen más estrecho lo tiene
<i>surfaceVariant</i>, el rol que se usa para texto secundario: por eso conviene no atenuarlo más con transparencia. Estos
resultados se refieren al modo claro; el modo oscuro usa tonos distintos y debe verificarse por separado.</p>
<p>Otros dos aspectos del <i>colorScheme</i> afectan a la accesibilidad. Primero, el significado no debe depender solo del
color: en la aplicación el estado «Activado/Desactivado» del resumen se expresa con texto, no únicamente con un tono.
Segundo, la tipografía también cuenta: Poppins tiene aperturas amplias y buena altura de x, pero su peso Bold en 22 sp para
títulos mantiene la jerarquía sin depender del color, y el cuerpo de 16 sp respeta el tamaño mínimo recomendado.</p>""")

    # Dificultades
    p.append('<h1>Dificultades encontradas</h1>')
    p.append("""<p>Tres situaciones merecen registro. (1) El proyecto no tenía <i>font_certs.xml</i>; sin él, <i>Type.kt</i>
no compila porque <i>R.array.com_google_android_gms_fonts_certs</i> no existe. (2) La propiedad
<i>org.gradle.java.home</i> del repositorio apunta a una ruta del equipo de otro integrante; en este equipo se compiló
sustituyéndola por línea de comandos (JDK 21) sin modificar el archivo compartido. (3) La primera vez que se carga una fuente
descargable el emulador necesita conexión a Internet y Google Play Services; la guía lo menciona como requisito previo y fue
efectivamente necesario.</p>""")

    # Conclusiones
    p.append('<h1>Conclusiones</h1>')
    p.append("""<p>El color dinámico logra que una aplicación se sienta parte del dispositivo con muy poco código: bastó con
verificar una bandera y un bloque <i>when</i> en <i>Theme.kt</i>, y todas las pantallas de EcoTrip cambiaron de paleta a la
vez. Lo que en realidad hace el trabajo es la disciplina de usar los roles del <i>colorScheme</i> en lugar de colores fijos,
y esa disciplina es la que sostiene la accesibilidad: con cinco pares de roles y dos fondos muy distintos, el contraste se
mantuvo entre 4,9:1 y 6,1:1, por encima del mínimo AA.</p>
<p>La tipografía aporta identidad con poco costo, pero introduce una dependencia de red y de Google Play Services. Mi
valoración es que conviene aceptarla en aplicaciones con servicios de Google, y declarar una fuente de respaldo (la
<i>FontFamily</i> por defecto) para dispositivos sin ellos. Además, aplicar Poppins solo a dos estilos, como sugiere la
guía, habría dejado la aplicación con dos familias mezcladas; extenderla a toda la jerarquía fue una decisión que mejoró el
resultado visual.</p>
<p>Por último, el laboratorio muestra que el diseño y la ingeniería no compiten: el mismo cambio que hizo la interfaz más
moderna fue el que habría roto la legibilidad si se hubiera hecho sin respetar los pares de color. Medir el contraste, aun
de forma aproximada, convirtió una afirmación de la teoría en un dato verificable.</p>""")

    # Recomendaciones
    p.append('<h1>Recomendaciones</h1>')
    p.append("""<p>1. Usar siempre pares de roles (<i>x</i> sobre <i>onX</i>) y evitar colores literales dentro de
componentes; reservarlos para la paleta de respaldo.</p>
<p>2. Probar con al menos dos fondos muy distintos (uno claro y saturado, otro oscuro) y en modo claro y oscuro antes de
dar por buena una pantalla.</p>
<p>3. Declarar una fuente de respaldo para dispositivos sin Google Play Services, por ejemplo con
<i>FontFamily(Font(googleFont = …), Font(DeviceFontFamilyName("sans-serif")))</i>.</p>
<p>4. Automatizar la comprobación de contraste con el Escáner de Accesibilidad de Android o con pruebas de interfaz que
inspeccionen el árbol semántico.</p>
<p>5. No fijar <i>dynamicColor = true</i> como única opción: ofrecer un ajuste para desactivarlo permite a una marca con
colores obligatorios (por ejemplo, el verde de EcoTrip) conservar su identidad.</p>
<p>6. Mover el ajuste de color dinámico y el acceso a la pantalla de identidad a una pantalla de configuración definitiva
antes de publicar la aplicación.</p>""")

    # Referencias
    p.append('<h1>Referencias</h1>')
    refs = [
        "Android Developers. (s. f.-a). <i>Material Design 3 in Compose</i>. Google. https://developer.android.com/develop/ui/compose/designsystems/material3",
        "Android Developers. (s. f.-b). <i>Fonts in Compose: Use downloadable fonts</i>. Google. https://developer.android.com/develop/ui/compose/text/fonts",
        "Android Developers. (s. f.-c). <i>Accessibility in Compose</i>. Google. https://developer.android.com/develop/ui/compose/accessibility",
        "Google. (s. f.-a). <i>Dynamic color</i>. Material Design 3. https://m3.material.io/styles/color/dynamic-color/overview",
        "Google. (s. f.-b). <i>Color roles</i>. Material Design 3. https://m3.material.io/styles/color/roles",
        "The Android Open Source Project. (2022). <i>font_certs.xml</i> [Archivo de código]. AndroidX, compose/ui/ui-text-google-fonts. https://github.com/androidx/androidx",
        "World Wide Web Consortium. (2023). <i>Web Content Accessibility Guidelines (WCAG) 2.2</i>. https://www.w3.org/TR/WCAG22/",
    ]
    for r in refs:
        p.append(f'<p class="ref">{r}</p>')

    # Anexo
    p.append('<h1>Anexo. Código modificado</h1>')
    for rel in CODIGO:
        ruta = RAIZ / rel
        if not ruta.exists():
            print(f"AVISO: no existe {rel}", file=sys.stderr)
            continue
        p.append(f'<p class="codigo-t">{esc(rel)}</p><pre>{esc(ruta.read_text(encoding="utf-8"))}</pre>')
    return "\n".join(p)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    html_path = SALIDA / "informe_lab72.html"
    html_path.write_text(
        f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Laboratorio 7.2 Identidad Visual</title>'
        f'<style>{CSS}{CSS_EXTRA}</style></head><body>{cuerpo()}</body></html>', encoding="utf-8")
    pdf = SALIDA / "Informe_Lab7.2_Identidad_Visual.pdf"
    navegadores = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    exe = next((n for n in navegadores if Path(n).exists()), None)
    if not exe:
        sys.exit("No se encontró Chrome ni Edge; abre informe_lab72.html e imprime a PDF.")
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", html_path.as_uri()], check=True)
    print(f"PDF generado: {pdf}")


if __name__ == "__main__":
    main()
