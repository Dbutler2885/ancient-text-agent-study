import { cp, mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const site = path.join(root, 'site');
const dist = path.join(root, 'dist');
const readJSON = async (name) => JSON.parse(await readFile(path.join(site, 'evidence', name), 'utf8'));
const manifest = await readJSON('manifest.json');
const words = await readJSON('word-location-analysis.json');
const evidence = new Set([
  'source.png', 'manifest.json', 'glyph-comparison.json',
  'word-location-analysis.json', 'glyph-atlas.png',
  'deconvolution-comparison.png', 'transcription.txt', 'analysis-report.md',
  'interpretation.json', 'reading-modes.txt',
]);

for (const region of Object.values(manifest.regions)) {
  for (const file of Object.values(region.files)) evidence.add(file);
}
for (const group of words.rows) {
  for (const token of group.tokens) evidence.add(token.file);
}
for (const file of evidence) {
  if (path.basename(file) !== file) throw new Error(`Invalid evidence filename: ${file}`);
  const info = await stat(path.join(site, 'evidence', file));
  if (!info.isFile() || info.size === 0) throw new Error(`Missing or empty evidence: ${file}`);
}

const html = await readFile(path.join(site, 'index.html'), 'utf8');
if (/__\w+__/.test(html)) throw new Error('Unresolved template placeholder in index.html');
const dependencies = [...html.matchAll(/<(?:script|link|img)\b[^>]*?\b(?:src|href)="([^"]+)"/g)].map(m => m[1]);
for (const file of dependencies) {
  if (/^(?:https?:)?\/\//.test(file)) throw new Error(`External runtime dependency: ${file}`);
  if (file.startsWith('data:')) continue;
  await stat(path.join(site, file));
}
for (const match of html.matchAll(/href="(evidence\/[^"#]+)"/g)) {
  if (!evidence.has(match[1].slice('evidence/'.length))) throw new Error(`Unpackaged download: ${match[1]}`);
}

// Only the public site enters dist. Python tooling, the virtual environment,
// old review sessions, and unused diagnostic sheets are not deployed.
await rm(dist, { recursive: true, force: true });
await mkdir(path.join(dist, 'evidence'), { recursive: true });
await cp(path.join(site, 'assets'), path.join(dist, 'assets'), { recursive: true });
await writeFile(path.join(dist, 'index.html'), html);
await Promise.all([...evidence].map(file => cp(path.join(site, 'evidence', file), path.join(dist, 'evidence', file))));
console.log(`Built dist/: ${evidence.size} evidence files, local styles/scripts, and the standalone viewer.`);
