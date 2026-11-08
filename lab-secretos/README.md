# Lab: Gestión de Secretos y Configuración Segura

API Node.js + PostgreSQL con dos versiones: `vulnerable/` (errores intencionales, credenciales **ficticias**) y `seguro/` (corregida).

```
vulnerable/app.js        Fase 2: contraseña/token en código, superusuario, /debug, /admin/sql
seguro/config.js         Fase 3: carga .env.<entorno>, valida variables, falla sin mostrar valores
seguro/app.js            Fase 3: API sin fugas, token en tiempo constante, errores genéricos
db/00_vulnerable.sql     Rol SUPERUSER + datos (solo laboratorio)
db/01_esquema_seguro.sql Esquema + GRANT mínimos (incluye permisos por columna)
scripts/setup-db.js      Crea BD/roles por ambiente y genera .env.* con secretos aleatorios
scripts/scan-secrets.js  Escáner de secretos (sale con código 1 si encuentra algo)
tests/pruebas.js         28 pruebas funcionales y de seguridad
```

## Uso

```bash
npm install

# 1) Versión insegura (opcional): crear su BD con un admin de un PostgreSQL de LABORATORIO
psql -h localhost -p <puerto> -U postgres -f db/00_vulnerable.sql
#    (ajusta el puerto en vulnerable/app.js) y luego:  npm run vulnerable

# 2) Versión segura: las credenciales de administración se pasan por entorno, nunca en el código
PG_ADMIN_HOST=localhost PG_ADMIN_PORT=5432 PG_ADMIN_USER=postgres PG_ADMIN_PASSWORD=*** npm run setup:db
npm run dev        # development (puerto 3000)
npm start          # production  (puerto 8080)

npm run scan       # busca secretos en el código
npm test           # pruebas Fase 4
```

`setup:db` crea `lab_dev`/`lab_prod`, los roles `lab_owner_*` (DDL) y `lab_app_*` (runtime, mínimo privilegio) y escribe
`.env.development` / `.env.production` (ignorados por git). **No uses un PostgreSQL con datos reales**: `setup:db` hace
`DROP DATABASE IF EXISTS` sobre `lab_dev` y `lab_prod`.

Informe: `docs/informe/Informe_Lab_Gestion_Secretos.pdf` · Evidencias: `docs/evidencias/23..31-labsecretos-*.png`
(regenerables con `scripts/capturar_evidencias_secretos.py` y `scripts/generar_informe_secretos.py`).
