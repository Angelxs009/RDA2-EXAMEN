// Pruebas funcionales y de seguridad (Fase 4). Arranca la app segura en development y production.
// Uso: npm test      (requiere haber ejecutado npm run setup:db)
const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');
const { Client } = require('pg');

const raiz = path.join(__dirname, '..');
const envs = {
  development: dotenv.parse(fs.readFileSync(path.join(raiz, '.env.development'))),
  production: dotenv.parse(fs.readFileSync(path.join(raiz, '.env.production'))),
};
const secretos = Object.values(envs).flatMap((e) => [e.DB_PASSWORD, e.API_TOKEN]);

let ok = 0, fallos = 0;
const prueba = (nombre, cond, detalle = '') => {
  cond ? ok++ : fallos++;
  console.log(`  ${cond ? '[PASA]' : '[FALLA]'} ${nombre}${detalle ? '  -> ' + detalle : ''}`);
};
const pausa = (ms) => new Promise((r) => setTimeout(r, ms));
const vistas = []; // todo lo que ve un cliente, para buscar fugas de secretos

async function http(puerto, ruta, opts = {}) {
  const r = await fetch(`http://localhost:${puerto}${ruta}`, opts);
  const texto = await r.text();
  vistas.push(texto);
  return { status: r.status, texto, json: () => JSON.parse(texto) };
}

function lanzar(entorno) {
  const p = spawn(process.execPath, [path.join(raiz, 'seguro', 'app.js')], {
    env: { PATH: process.env.PATH, SystemRoot: process.env.SystemRoot, NODE_ENV: entorno }, cwd: raiz,
  });
  let salida = '';
  p.stdout.on('data', (d) => (salida += d)); p.stderr.on('data', (d) => (salida += d));
  return { p, salida: () => salida };
}

async function intentar(cliente, sql) {
  try { await cliente.query(sql); return { ok: true }; } catch (e) { return { ok: false, msg: e.message }; }
}

(async () => {
  const dev = lanzar('development'), prod = lanzar('production');
  await pausa(1800);
  const pd = Number(envs.development.PORT), pp = Number(envs.production.PORT);
  try {
    console.log('\n== 1. Pruebas funcionales ==');
    const hd = await http(pd, '/health'), hp = await http(pp, '/health');
    prueba('GET /health responde 200 en development y production', hd.status === 200 && hp.status === 200);
    prueba('Cada ambiente informa su propio entorno', hd.json().entorno === 'development' && hp.json().entorno === 'production');
    const prods = await http(pd, '/api/productos');
    prueba('GET /api/productos devuelve el catálogo (>= 3 productos)', prods.status === 200 && prods.json().length >= 3);
    const t = envs.development.API_TOKEN;
    const creado = await http(pd, '/api/productos', { method: 'POST', headers: { 'content-type': 'application/json', authorization: 'Bearer ' + t }, body: JSON.stringify({ nombre: 'Regla', precio: 1.2 }) });
    prueba('POST con token válido crea el producto (201)', creado.status === 201 && creado.json().nombre === 'Regla');
    const malo = await http(pd, '/api/productos', { method: 'POST', headers: { 'content-type': 'application/json', authorization: 'Bearer ' + t }, body: JSON.stringify({ nombre: '', precio: -1 }) });
    prueba('POST con datos inválidos se rechaza (400)', malo.status === 400);

    console.log('\n== 2. Control de acceso y exposición de datos ==');
    const sinTok = await http(pd, '/api/productos', { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{"nombre":"x","precio":1}' });
    prueba('POST sin token -> 401', sinTok.status === 401);
    const tokProd = await http(pd, '/api/productos', { method: 'POST', headers: { 'content-type': 'application/json', authorization: 'Bearer ' + envs.production.API_TOKEN }, body: '{"nombre":"x","precio":1}' });
    prueba('El token de producción NO sirve en development (401)', tokProd.status === 401);
    const usr = await http(pd, '/api/usuarios');
    prueba('GET /api/usuarios no expone password_hash', usr.status === 200 && !usr.texto.includes('password_hash') && !usr.texto.includes('FAKEHASH'));
    prueba('/debug eliminado (404)', (await http(pd, '/debug')).status === 404);
    prueba('/admin/sql eliminado (404)', (await http(pd, '/admin/sql', { method: 'POST' })).status === 404);
    const roto = await http(pd, '/api/productos', { method: 'POST', headers: { 'content-type': 'application/json', authorization: 'Bearer ' + t }, body: '{"nombre":' });
    prueba('Errores sin stack trace ni detalles internos', !/at .*\.js|node_modules|password|lab_app/i.test(roto.texto), roto.texto.replace(/\s+/g, ' ').slice(0, 60));
    prueba('Ninguna respuesta del servidor contiene secretos', !vistas.some((v) => secretos.some((s) => v.includes(s))));
    const logs = dev.salida() + prod.salida();
    prueba('Los logs de arranque no contienen secretos', !secretos.some((s) => logs.includes(s)));

    console.log('\n== 3. Mínimo privilegio en base de datos (rol de la app) ==');
    const e = envs.development;
    const cli = new Client({ host: e.DB_HOST, port: Number(e.DB_PORT), database: e.DB_NAME, user: e.DB_USER, password: e.DB_PASSWORD });
    await cli.connect();
    const su = (await cli.query("SELECT rolsuper, rolcreatedb, rolcreaterole FROM pg_roles WHERE rolname = current_user")).rows[0];
    prueba('El rol de la app NO es superusuario / createdb / createrole', !su.rolsuper && !su.rolcreatedb && !su.rolcreaterole);
    for (const [nombre, sql] of [
      ['SELECT password_hash denegado', 'SELECT password_hash FROM usuarios'],
      ['DROP TABLE denegado', 'DROP TABLE productos'],
      ['DELETE denegado', 'DELETE FROM productos'],
      ['UPDATE denegado', 'UPDATE productos SET precio = 0'],
      ['CREATE ROLE denegado', 'CREATE ROLE intruso'],
      ['CREATE TABLE denegado', 'CREATE TABLE x (a int)'],
    ]) {
      const r = await intentar(cli, sql);
      prueba(nombre, !r.ok, r.msg);
    }
    await cli.end();
    const cruzado = new Client({ host: e.DB_HOST, port: Number(e.DB_PORT), database: envs.production.DB_NAME, user: e.DB_USER, password: e.DB_PASSWORD });
    let cruzo = true; try { await cruzado.connect(); await cruzado.end(); } catch { cruzo = false; }
    prueba('El usuario de development NO puede conectarse a la BD de production', !cruzo);

    console.log('\n== 4. Separación de ambientes ==');
    prueba('Distinta base de datos', envs.development.DB_NAME !== envs.production.DB_NAME);
    prueba('Distinto usuario de BD', envs.development.DB_USER !== envs.production.DB_USER);
    prueba('Distinta contraseña de BD y distinto token', envs.development.DB_PASSWORD !== envs.production.DB_PASSWORD && envs.development.API_TOKEN !== envs.production.API_TOKEN);
    prueba('Token de producción >= 32 caracteres', envs.production.API_TOKEN.length >= 32);

    console.log('\n== 5. Configuración faltante / archivos ignorados ==');
    const sinCfg = spawnSync(process.execPath, ['-e', "require('./seguro/config')"], { env: { PATH: process.env.PATH, SystemRoot: process.env.SystemRoot, NODE_ENV: 'production', DOTENV_PATH: path.join(raiz, 'no-existe.env') }, cwd: raiz, encoding: 'utf8' });
    prueba('Sin variables la app falla rápido (código 1) listando solo nombres', sinCfg.status === 1 && /Faltan: PORT/.test(sinCfg.stderr), sinCfg.stderr.trim().slice(0, 70));
    const ign = ['.env.development', '.env.production'].map((f) => spawnSync('git', ['check-ignore', '-q', f], { cwd: raiz }).status);
    prueba('.env.development y .env.production están en .gitignore', ign.every((x) => x === 0));
    const trk = spawnSync('git', ['ls-files', '--', '.env.development', '.env.production'], { cwd: raiz, encoding: 'utf8' });
    prueba('Ningún archivo .env real está versionado', trk.stdout.trim() === '');
  } finally {
    dev.p.kill(); prod.p.kill();
  }
  console.log(`\nRESUMEN: ${ok} pasan, ${fallos} fallan.`);
  process.exit(fallos ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(2); });
