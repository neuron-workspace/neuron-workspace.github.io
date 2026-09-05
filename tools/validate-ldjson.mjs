// Every JSON-LD block on the site parses and declares a type.
//
// Structured data fails silently: a trailing comma or a stray quote makes the
// whole block invisible to a crawler, and the page still looks perfect. Run:
//
//   node tools/validate-ldjson.mjs
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

function html(dir = root, found = []) {
  for (const name of readdirSync(dir)) {
    if (name === '.git' || name === 'node_modules' || name === 'fonts') continue;
    const full = join(dir, name);
    if (statSync(full).isDirectory()) html(full, found);
    else if (name.endsWith('.html')) found.push(full);
  }
  return found;
}

let blocks = 0;
const bad = [];

for (const file of html()) {
  const source = readFileSync(file, 'utf-8');
  for (const [, body] of source.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    blocks++;
    try {
      const data = JSON.parse(body);
      if (!data['@context'] || !data['@type']) throw new Error('no @context or @type');
    } catch (error) {
      bad.push(`${relative(root, file)}: ${error.message}`);
    }
  }
}

if (bad.length) {
  console.error(`Invalid structured data:\n  ${bad.join('\n  ')}`);
  process.exit(1);
}
console.log(`structured data: ${blocks} JSON-LD blocks parse and declare a type`);
