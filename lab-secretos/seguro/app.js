// VERSIÓN SEGURA (Fase 3): secretos por entorno, mínimo privilegio, sin fugas de información.
const crypto = require('crypto');
const path = require('path');
const express = require('express');
const { Pool } = require('pg');
const cfg = require('./config');

const pool = new Pool(cfg.db);
const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '10kb' }));
app.use('/ui', express.static(path.join(__dirname, '..', 'ui')));
app.use(express.static(path.join(__dirname, 'public')));

// Comparación en tiempo constante del token (evita ataques de temporización)
function tokenValido(cabecera = '') {
  const dado = Buffer.from(cabecera.replace(/^Bearer /, ''));
  const esperado = Buffer.from(cfg.apiToken);
  return dado.length === esperado.length && crypto.timingSafeEqual(dado, esperado);
}
const exigirToken = (req, res, next) =>
  (tokenValido(req.headers.authorization) ? next() : res.status(401).json({ error: 'No autorizado' }));

app.get('/health', (_req, res) => res.json({ estado: 'ok', entorno: cfg.entorno }));

app.get('/api/productos', async (_req, res, next) => {
  try { res.json((await pool.query('SELECT id, nombre, precio FROM productos ORDER BY id')).rows); } catch (e) { next(e); }
});

// Solo columnas permitidas por el GRANT (sin password_hash)
app.get('/api/usuarios', async (_req, res, next) => {
  try { res.json((await pool.query('SELECT id, nombre, email FROM usuarios ORDER BY id')).rows); } catch (e) { next(e); }
});

app.post('/api/productos', exigirToken, async (req, res, next) => {
  const { nombre, precio } = req.body || {};
  if (typeof nombre !== 'string' || !nombre.trim() || nombre.length > 80 || !(Number(precio) >= 0)) {
    return res.status(400).json({ error: 'Datos inválidos' });
  }
  try {
    const r = await pool.query(
      'INSERT INTO productos (nombre, precio) VALUES ($1,$2) RETURNING id, nombre, precio', [nombre.trim(), precio]);
    res.status(201).json(r.rows[0]);
  } catch (e) { next(e); }
});

// Los endpoints /debug y /admin/sql de la versión insegura se ELIMINARON.

// Errores genéricos: el detalle va a logs internos, nunca al cliente ni con secretos
app.use((err, _req, res, _next) => {
  console.error(`[error] ${err.code || ''} ${err.message}`);
  res.status(500).json({ error: 'Error interno' });
});

app.listen(cfg.port, () =>
  console.log(`[SEGURA] entorno=${cfg.entorno} puerto=${cfg.port} usuarioBD=${cfg.db.user} (secretos no mostrados)`));
