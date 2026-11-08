// Escáner sencillo de secretos en el código. Uso: node scripts/scan-secrets.js [carpeta ...]
// Sale con código 1 si encuentra algo (útil como hook pre-commit / paso de CI).
const fs = require('fs');
const path = require('path');

const raiz = path.join(__dirname, '..');
const objetivos = process.argv.slice(2).length ? process.argv.slice(2) : ['vulnerable', 'seguro', 'scripts', 'db', 'tests'];
const REGLAS = [
  ['Contraseña literal', /(password|passwd|pwd)\s*[:=]\s*['"][^'"\s]{3,}['"]/i],
  ['Token/clave literal', /(token|api[_-]?key|secret)\s*[:=]\s*['"][^'"\s]{6,}['"]/i],
  ['Credenciales en URL', /[a-z]+:\/\/[^\s:@/]+:[^\s@/]+@/i],
  ['Rol SUPERUSER con clave en SQL', /SUPERUSER[^;]*PASSWORD\s+'[^']+'/i],
  ['Secreto impreso en logs', /console\.(log|error)\([^)]*(token|password)\s*=\s*['"]?\s*\+/i],
];

function* archivos(dir) {
  for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
    if (f.name === 'node_modules' || f.name.startsWith('.env')) continue;
    const p = path.join(dir, f.name);
    if (f.isDirectory()) yield* archivos(p); else if (/\.(js|sql|json|md|ya?ml)$/.test(f.name)) yield p;
  }
}

let total = 0;
for (const obj of objetivos) {
  const dir = path.join(raiz, obj);
  if (!fs.existsSync(dir)) continue;
  let n = 0;
  for (const f of archivos(dir)) {
    fs.readFileSync(f, 'utf8').split(/\r?\n/).forEach((linea, i) => {
      if (/^\s*(\/\/|--|#)/.test(linea) || /scan-secrets/.test(f)) return; // comentarios y este escáner
      for (const [nombre, re] of REGLAS) {
        if (re.test(linea)) { n++; console.log(`  [HALLAZGO] ${nombre}  ${path.relative(raiz, f)}:${i + 1}`); }
      }
    });
  }
  console.log(`${obj.padEnd(11)} -> ${n} hallazgo(s)`);
  total += n;
}
console.log(total ? `\nRESULTADO: ${total} posible(s) secreto(s) expuesto(s).` : '\nRESULTADO: sin secretos expuestos.');
process.exit(total ? 1 : 0);
