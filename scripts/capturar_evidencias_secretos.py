"""Genera las capturas del lab de secretos (docs/evidencias/23..31) ejecutando los comandos DE VERDAD
y fotografiando la salida con Chrome headless. Los secretos reales (.env) nunca se imprimen.

Requiere: PostgreSQL de laboratorio en el puerto PG_ADMIN_PORT (var. de entorno PG_ADMIN_PORT / PG_ADMIN_PASSWORD).
Uso: python scripts/capturar_evidencias_secretos.py
"""
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LAB = RAIZ / "lab-secretos"
EVID = RAIZ / "docs" / "evidencias"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASH = shutil.which("bash")
PSQL = r"C:\Program Files\PostgreSQL\18\bin\psql.exe"
ADMIN_PORT = os.environ.get("PG_ADMIN_PORT", "5432")
ADMIN_PW = os.environ["PG_ADMIN_PASSWORD"]


def leer_env(nombre):
    d = {}
    for l in (LAB / nombre).read_text(encoding="utf-8").splitlines():
        if "=" in l:
            k, v = l.split("=", 1)
            d[k] = v
    return d


ENV_DEV = leer_env(".env.development")
SECRETOS = [ENV_DEV["DB_PASSWORD"], ENV_DEV["API_TOKEN"], leer_env(".env.production")["DB_PASSWORD"], leer_env(".env.production")["API_TOKEN"]]


def ejecutar(cmd, extra_env=None):
    env = {**os.environ, "PGCLIENTENCODING": "UTF8", **(extra_env or {})}
    r = subprocess.run([BASH, "-c", cmd], cwd=LAB, env=env, capture_output=True, timeout=120)

    def dec(linea):  # libpq puede emitir cp1252 en Windows; el resto es UTF-8
        try:
            return linea.decode("utf-8")
        except UnicodeDecodeError:
            return linea.decode("cp1252", errors="replace")
    salida = chr(10).join(dec(l) for l in (r.stdout + r.stderr).rstrip().splitlines())
    for s in SECRETOS:  # red de seguridad: jamás fotografiar un secreto real
        assert s not in salida, "¡secreto real en la salida! se aborta"
    return salida


CSS = """
body{margin:0;background:#0d1117;font-family:'Cascadia Mono',Consolas,monospace;color:#e6edf3;}
.win{margin:14px;border:1px solid #30363d;border-radius:10px;overflow:hidden;background:#0d1117}
.bar{background:#161b22;padding:8px 14px;font-size:13px;color:#8b949e;display:flex;align-items:center;gap:8px;border-bottom:1px solid #30363d}
.dot{width:11px;height:11px;border-radius:50%;display:inline-block}
.r{background:#ff5f56}.y{background:#ffbd2e}.g{background:#27c93f}
.body{padding:14px 18px;font-size:13.5px;line-height:1.45;white-space:pre-wrap;word-break:break-all}
.p{color:#7ee787}.c{color:#79c0ff}.out{color:#c9d1d9}
.bad{background:#5c1a1a;color:#ffb3b3;margin:0 -18px;padding:0 18px}
.body div{min-height:1.45em}
.good{color:#7ee787}.bd{color:#ff7b72}
.nota{margin-top:10px;padding:8px 12px;border-left:3px solid #d29922;background:#1f1a0a;color:#f2cc60;font-size:12.5px;white-space:pre-wrap}
"""


def resaltar(linea):
    t = html.escape(linea)
    t = re.sub(r"(\[PASA\])", r'<span class="good">\1</span>', t)
    t = re.sub(r"(\[FALLA\]|\[HALLAZGO\]|permiso denegado[^<]*|ERROR:[^<]*|ERROR\b)", r'<span class="bd">\1</span>', t)
    return t


def render(titulo, pasos, nota=None):
    cuerpo = []
    nlineas = 0
    for visible, salida in pasos:
        cuerpo.append(f'<div><span class="p">$</span> <span class="c">{html.escape(visible)}</span></div>')
        nlineas += 1 + visible.count("\n")
        for l in salida.splitlines():
            marca = ("VULN-" in l) and l.lstrip()[:2] == "//" or "password: 'admin123'" in l or "API_TOKEN = 'lab" in l
            t = resaltar(l)
            cuerpo.append(f'<div class="bad">{t}</div>' if marca else f'<div class="out">{t}</div>')
            nlineas += 1 + len(l) // 125
        cuerpo.append("<div></div>")
        nlineas += 1
    if nota:
        cuerpo.append(f'<div class="nota">{html.escape(nota)}</div>')
        nlineas += 2 + len(nota) // 110
    pagina = (f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><div class="win"><div class="bar">'
              f'<span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>&nbsp;{html.escape(titulo)}</div>'
              f'<div class="body">{''.join(cuerpo)}</div></div>')
    return pagina, 60 + nlineas * 20 + 75


def foto(nombre, titulo, pasos, nota=None):
    pagina, alto = render(titulo, pasos, nota)
    tmp = Path(tempfile.mkdtemp()) / "t.html"
    tmp.write_text(pagina, encoding="utf-8")
    destino = EVID / nombre
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1.4",
                    f"--window-size=1180,{alto}", f"--screenshot={destino}", tmp.as_uri()], check=True, capture_output=True)
    print("capturada", nombre)


def levantar(cmd, extra_env=None):
    env = {**os.environ, **(extra_env or {})}
    p = subprocess.Popen([BASH, "-c", cmd], cwd=LAB, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    time.sleep(2.5)
    return p


def parar(p, puerto):
    """Mata el árbol de procesos y, por seguridad, cualquier node que siga escuchando en el puerto."""
    p.kill()
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
    subprocess.run(["powershell", "-NoProfile", "-c", f"Get-NetTCPConnection -LocalPort {puerto} -State Listen -ErrorAction SilentlyContinue | % {{ Stop-Process -Id $_.OwningProcess -Force }}"], capture_output=True)


def sh(visible, real=None, **kw):
    return visible, ejecutar(real or visible, **kw)


PSQL_ADMIN = f'"{PSQL}" -h localhost -p {ADMIN_PORT} -U postgres'
ADM = {"PGPASSWORD": ADMIN_PW}
APP = {"PGPASSWORD": ENV_DEV["DB_PASSWORD"]}
PSQL_APP = f'"{PSQL}" -h localhost -p {ADMIN_PORT} -U {ENV_DEV["DB_USER"]} -d {ENV_DEV["DB_NAME"]}'

# 01 — código vulnerable
foto("23-labsecretos-codigo-vulnerable.png", "vulnerable/app.js — Fase 2: implementación insegura controlada", [
    sh(r"""awk 'NR>=9&&NR<=20||NR>=44&&NR<=57{printf "%3d  %s\n",NR,$0}' vulnerable/app.js"""),
    sh("grep -n \"SUPERUSER\" db/00_vulnerable.sql"),
], "Marcadas en rojo: VULN-01 contraseña en código, VULN-02 superusuario, VULN-03 token en código, VULN-05/06/07 depuración, SQL libre y token en logs.")

# 02 — explotación de la versión vulnerable
v = levantar("node vulnerable/app.js")
try:
    foto("24-labsecretos-explotacion-vulnerable.png", "Explotación de la versión insegura (puerto 3001)", [
        sh("curl -s localhost:3001/debug"),
        sh("curl -s localhost:3001/api/usuarios"),
        sh("curl -s -X POST localhost:3001/admin/sql -H 'content-type: application/json' -d '{\"sql\":\"SELECT current_user, usesuper FROM pg_user WHERE usename=current_user\"}'"),
        sh("curl -s -w ' -> HTTP %{http_code}\n' -X POST localhost:3001/admin/sql -H 'content-type: application/json' -d '{\"sql\":\"CREATE TABLE demo_poder(a int)\"}'"),
        sh("curl -s -w ' -> HTTP %{http_code}\n' -X POST localhost:3001/admin/sql -H 'content-type: application/json' -d '{\"sql\":\"DROP TABLE demo_poder\"}'"),
    ], "Hallazgos: /debug revela usuario, clave y token; /api/usuarios filtra password_hash; la cuenta de la app es SUPERUSER y puede ejecutar DDL (se crea y borra una tabla de prueba inofensiva).")
finally:
    parar(v, 3001)

# 03 — escáner
foto("25-labsecretos-escaner-secretos.png", "Escáner de secretos: insegura vs. segura", [
    sh("node scripts/scan-secrets.js vulnerable seguro; echo \"código de salida: $?\""),
])

# 04 — gitignore
foto("26-labsecretos-gitignore.png", "Exclusión de secretos con .gitignore", [
    sh("cat .gitignore"),
    sh("ls -1A | grep -E '^\\.env'"),
    sh("git check-ignore -v .env.development .env.production"),
    sh("git add -n . | grep -i env || true"),
    sh("git ls-files -- '.env*'"),
], "Los archivos .env.development y .env.production existen en disco, pero git los ignora: solo se versionan las plantillas *.example (sin valores).")

# 05 — roles y permisos
foto("27-labsecretos-roles-privilegios.png", "Roles de mínimo privilegio en PostgreSQL", [
    sh("psql -c \"SELECT rolname, rolsuper AS super, rolcreatedb AS createdb, rolcreaterole AS createrole FROM pg_roles WHERE rolname LIKE 'lab\\_%' ORDER BY 1\"",
       PSQL_ADMIN + " -c \"SELECT rolname, rolsuper AS super, rolcreatedb AS createdb, rolcreaterole AS createrole FROM pg_roles WHERE rolname LIKE 'lab\\_%' ORDER BY 1\"", extra_env=ADM),
    sh("psql -d lab_dev -c \"SELECT table_name, privilege_type, grantee FROM information_schema.role_table_grants WHERE grantee='lab_app_dev' ORDER BY 1,2\"",
       PSQL_ADMIN + " -d lab_dev -c \"SELECT table_name, privilege_type, grantee FROM information_schema.role_table_grants WHERE grantee='lab_app_dev' ORDER BY 1,2\"", extra_env=ADM),
    sh("psql -d lab_dev -c \"SELECT table_name, column_name, privilege_type FROM information_schema.column_privileges WHERE grantee='lab_app_dev' AND table_name='usuarios' ORDER BY 2\"",
       PSQL_ADMIN + " -d lab_dev -c \"SELECT table_name, column_name, privilege_type FROM information_schema.column_privileges WHERE grantee='lab_app_dev' AND table_name='usuarios' ORDER BY 2\"", extra_env=ADM),
], "lab_vuln_admin es SUPERUSER (versión insegura). lab_app_* solo tienen SELECT/INSERT en productos y SELECT de 3 columnas en usuarios (sin password_hash). Un owner distinto por ambiente hace el DDL.")

# 06 — app segura en ejecución
LOG = Path(tempfile.mkdtemp()) / "dev.log"
s = levantar(f"npm run dev --silent > '{LOG.as_posix()}' 2>&1")
try:
    foto("28-labsecretos-app-segura.png", "Aplicación segura en ejecución (development)", [
        ("npm run dev", LOG.read_text(encoding="utf-8").strip()),
        sh("curl -s localhost:3000/health"),
        sh("curl -s localhost:3000/api/productos"),
        sh("curl -s localhost:3000/api/usuarios"),
        sh("curl -s -o /dev/null -w 'GET /debug -> HTTP %{http_code}\\n' localhost:3000/debug"),
        sh("curl -s -w ' -> HTTP %{http_code}\\n' -X POST localhost:3000/api/productos -H 'content-type: application/json' -d '{\"nombre\":\"Borrador\",\"precio\":0.4}'"),
        sh("curl -s -w ' -> HTTP %{http_code}\\n' -X POST localhost:3000/api/productos -H \"Authorization: Bearer $API_TOKEN\" -H 'content-type: application/json' -d '{\"nombre\":\"Borrador\",\"precio\":0.4}'",
           extra_env={"API_TOKEN": ENV_DEV["API_TOKEN"]}),
    ], "La app funciona con configuración tomada de .env.development. /debug ya no existe, usuarios no expone password_hash y el POST exige el token (leído de la variable de entorno, no mostrado).")
finally:
    parar(s, 3000)

# 07 — mínimo privilegio en acción
foto("29-labsecretos-minimo-privilegio.png", "Intentos de abuso con el rol de la aplicación (lab_app_dev)", [
    sh("psql -U lab_app_dev -d lab_dev -c \"SELECT nombre, precio FROM productos LIMIT 2\"", PSQL_APP + " -c \"SELECT nombre, precio FROM productos LIMIT 2\"", extra_env=APP),
    sh("psql -U lab_app_dev -d lab_dev -c \"SELECT password_hash FROM usuarios\"", PSQL_APP + " -c \"SELECT password_hash FROM usuarios\"", extra_env=APP),
    sh("psql -U lab_app_dev -d lab_dev -c \"DROP TABLE productos\"", PSQL_APP + " -c \"DROP TABLE productos\"", extra_env=APP),
    sh("psql -U lab_app_dev -d lab_dev -c \"DELETE FROM productos\"", PSQL_APP + " -c \"DELETE FROM productos\"", extra_env=APP),
    sh("psql -U lab_app_dev -d lab_dev -c \"CREATE ROLE intruso SUPERUSER\"", PSQL_APP + " -c \"CREATE ROLE intruso SUPERUSER\"", extra_env=APP),
    sh("psql -U lab_app_dev -d lab_prod -c \"SELECT 1\"   # cruce de ambientes", PSQL_APP.replace(f'-d {ENV_DEV["DB_NAME"]}', "-d lab_prod") + " -c \"SELECT 1\"", extra_env=APP),
], "Solo la lectura permitida funciona; todo lo demás es denegado por la base de datos, aunque alguien robara las credenciales de la app.")

# 08 — pruebas automáticas
foto("30-labsecretos-pruebas.png", "Fase 4: pruebas funcionales y de seguridad (npm test)", [
    sh("npm test --silent"),
])

# 09 — configuración faltante
foto("31-labsecretos-config-faltante.png", "Falla rápida sin exponer valores", [
    sh("DOTENV_PATH=./no-existe.env NODE_ENV=production node seguro/app.js; echo \"código de salida: $?\""),
    sh("grep -n 'API_TOKEN\\|DB_PASSWORD' .env.example .env.development.example .env.production.example 2>/dev/null || grep -n 'DB_PASSWORD\\|API_TOKEN' .env.development.example"),
])
print("listo")
