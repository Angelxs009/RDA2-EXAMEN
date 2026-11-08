"""Genera docs/informe/Informe_Lab_Gestion_Secretos.pdf (HTML -> PDF con Chrome/Edge headless).

Formato del informe de la asignatura Desarrollo de Software Seguro (PUCE): portada, secciones numeradas,
"Ilustración N", tablas con cabecera oscura y pie "Página X de N". Capturas en docs/evidencias/ (23 a 34).
Uso: python scripts/generar_informe_secretos.py
"""
import base64
import html
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVID = RAIZ / "docs" / "evidencias"
SALIDA = RAIZ / "docs" / "informe"
LAB = "lab-secretos/"
CODIGO = [
    LAB + "vulnerable/app.js", LAB + "seguro/config.js", LAB + "seguro/app.js", LAB + "scripts/setup-db.js",
    LAB + "db/01_esquema_seguro.sql", LAB + ".gitignore", LAB + ".env.development.example", LAB + "tests/pruebas.js",
]
esc = lambda t: html.escape(t, quote=False)

CSS = """
@page { size: A4; margin: 22mm 20mm 22mm 20mm;
  @bottom-right { content: "Página " counter(page) " de " counter(pages); font: 9pt Arial, sans-serif; color: #9a8f86; } }
* { box-sizing: border-box; }
body { font: 12pt/1.6 "Times New Roman", Times, serif; color:#000; margin:0; }
.portada { height: 245mm; text-align:center; display:flex; flex-direction:column; justify-content:center; gap: 30px; break-after:page; }
.portada b { display:block; font-size:12pt; } .portada span { display:block; margin-top:6px; }
.portada .fecha { margin-top: 30px; }
h1 { font-size: 13pt; font-weight:bold; margin: 22px 0 8px; break-after: avoid; }
h2 { font-size: 12pt; font-weight:bold; margin: 18px 0 6px; break-after: avoid; }
p { margin: 8px 0; text-align: justify; }
ul, ol { margin: 6px 0 6px 26px; padding:0; } li { margin: 3px 0; }
table { border-collapse: collapse; width:100%; margin: 12px 0 14px; font-size: 11pt; line-height:1.45; border:1px solid #ddd; }
th { background:#1c1c1c; color:#fff; text-align:left; padding:8px 10px; }
td { padding:8px 10px; vertical-align: top; border-left:1px solid #e4e4e4; border-bottom:1px solid #e4e4e4; }
tr:nth-child(even) td { background:#faf9f7; } tr { break-inside: avoid; }
td:first-child { font-weight: bold; }
.cod { margin: 10px 0 10px 30px; font: 10pt/1.4 Consolas, "Courier New", monospace; white-space: pre-wrap; break-inside: avoid; }
figure { margin: 12px 0 14px; break-inside: avoid; }
figure img { width:100%; display:block; }
figcaption { font: italic 9pt Arial, sans-serif; color:#3b4a5a; margin-top: 4px; }
pre { background:#f6f6f6; border:1px solid #ddd; padding:8px 10px; font: 7.6pt/1.4 Consolas, "Courier New", monospace; white-space: pre-wrap; word-break: break-all; }
.codigo-t { font: bold 9pt Consolas, monospace; margin: 14px 0 3px; break-after: avoid; }
.ref { margin: 4px 0 4px 18px; text-indent: -14px; }
"""

_fig = [0]


def img64(nombre):
    ruta = EVID / nombre
    if not ruta.exists():
        print(f"AVISO: falta {nombre}", file=sys.stderr)
        return ""
    return base64.b64encode(ruta.read_bytes()).decode()


def figura(nombre, pie):
    _fig[0] += 1
    return (f'<figure><img src="data:image/png;base64,{img64(nombre)}">'
            f'<figcaption>Ilustración {_fig[0]} {esc(pie)}</figcaption></figure>')


def tabla(cabecera, filas):
    t = ['<table><tr>'] + [f'<th>{c}</th>' for c in cabecera] + ['</tr>']
    for f in filas:
        t.append('<tr>' + ''.join(f'<td>{c}</td>' for c in f) + '</tr>')
    t.append('</table>')
    return ''.join(t)


def cod(texto):
    return f'<div class="cod">{esc(texto)}</div>'


def cuerpo():
    p = []
    p.append("""<div class="portada">
<div><b>Facultad:</b><span>Hábitat, Infraestructura y Creatividad</span></div>
<div><b>Carrera:</b><span>Ingeniería en Sistemas de Información</span></div>
<div><b>Asignatura:</b><span>Desarrollo de Software Seguro</span></div>
<div><b>Tema:</b><span>Práctica de Laboratorio: Gestión de Secretos y Configuración Segura</span></div>
<div><b>Estudiante:</b><span>Ángel Loor</span></div>
<div><b>Docente:</b><span>Edison Guaña</span></div>
<div class="fecha">Quito, 5 de Noviembre del 2026</div></div>""")

    # 1
    p.append('<h1>1. Introducción</h1>')
    p.append("""<p>El manejo inadecuado de credenciales y secretos dentro del código fuente es uno de los errores más frecuentes
en el desarrollo de software. Muchas veces, por rapidez o descuido, se dejan contraseñas, tokens y llaves de acceso escritas
directamente en el código, sin considerar el riesgo que esto representa. Si además la aplicación se conecta a la base de datos con
una cuenta administrativa, el robo de una sola credencial entrega el sistema completo.</p>
<p>Esta práctica de laboratorio tuvo como objetivo construir una aplicación web funcional, identificar de manera controlada sus
vulnerabilidades de seguridad, corregirlas y documentar cada paso con evidencia. El trabajo se desarrolló en cuatro fases: investigación
y selección de herramientas, implementación con errores intencionales, corrección segura y endurecimiento, y validación con pruebas.</p>
<p>La aplicación desarrollada es un inventario llamado Inventario Lab, una API con interfaz web que lista productos y usuarios y permite
registrar productos mediante un token. Sirvió como escenario para demostrar vulnerabilidades como credenciales expuestas, token en el código,
datos sensibles en las respuestas, endpoints de depuración y un usuario de base de datos con privilegios de administrador.</p>""")

    # 2
    p.append('<h1>2. Fase 1 - Investigación Inicial</h1>')
    p.append('<h2>2.1 Aplicación desarrollada</h2>')
    p.append("""<p>Se desarrolló una API con interfaz web, en dos versiones, con las siguientes funcionalidades:</p>
<ul><li>Consulta de productos del inventario</li><li>Consulta de usuarios (nombre y correo)</li>
<li>Registro de productos protegido con un token de API</li>
<li>Versión insegura con endpoints de depuración (/debug) y de SQL libre (/admin/sql)</li>
<li>Versión segura con verificaciones en vivo de sus propias protecciones</li></ul>""")
    p.append('<h2>2.2 Herramientas y tecnologías seleccionadas</h2>')
    p.append('<p>Para el desarrollo del proyecto se utilizaron las siguientes herramientas:</p>')
    p.append(tabla(['Herramienta', 'Uso en el proyecto'], [
        ['Visual Studio Code', 'Editor de código principal para desarrollar la aplicación'],
        ['Node.js v24.11.1', 'Entorno de ejecución para el servidor backend'],
        ['Express.js', 'Framework web para manejar rutas y archivos estáticos'],
        ['PostgreSQL 18', 'Motor de base de datos relacional para almacenar productos y usuarios'],
        ['node-postgres (pg)', 'Controlador de PostgreSQL con consultas parametrizadas'],
        ['dotenv', 'Carga de variables de entorno desde archivos .env por ambiente'],
        ['Git y GitHub', 'Control de versiones y repositorio remoto del proyecto'],
        ['Terminal y Google Chrome', 'Ejecución de comandos y pruebas de la aplicación en localhost'],
        ['Archivo .env', 'Gestión segura de variables de entorno (Fase 3)'],
    ]))
    p.append("""<p>Como métodos seguros de gestión de secretos se investigaron: variables de entorno (usado en esta práctica), archivos .env
excluidos del repositorio, gestores de secretos dedicados (de un proveedor de nube o HashiCorp Vault) y secretos cifrados del sistema de
integración continua. Los dos últimos son recomendables para producción porque añaden rotación y auditoría.</p>""")
    p.append('<h2>2.3 Estructura del proyecto</h2>')
    p.append('<p>El proyecto se organizó en carpetas separadas para distinguir claramente la versión insegura de la versión corregida:</p>')
    p.append(cod("""lab-secretos/
  vulnerable/   <- Servidor con vulnerabilidades intencionales (app.js, index.html)
  seguro/       <- Versión corregida (app.js, config.js, public/)
  db/           <- Scripts SQL (rol inseguro y esquema con mínimo privilegio)
  scripts/      <- setup-db.js (roles y .env) y scan-secrets.js (escáner)
  tests/        <- pruebas.js (28 pruebas funcionales y de seguridad)
  ui/           <- Estilos compartidos
  .env.*        <- Variables de entorno protegidas (no versionadas)
  .gitignore    <- Exclusión de archivos sensibles"""))
    p.append('<h2>2.4 Diseño de la base de datos</h2>')
    p.append("""<p>Se crearon bases de datos en PostgreSQL con un diseño sencillo y las siguientes tablas:</p>
<ul><li>usuarios: almacena id, nombre, email y password_hash</li>
<li>productos: almacena id, nombre y precio (con restricción de precio mayor o igual a cero)</li></ul>
<p>La versión insegura usa la base lab_vuln con el rol lab_vuln_admin (superusuario). La versión segura usa dos bases separadas,
lab_dev y lab_prod, cada una con un rol dueño para el DDL (lab_owner_*) y un rol de aplicación de mínimo privilegio (lab_app_*).</p>""")

    # 3
    p.append('<h1>3. Fase 2 - Identificación de Vulnerabilidades</h1>')
    p.append("""<p>En esta fase se configuró la aplicación de forma intencionalmente insegura para demostrar los riesgos reales de un
desarrollo sin buenas prácticas. Todas las credenciales son ficticias y la aplicación corre en http://localhost:3001. A continuación
se describe cada vulnerabilidad identificada e implementada.</p>""")
    p.append('<h2>3.1 Resumen de vulnerabilidades encontradas</h2>')
    p.append(tabla(['Vulnerabilidad', 'Ubicación en el código', 'Riesgo'], [
        ['Credenciales hardcodeadas', 'vulnerable/app.js, líneas 9-16', 'Cualquiera con acceso al código ve la contraseña de la base de datos'],
        ['Token de API expuesto', 'vulnerable/app.js, línea 20', 'Token imposible de rotar y visible para todos'],
        ['Usuario superadmin en BD', 'db/00_vulnerable.sql, línea 2', 'La app tiene permisos ilimitados en la base de datos'],
        ['Datos sensibles sin protección', 'vulnerable/app.js, GET /api/usuarios', 'La API devuelve el password_hash de todos los usuarios'],
        ['Endpoint de depuración', 'vulnerable/app.js, GET /debug', 'Revela usuario, base y token sin autenticación'],
        ['SQL libre con stack trace', 'vulnerable/app.js, POST /admin/sql', 'Ejecución arbitraria como superusuario y fuga de detalles internos'],
        ['Secretos en registros', 'vulnerable/app.js, línea 57', 'Token y clave quedan impresos en consola y logs'],
    ]))
    p.append('<h2>3.2 Vulnerabilidad 1 - Credenciales hardcodeadas en el código</h2>')
    p.append("""<p>La primera y más grave vulnerabilidad es que las credenciales de conexión a la base de datos están escritas directamente
en el archivo app.js. Cualquier persona que tenga acceso al repositorio o al código fuente puede ver la contraseña real de la base de datos.</p>""")
    p.append(figura('23-labsecretos-codigo-vulnerable.png', 'Credenciales, token y endpoints inseguros visibles en el código fuente (vulnerable/app.js)'))
    p.append('<h2>3.3 Vulnerabilidad 2 - Token de API expuesto</h2>')
    p.append("""<p>El token que autoriza la escritura también está fijo en el código. Si se filtra el repositorio, un atacante puede crear
registros, y para cambiarlo hay que modificar el código y volver a desplegar.</p>""")
    p.append(cod("const API_TOKEN = 'lab-token-12345-INSEGURO';   // Valor débil, fijo y expuesto"))
    p.append('<h2>3.4 Vulnerabilidad 3 - Datos sensibles sin protección</h2>')
    p.append("""<p>La consulta de usuarios usa SELECT *, por lo que la API devuelve también el hash de la contraseña a cualquier visitante, sin
autenticación. Con el hash, un atacante puede intentar descifrarlo fuera de línea.</p>""")
    p.append(cod("const r = await pool.query('SELECT * FROM usuarios ORDER BY id');   // incluye password_hash"))
    p.append(figura('32-labsecretos-web-vulnerable.png', 'Aplicación insegura en http://localhost:3001: muestra el hash de contraseña y la configuración completa'))
    p.append('<h2>3.5 Vulnerabilidad 4 - Endpoint de depuración y SQL libre</h2>')
    p.append("""<p>La ruta /debug devuelve la configuración de la conexión y el token, y la ruta /admin/sql ejecuta cualquier sentencia SQL que
reciba, devolviendo además el stack trace en los errores. Combinadas con la cuenta de superusuario, permiten controlar toda la base de datos.</p>""")
    p.append(cod("""app.get('/debug', (_req, res) => {
  res.json({ db: pool.options, token: API_TOKEN, env: process.env.NODE_ENV });
});
app.post('/admin/sql', async (req, res) => {
  try { res.json((await pool.query(req.body.sql)).rows); }
  catch (e) { res.status(500).json({ error: e.message, stack: e.stack }); }
});"""))
    p.append(figura('24-labsecretos-explotacion-vulnerable.png', 'Explotación de la versión insegura: /debug, hash expuesto y DDL ejecutado con la cuenta de la aplicación'))
    p.append('<h2>3.6 Vulnerabilidad 5 - Secretos impresos en los registros</h2>')
    p.append("""<p>Al arrancar, el servidor imprime el token y la clave de la base de datos en la consola. Esos mensajes suelen terminar en
archivos de registro, herramientas de monitoreo y capturas de pantalla.</p>""")
    p.append(cod("app.listen(3001, () => console.log('[INSEGURA] ... token=' + API_TOKEN + ' db=lab_vuln_admin:admin123'));"))
    p.append('<h2>3.7 Vulnerabilidad 6 - Usuario con privilegios excesivos en la base de datos</h2>')
    p.append("""<p>La aplicación se conecta con el rol lab_vuln_admin, creado como SUPERUSER. Si alguien explota otra vulnerabilidad y toma control
de la aplicación, tendrá acceso total a la base de datos: podrá crear y eliminar tablas, modificar usuarios y crear nuevos roles.</p>""")
    p.append(cod("CREATE ROLE lab_vuln_admin LOGIN SUPERUSER PASSWORD 'admin123';"))
    p.append(figura('25-labsecretos-escaner-secretos.png', 'Escáner de secretos: 3 hallazgos en la versión insegura y 0 en la segura'))

    # 4
    p.append('<h1>4. Fase 3 - Corrección Segura y Endurecimiento</h1>')
    p.append("""<p>Se corrigió la aplicación en la carpeta seguro/ aplicando variables de entorno, exclusión de secretos con .gitignore,
mínimo privilegio en la base de datos y separación de ambientes. La siguiente tabla relaciona cada vulnerabilidad con su solución.</p>""")
    p.append(tabla(['Vulnerabilidad', 'Solución aplicada', 'Archivo'], [
        ['Credenciales y token hardcodeados', 'Variables de entorno cargadas desde .env.&lt;ambiente&gt;, generadas al azar con crypto.randomBytes', 'seguro/config.js, scripts/setup-db.js'],
        ['Usuario superadmin', 'Rol lab_app_* sin superusuario, createdb ni createrole; SELECT e INSERT solo donde hace falta', 'db/01_esquema_seguro.sql'],
        ['Datos sensibles', 'GRANT SELECT (id, nombre, email) por columna y consulta explícita de columnas', 'db/01_esquema_seguro.sql, seguro/app.js'],
        ['/debug y /admin/sql', 'Endpoints eliminados; errores genéricos al cliente y detalle solo en el registro interno', 'seguro/app.js'],
        ['Secretos en registros', 'El arranque imprime entorno y usuario de BD, nunca contraseñas ni tokens', 'seguro/app.js'],
        ['Secretos en el repositorio', '.gitignore excluye .env y .env.*; solo se versionan plantillas *.example sin valores', '.gitignore'],
        ['Un solo ambiente', 'Development y production con BD, usuario, contraseña, token y puerto distintos', 'scripts/setup-db.js'],
    ]))
    p.append('<h2>4.1 Archivo de variables de entorno y validación</h2>')
    p.append("""<p>El módulo config.js carga .env.development o .env.production según NODE_ENV y valida las siete variables requeridas. Si faltan,
termina con código 1 mostrando solo sus nombres, nunca sus valores; en producción exige además un token de al menos 32 caracteres.
Las contraseñas y el token se generan con el script setup-db.js, por lo que ningún secreto real existe en el código ni en este informe.</p>""")
    p.append(cod("""PORT=3000
DB_HOST=localhost
DB_NAME=lab_dev
DB_USER=lab_app_dev
DB_PASSWORD=<generada-por-setup-db>
API_TOKEN=<generado-por-setup-db>"""))
    p.append('<h2>4.2 Exclusión de secretos con .gitignore</h2>')
    p.append(figura('26-labsecretos-gitignore.png', 'Los archivos .env existen en disco pero Git los ignora; solo se versionan las plantillas'))
    p.append('<h2>4.3 Mínimo privilegio en la base de datos</h2>')
    p.append("""<p>El rol dueño ejecuta el esquema y el rol de aplicación solo recibe SELECT e INSERT sobre productos y SELECT de las columnas id,
nombre y email de usuarios, sin password_hash. Además se revocó el permiso de conexión a PUBLIC en cada base, de modo que cada rol solo
entra a su ambiente.</p>""")
    p.append(figura('27-labsecretos-roles-privilegios.png', 'Roles sin atributos de administrador y permisos por tabla y por columna'))
    p.append('<h2>4.4 Separación de ambientes</h2>')
    p.append(tabla(['Elemento', 'Development', 'Production'], [
        ['Archivo de configuración', '.env.development', '.env.production'],
        ['Base de datos', 'lab_dev', 'lab_prod'],
        ['Rol de aplicación / de migraciones', 'lab_app_dev / lab_owner_dev', 'lab_app_prod / lab_owner_prod'],
        ['Contraseña y token', 'Aleatorios, propios', 'Aleatorios, propios (token de 32 o más caracteres)'],
        ['Puerto', '3000', '8080'],
    ]))

    # 5
    p.append('<h1>5. Fase 4 - Validación, Análisis y Pruebas</h1>')
    p.append("""<p>La versión segura se ejecutó con npm run dev en http://localhost:3000. La página consulta la API real y muestra productos y
usuarios sin password_hash. El panel «Verificaciones en vivo» realiza peticiones reales al cargar: /debug y /admin/sql responden 404 y
escribir sin token responde 401.</p>""")
    p.append(figura('33-labsecretos-web-segura.png', 'Aplicación segura funcionando en http://localhost:3000, entorno development'))
    p.append(figura('34-labsecretos-web-token-rechazado.png', 'Prueba funcional: guardar un producto con un token incorrecto es rechazado (HTTP 401)'))
    p.append(figura('28-labsecretos-app-segura.png', 'Pruebas con curl: el POST con token válido responde 201 (el token se leyó de la variable de entorno y no se muestra)'))
    p.append("""<p>Después se simuló que un atacante roba las credenciales del rol de la aplicación. La base de datos rechazó todo salvo la lectura
permitida, y el usuario de development tampoco puede conectarse a la base de production.</p>""")
    p.append(figura('29-labsecretos-minimo-privilegio.png', 'Intentos de leer password_hash, borrar tablas y crear roles: denegados por PostgreSQL'))
    p.append("""<p>Finalmente, el script tests/pruebas.js (npm test) arranca la aplicación en ambos ambientes y ejecuta 28 comprobaciones en cinco
grupos: funcionales, control de acceso, mínimo privilegio, separación de ambientes y configuración. También verifica que ninguna respuesta ni
registro contenga los secretos reales.</p>""")
    p.append(figura('30-labsecretos-pruebas.png', 'Resultado de npm test: 28 pruebas pasan, 0 fallan'))
    p.append(figura('31-labsecretos-config-faltante.png', 'Sin configuración la aplicación falla rápido sin imprimir valores; las plantillas no contienen secretos'))
    p.append('<h2>5.1 Vulnerabilidades corregidas y riesgos mitigados</h2>')
    p.append(tabla(['Aspecto', 'Versión insegura', 'Versión segura'], [
        ['Contraseña de BD', 'Literal en el código', 'Variable de entorno aleatoria'],
        ['Token de API', 'Fijo y visible', 'Variable de entorno; comparación en tiempo constante'],
        ['Rol de la aplicación', 'Superusuario', 'Sin privilegios de administrador'],
        ['Datos sensibles', 'password_hash expuesto', 'Sin acceso (a nivel de BD y de API)'],
        ['Depuración', '/debug y /admin/sql activos', 'Eliminados (404)'],
        ['Registros de arranque', 'Imprime token y clave', 'Sin secretos'],
        ['Ambientes', 'Uno solo', 'Dos, aislados'],
        ['Hallazgos del escáner', '3', '0'],
    ]))
    p.append("""<p><b>Limitaciones.</b> Los archivos .env siguen existiendo en el disco del equipo; en producción conviene un gestor de secretos con
rotación y auditoría. Si un secreto se hubiera confirmado en Git antes de aplicar .gitignore, seguiría en el historial y habría que rotarlo.
Tampoco se configuró TLS hacia la base de datos ni limitación de peticiones, y las pruebas se hicieron en un entorno local de laboratorio.</p>""")

    # 6-8
    p.append('<h1>6. Conclusiones</h1>')
    p.append("""<ul>
<li>Esta práctica demostró que las vulnerabilidades más peligrosas no son las más complejas. Dejar una contraseña en el código o conectar la
aplicación con un superusuario puede comprometer por completo un sistema, y corregirlo requirió pocas líneas.</li>
<li>La seguridad debe ser parte del desarrollo desde el inicio, no un paso opcional al final. Aplicar variables de entorno, .gitignore y
configuración validada no requiere un esfuerzo adicional significativo, pero la diferencia en protección es enorme.</li>
<li>Configurar correctamente los permisos de la base de datos es tan importante como proteger el código: con el rol limitado, aun con las
credenciales robadas, PostgreSQL rechazó leer password_hash, borrar tablas o crear roles.</li>
<li>Separar ambientes con credenciales distintas evita que una filtración en desarrollo comprometa producción.</li></ul>""")
    p.append('<h1>7. Recomendaciones</h1>')
    p.append('<p>Basado en las vulnerabilidades identificadas, se recomienda:</p>')
    p.append("""<ul>
<li>Usar variables de entorno: las credenciales nunca deben estar en el código; deben almacenarse en archivos .env excluidos del repositorio
con .gitignore, y en producción en un gestor de secretos con rotación.</li>
<li>Aplicar mínimo privilegio: una cuenta distinta para migraciones y para la aplicación, con permisos por tabla y por columna.</li>
<li>Automatizar la detección: ejecutar el escáner de secretos como pre-commit hook y en la integración continua.</li>
<li>Rotar de inmediato cualquier secreto que llegue a confirmarse en Git, ya que .gitignore no borra el historial.</li>
<li>Activar TLS hacia la base de datos y reemplazar el token estático por autenticación con expiración.</li></ul>""")
    p.append('<h1>8. Referencias</h1>')
    for r in [
        "OWASP Foundation. (2021). A05:2021 Security Misconfiguration. https://owasp.org/Top10/A05_2021-Security_Misconfiguration/",
        "OWASP Foundation. Secrets Management Cheat Sheet. https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
        "MITRE. CWE-798: Use of Hard-coded Credentials. https://cwe.mitre.org/data/definitions/798.html",
        "MITRE. CWE-532: Insertion of Sensitive Information into Log File. https://cwe.mitre.org/data/definitions/532.html",
        "The Twelve-Factor App. III. Config. https://12factor.net/config",
        "PostgreSQL Global Development Group. PostgreSQL Documentation: Privileges. https://www.postgresql.org/docs/current/ddl-priv.html",
        "Express.js. Express - Node.js web application framework. https://expressjs.com/",
        "dotenv (motdotla). https://github.com/motdotla/dotenv",
    ]:
        p.append(f'<p class="ref">- {r}</p>')

    p.append('<h1>Anexo. Código corregido</h1>')
    for rel in CODIGO:
        ruta = RAIZ / rel
        if not ruta.exists():
            print(f"AVISO: no existe {rel}", file=sys.stderr)
            continue
        p.append(f'<p class="codigo-t">{esc(rel)}</p><pre>{esc(ruta.read_text(encoding="utf-8"))}</pre>')
    return "\n".join(p)


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    html_path = SALIDA / "informe_secretos.html"
    html_path.write_text(
        f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Gestión de secretos y configuración segura</title>'
        f'<style>{CSS}</style></head><body>{cuerpo()}</body></html>', encoding="utf-8")
    pdf = SALIDA / "Informe_Lab_Gestion_Secretos.pdf"
    exe = next((n for n in [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"] if Path(n).exists()), None)
    if not exe:
        sys.exit("No se encontró Chrome ni Edge; abre informe_secretos.html e imprime a PDF.")
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", html_path.as_uri()], check=True)
    print(f"PDF generado: {pdf}")


if __name__ == "__main__":
    main()
