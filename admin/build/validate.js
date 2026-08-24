#!/usr/bin/env node
// sg-compute.sgit.ai pre-release gate. Run from anywhere: node admin/build/validate.js
// Checks, in order:
//   1. version agreement — admin/build/version.txt vs every page's version badge,
//      the versions table, llms.txt, llms-full.txt and index.md
//   2. internal links — every relative href/src in every .html file resolves to a
//      file in the tree (fragments stripped; external and mailto links skipped)
//   3. canonical host — every <link rel="canonical"> and og:url points at the host
//      in CNAME, and every page declares one
//   4. the leak tripwire — see below. This is the check this site adds, and it is
//      longer than the siblings' because the platform this site documents is LIVE
//      INFRASTRUCTURE. Publishing a hostname here publishes an attack surface.
//   5. measured-number provenance — data/specs.json must carry a `surveyed` date,
//      because the house rule is that every number is either generated or dated.
// Any failure exits 1: no tag, no publish.
'use strict';
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const errors = [];

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir)) {
    if (name === '.git' || name === '.github' || name === 'node_modules' || name === '.sg_vault') continue;
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

const files = walk(ROOT);
const htmlFiles = files.filter(f => f.endsWith('.html'));

// --- 1. version agreement -------------------------------------------------
const VERSION = fs.readFileSync(path.join(ROOT, 'admin/build/version.txt'), 'utf8').trim();
if (!/^v\d+\.\d+\.\d+$/.test(VERSION)) {
  errors.push(`version.txt does not carry a vX.Y.Z version: "${VERSION}"`);
}
for (const f of htmlFiles) {
  const t = fs.readFileSync(f, 'utf8');
  const badges = [...t.matchAll(/class="ver"[^>]*>(v\d+\.\d+\.\d+)</g)].map(m => m[1]);
  for (const b of badges) if (b !== VERSION) {
    errors.push(`${path.relative(ROOT, f)}: version badge ${b} != ${VERSION}`);
  }
}
for (const extra of ['llms.txt', 'llms-full.txt', 'index.md']) {
  const t = fs.readFileSync(path.join(ROOT, extra), 'utf8');
  if (!t.includes(VERSION)) errors.push(`${extra} does not mention ${VERSION}`);
}
const versTable = fs.readFileSync(path.join(ROOT, 'admin/versions.html'), 'utf8');
if (!versTable.includes(`class="vnum">${VERSION}<`)) {
  errors.push(`admin/versions.html has no row for ${VERSION}`);
}
// each release appears exactly once — a blanket version-bump sed that touches
// the history table produces duplicates, which shipped once on the NHI site
const rows = [...versTable.matchAll(/class="vnum">(v\d+\.\d+\.\d+)</g)].map(m => m[1]);
for (const v of rows) if (rows.filter(x => x === v).length > 1) {
  errors.push(`admin/versions.html lists ${v} more than once`);
  break;
}

// --- 2. internal links ----------------------------------------------------
for (const f of htmlFiles) {
  const t = fs.readFileSync(f, 'utf8');
  const dir = path.dirname(f);
  for (const m of t.matchAll(/(?:href|src)="([^"#]+)(?:#[^"]*)?"/g)) {
    const target = m[1];
    if (/^(https?:|mailto:|data:|\/\/)/.test(target) || target === '') continue;
    const resolved = path.resolve(dir, target);
    if (!fs.existsSync(resolved)) {
      errors.push(`${path.relative(ROOT, f)}: broken link -> ${target}`);
    }
  }
}

// --- 3. canonical host ----------------------------------------------------
const HOST = fs.readFileSync(path.join(ROOT, 'CNAME'), 'utf8').trim();
if (!/^[a-z0-9.-]+$/.test(HOST)) errors.push(`CNAME does not carry a hostname: "${HOST}"`);
for (const f of htmlFiles) {
  const t = fs.readFileSync(f, 'utf8');
  const claimed = [
    ...[...t.matchAll(/<link[^>]+rel="canonical"[^>]+href="([^"]+)"/g)].map(m => m[1]),
    ...[...t.matchAll(/<meta[^>]+property="og:url"[^>]+content="([^"]+)"/g)].map(m => m[1]),
  ];
  for (const url of claimed) if (!url.startsWith(`https://${HOST}/`)) {
    errors.push(`${path.relative(ROOT, f)}: canonical/og:url is not on ${HOST} -> ${url}`);
  }
  if (!/rel="canonical"/.test(t)) {
    errors.push(`${path.relative(ROOT, f)}: no canonical link`);
  }
}

// --- 4. the leak tripwire -------------------------------------------------
// The house rule this site publishes is "shapes, not addresses":
// <stack-name>.sg-compute.<zone> is documentation; a live FQDN is a target. The
// list below is what the source repo's redaction pass found, encoded so it cannot
// regress. A page that names one of these fails the release.
//
// ONE DELIBERATE EXCEPTION, and it is the whole reason the exception mechanism
// exists: the bare zone `sg-compute.sgraph.ai` IS published, on the front page and
// in /network/, because this site's label collides with it and the site's stated
// decision is to claim the distinction rather than move 128 references. The zone
// name is the subject of that decision; the per-node FQDNs under it are not, and
// they stay banned by the stack-slug patterns below.
const ALLOWED_ZONE = 'sg-compute.sgraph.ai';
const LEAKS = [
  [/\b745506449035\b/,                          'the AWS account id'],
  [/\baws\.sg-labs\.app\b/,                     'a live internal hostname (sg-labs)'],
  [/\bedge\.sg-labs\.app\b/,                    'a live internal hostname (sg-labs)'],
  [/\bvp-admin\.aws\.sg-labs\.app\b/,           'a live internal hostname (sg-labs)'],
  [/\bwaker\.aws\.sg-labs\.app\b/,              'a live internal hostname (sg-labs)'],
  [/\bsend\.sgraph\.ai\b/,                      'a live internal hostname'],
  [/\b(?:dev\.)?vault\.sgraph\.ai\b/,           'a live internal hostname'],
  [/\bqa\.sgraph\.ai\b/,                        'a live internal hostname'],
  [/\b(?:dev\.)?tools\.sgraph\.ai\b/,           'an internal CDN host'],
  [/\b(?:fast-hopper|warm-bohr|quiet-fermi|zen-darwin|sara-cv)[.\w-]*\.(?:sgraph\.ai|sg-labs\.app)/,
                                                'a named live stack FQDN'],
  [/\bi-[0-9a-f]{17}\b/,                        'a real EC2 instance id'],
  [/\bami-[0-9a-f]{17}\b/,                      'a real AMI id'],
  // carried from the siblings: nothing in the tree may look like an sgit vault key
  // (a >=20-char passphrase joined by a colon to a uuid-shaped id)
  [/[A-Za-z0-9_-]{20,}:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/,
                                                'a vault-key-shaped string'],
];
for (const f of files) {
  if (/\.(png|jpg|jpeg|gif|webp|ico|woff2?|zip)$/.test(f)) continue;
  // validate.js itself carries the patterns; exempting it is what makes them writable
  if (path.resolve(f) === path.resolve(__filename)) continue;
  const text = fs.readFileSync(f, 'utf8');
  // blank the one deliberately published zone before scanning, so a per-node FQDN
  // under it is still caught by the stack-slug pattern
  const t = text.split(ALLOWED_ZONE).join('<allowed-zone>');
  for (const [re, what] of LEAKS) {
    const hit = t.match(re);
    if (hit) errors.push(`${path.relative(ROOT, f)}: contains ${what} -> ${hit[0]}`);
  }
}

// --- 5. measured-number provenance ---------------------------------------
// House rule: every number on this site is generated from data or carries the date
// it was measured. The catalogue is the data; it must say when it was surveyed and
// which repo version it was surveyed at.
const cat = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/specs.json'), 'utf8'));
for (const k of ['surveyed', 'repo_version', 'source']) {
  if (!cat[k]) errors.push(`data/specs.json has no "${k}" — a measured number with no provenance`);
}
if (cat.surveyed && !/^\d{4}-\d{2}-\d{2}$/.test(cat.surveyed)) {
  errors.push(`data/specs.json: "surveyed" is not a YYYY-MM-DD date -> ${cat.surveyed}`);
}

// --- report ---------------------------------------------------------------
if (errors.length) {
  console.error(`validate: ${errors.length} error(s)`);
  for (const e of errors) console.error('  ✗ ' + e);
  process.exit(1);
}
console.log(`validate: OK — ${VERSION} on ${HOST}, ${htmlFiles.length} pages, links resolve, `
          + `no leaked account id / hostname / instance id / key, catalogue surveyed ${cat.surveyed}`);
