// Crea BD, roles de mínimo privilegio y archivos .env.<entorno> con secretos ALEATORIOS.
// Las credenciales de administración se leen de variables de entorno (nunca del código):
//   PG_ADMIN_HOST, PG_ADMIN_PORT, PG_ADMIN_USER, PG_ADMIN_PASSWORD
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { Client } = require('pg');

const admin = {
  host: process.env.PG_ADMIN_HOST || 'localhost',
  port: Number(process.env.PG_ADMIN_PORT || 5432),
  user: process.env.PG_ADMIN_USER || 'postgres',
  password: process.env.PG_ADMIN_PASSWORD,
};
if (!admin.password) { console.error('Define PG_ADMIN_PASSWORD en el entorno.'); process.exit(1); }

const ENTORNOS = [
  { nombre: 'development', sufijo: 'dev', puerto: 3000 },
  { nombre: 'production', sufijo: 'prod', puerto: 8080 },
];
const rand = (n) => crypto.randomBytes(n).toString('hex');
const ident = (s) => '"' + s.replace(/"/g, '""') + '"';
const lit = (s) => "'" + s.replace(/'/g, "''") + "'";

async function conectar(database) {
  const c = new Client({ ...admin, database });
  await c.connect();
  return c;
}

(async () => {
  const schema = fs.readFileSync(path.join(__dirname, '..', 'db', '01_esquema_seguro.sql'), 'utf8');
  for (const e of ENTORNOS) {
    const owner = `lab_owner_${e.sufijo}`, app = `lab_app_${e.sufijo}`, db = `lab_${e.sufijo}`;
    const pwOwner = rand(16), pwApp = rand(16), token = rand(24); // 48 caracteres hex

    const c = await conectar('postgres');
    for (const [rol, pw] of [[owner, pwOwner], [app, pwApp]]) {
      const existe = (await c.query('SELECT 1 FROM pg_roles WHERE rolname=$1', [rol])).rowCount;
      // Roles SIN superusuario, sin CREATEDB, sin CREATEROLE
      await c.query(`${existe ? 'ALTER' : 'CREATE'} ROLE ${ident(rol)} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD ${lit(pw)}`);
    }
    await c.query(`DROP DATABASE IF EXISTS ${ident(db)}`);
    await c.query(`CREATE DATABASE ${ident(db)} OWNER ${ident(owner)}`);
    await c.query(`REVOKE CONNECT ON DATABASE ${ident(db)} FROM PUBLIC`);       // aislamiento entre ambientes
    await c.query(`GRANT CONNECT ON DATABASE ${ident(db)} TO ${ident(app)}`);
    await c.end();

    // El esquema se crea con el rol OWNER (DDL); la app solo recibe los GRANT mínimos
    const o = new Client({ ...admin, database: db, user: owner, password: pwOwner });
    await o.connect();
    await o.query(schema.replace(/:"app"/g, ident(app)));
    await o.end();

    const archivo = path.join(__dirname, '..', `.env.${e.nombre}`);
    fs.writeFileSync(archivo, [
      `NODE_ENV=${e.nombre}`, `PORT=${e.puerto}`, `DB_HOST=${admin.host}`, `DB_PORT=${admin.port}`,
      `DB_NAME=${db}`, `DB_USER=${app}`, `DB_PASSWORD=${pwApp}`, `API_TOKEN=${token}`, '',
    ].join('\n'), { mode: 0o600 });
    console.log(`[ok] ${e.nombre}: BD=${db} rol app=${app} -> .env.${e.nombre} (secretos no mostrados)`);
  }
})().catch((err) => { console.error('Error:', err.message); process.exit(1); });
