// ============================================================
// VERSIÓN INSEGURA (Fase 2) — SOLO PARA FINES DIDÁCTICOS
// No usar en ningún entorno real. Todas las credenciales son ficticias.
// ============================================================
const path = require('path');
const express = require('express');
const { Pool } = require('pg');

// VULN-01: contraseña de BD escrita en el código fuente
// VULN-02: la app se conecta con un SUPERUSUARIO (privilegios innecesarios)
const pool = new Pool({
  host: 'localhost',
  port: 54329,
  database: 'lab_vuln',
  user: 'lab_vuln_admin',
  password: 'admin123',
});

// VULN-03: token de API expuesto en el código
const API_TOKEN = 'lab-token-12345-INSEGURO';

const app = express();
app.use(express.json());
app.use('/ui', express.static(path.join(__dirname, '..', 'ui')));
app.get('/', (_req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.get('/api/productos', async (_req, res) => {
  const r = await pool.query('SELECT * FROM productos ORDER BY id');
  res.json(r.rows);
});

// VULN-04: SELECT * devuelve también password_hash
app.get('/api/usuarios', async (_req, res) => {
  const r = await pool.query('SELECT * FROM usuarios ORDER BY id');
  res.json(r.rows);
});

app.post('/api/productos', async (req, res) => {
  if (req.headers.authorization !== 'Bearer ' + API_TOKEN) return res.sendStatus(401);
  const { nombre, precio } = req.body;
  const r = await pool.query('INSERT INTO productos (nombre,precio) VALUES ($1,$2) RETURNING *', [nombre, precio]);
  res.status(201).json(r.rows[0]);
});

// VULN-05: endpoint de depuración que vuelca la configuración completa
app.get('/debug', (_req, res) => {
  res.json({ db: pool.options, token: API_TOKEN, env: process.env.NODE_ENV });
});

// VULN-06: ejecuta SQL arbitrario con el superusuario (aprovechable si se filtra el token)
app.post('/admin/sql', async (req, res) => {
  try { res.json((await pool.query(req.body.sql)).rows); }
  catch (e) { res.status(500).json({ error: e.message, stack: e.stack }); }
});

// VULN-07: el token se imprime en consola/logs
app.listen(3001, () => console.log('[INSEGURA] http://localhost:3001  token=' + API_TOKEN + ' db=lab_vuln_admin:admin123'));
