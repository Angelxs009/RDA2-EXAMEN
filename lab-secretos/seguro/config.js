// Carga de configuración segura: secretos SOLO desde variables de entorno / archivo .env ignorado por git.
const path = require('path');
const dotenv = require('dotenv');

const entorno = process.env.NODE_ENV === 'production' ? 'production' : 'development';
// Separación de ambientes: .env.development vs .env.production (distintos usuarios, BD y tokens).
// dotenv no pisa variables ya definidas, así que en producción real mandan las del gestor/CI.
dotenv.config({ path: process.env.DOTENV_PATH || path.join(__dirname, '..', `.env.${entorno}`) });

const REQUERIDAS = ['PORT', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'API_TOKEN'];
const faltan = REQUERIDAS.filter((k) => !process.env[k]);
if (faltan.length) {
  // Falla rápido, sin imprimir valores: solo los nombres de las variables que faltan.
  console.error(`Configuración incompleta (${entorno}). Faltan: ${faltan.join(', ')}`);
  process.exit(1);
}
if (entorno === 'production' && process.env.API_TOKEN.length < 32) {
  console.error('API_TOKEN demasiado corto para producción (mínimo 32 caracteres).');
  process.exit(1);
}

module.exports = Object.freeze({
  entorno,
  port: Number(process.env.PORT),
  db: Object.freeze({
    host: process.env.DB_HOST, port: Number(process.env.DB_PORT),
    database: process.env.DB_NAME, user: process.env.DB_USER, password: process.env.DB_PASSWORD,
  }),
  apiToken: process.env.API_TOKEN,
});
