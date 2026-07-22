import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const dist = path.join(root, 'dist');
const site = 'https://amulet.cards';
const errors = [];
const warnings = [];

function walk(directory, extension, result = []) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(target, extension, result);
    else if (target.endsWith(extension)) result.push(target);
  }
  return result;
}

function matches(html, expression) { return [...html.matchAll(expression)]; }
function attr(html, expression) { return html.match(expression)?.[1] ?? null; }
function isFile(file) { return fs.existsSync(file) && fs.statSync(file).isFile(); }
function routeFor(file) {
  const relative = path.relative(dist, file).split(path.sep).join('/');
  if (relative === 'index.html') return '/';
  if (relative === '404.html') return '/404/';
  return `/${relative.replace(/index\.html$/, '')}`;
}
function fileForRoute(route) {
  const clean = route.replace(/^\//, '').replace(/\?.*$/, '').replace(/#.*$/, '');
  return path.join(dist, clean.endsWith('/') || clean === '' ? `${clean}index.html` : clean);
}

if (!fs.existsSync(dist) || !fs.statSync(dist).isDirectory()) throw new Error('dist/ does not exist; run astro build first');
const htmlFiles = walk(dist, '.html');
const pages = htmlFiles.map((file) => ({ file, route: routeFor(file), html: fs.readFileSync(file, 'utf8') }));
const titles = new Map();
const descriptions = new Map();
const canonicals = new Set();

for (const page of pages) {
  const h1s = matches(page.html, /<h1(?:\s[^>]*)?>/gi).length;
  if (h1s !== 1) errors.push(`${page.route}: expected one h1, found ${h1s}`);
  const title = attr(page.html, /<title>([^<]+)<\/title>/i);
  const description = attr(page.html, /<meta name="description" content="([^"]+)"/i);
  const canonical = attr(page.html, /<link rel="canonical" href="([^"]+)"/i);
  const robots = attr(page.html, /<meta name="robots" content="([^"]+)"/i) ?? '';
  if (!title || !description || !canonical) errors.push(`${page.route}: missing title, description, or canonical`);
  const expectedCanonical = new URL(page.route, site).href;
  if (canonical !== expectedCanonical) errors.push(`${page.route}: canonical ${canonical} does not point to itself (${expectedCanonical})`);
  if (canonical) canonicals.add(canonical);
  if (!robots.includes('noindex')) {
    if (title) titles.set(title, [...(titles.get(title) ?? []), page.route]);
    if (description) descriptions.set(description, [...(descriptions.get(description) ?? []), page.route]);
    for (const required of ['og:title', 'og:description', 'og:url', 'og:image']) {
      if (!page.html.includes(`property="${required}"`)) errors.push(`${page.route}: missing ${required}`);
    }
  }
  for (const script of matches(page.html, /<script[^>]+type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi)) {
    try { JSON.parse(script[1]); } catch (error) { errors.push(`${page.route}: invalid JSON-LD (${error.message})`); }
  }
  if (/\b(?:TODO|TBD)\b/.test(page.html) || /\b(?:lorem ipsum|placeholder)\b/i.test(page.html)) errors.push(`${page.route}: visible placeholder marker found`);
}

for (const [title, routes] of titles) if (routes.length > 1) errors.push(`duplicate title “${title}”: ${routes.join(', ')}`);
for (const [description, routes] of descriptions) if (routes.length > 1) errors.push(`duplicate description “${description.slice(0, 80)}…”: ${routes.join(', ')}`);
if (canonicals.size !== pages.length) errors.push(`canonical count ${canonicals.size} differs from page count ${pages.length}`);

for (const page of pages) {
  for (const match of matches(page.html, /<a\s[^>]*href="([^"]+)"/gi)) {
    const href = match[1];
    if (/^(?:https?:|mailto:|tel:)/.test(href)) continue;
    const resolved = new URL(href, `${site}${page.route}`);
    const targetFile = fileForRoute(resolved.pathname);
    if (!fs.existsSync(targetFile)) errors.push(`${page.route}: broken internal link ${href}`);
    if (resolved.hash && fs.existsSync(targetFile)) {
      const targetHtml = fs.readFileSync(targetFile, 'utf8');
      const id = decodeURIComponent(resolved.hash.slice(1)).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      if (!new RegExp(`id="${id}"`).test(targetHtml)) errors.push(`${page.route}: missing fragment target ${href}`);
    }
  }
  for (const match of matches(page.html, /<(?:img|source)\s[^>]*(?:src|srcset)="([^"\s,]+)/gi)) {
    const asset = match[1];
    if (asset.startsWith('/') && !fs.existsSync(path.join(dist, asset))) errors.push(`${page.route}: missing asset ${asset}`);
  }
}

const cardFiles = walk(path.join(root, 'src/content/cards'), '.json');
const cards = cardFiles.map((file) => JSON.parse(fs.readFileSync(file, 'utf8')));
for (const card of cards) {
  const enRoute = `/en/cards/${card.translations.en.slug}/`;
  const esRoute = `/es/cartas/${card.translations.es.slug}/`;
  const enHtml = fs.readFileSync(fileForRoute(enRoute), 'utf8');
  const esHtml = fs.readFileSync(fileForRoute(esRoute), 'utf8');
  if (!enHtml.includes('<html lang="en">') || !enHtml.includes(`<h1>${card.translations.en.name}</h1>`)) errors.push(`${enRoute}: English language or translated h1 mismatch`);
  if (!esHtml.includes('<html lang="es">') || !esHtml.includes(`<h1>${card.translations.es.name}</h1>`)) errors.push(`${esRoute}: Spanish language or translated h1 mismatch`);
  for (const [route, html] of [[enRoute, enHtml], [esRoute, esHtml]]) {
    for (const [lang, target] of [['en', enRoute], ['es', esRoute]]) {
      const expected = `<link rel="alternate" hreflang="${lang}" href="${site}${target}">`;
      if (!html.includes(expected)) errors.push(`${route}: missing bidirectional hreflang ${lang} -> ${target}`);
    }
  }
}

const vercel = JSON.parse(fs.readFileSync(path.join(root, 'vercel.json'), 'utf8'));
const redirectSignature = new Set(vercel.redirects.map((redirect) => `${redirect.source}|${redirect.destination}|${redirect.permanent}`));
for (const signature of [
  '/tarot|/es/cartas/|true', '/tarot/:slug|/es/cartas/:slug/|true',
  '/en/tarot|/en/cards/|true', '/en/tarot/:slug|/en/cards/:slug/|true',
]) if (!redirectSignature.has(signature)) errors.push(`missing historical Vercel redirect: ${signature}`);

const sitemapIndex = path.join(dist, 'sitemap-index.xml');
if (!isFile(sitemapIndex)) errors.push('missing sitemap-index.xml');
const sitemapFiles = fs.existsSync(sitemapIndex)
  ? matches(fs.readFileSync(sitemapIndex, 'utf8'), /<loc>([^<]+\.xml)<\/loc>/g).map((match) => path.join(dist, new URL(match[1]).pathname.slice(1)))
  : [];
const sitemapUrls = new Set();
for (const file of sitemapFiles) {
  if (!isFile(file)) errors.push(`missing sitemap child ${file}`);
  else for (const match of matches(fs.readFileSync(file, 'utf8'), /<loc>(https:\/\/amulet\.cards\/[^<]*)<\/loc>/g)) sitemapUrls.add(match[1]);
}
for (const page of pages) {
  const robots = attr(page.html, /<meta name="robots" content="([^"]+)"/i) ?? '';
  const canonical = attr(page.html, /<link rel="canonical" href="([^"]+)"/i);
  if (!robots.includes('noindex') && canonical && !sitemapUrls.has(canonical)) errors.push(`${page.route}: public canonical absent from sitemap`);
  if (robots.includes('noindex') && canonical && sitemapUrls.has(canonical)) errors.push(`${page.route}: noindex URL present in sitemap`);
}
const robotsText = fs.readFileSync(path.join(dist, 'robots.txt'), 'utf8');
if (!robotsText.includes('Sitemap: https://amulet.cards/sitemap-index.xml')) errors.push('robots.txt does not point to the real sitemap');
if (!robotsText.includes('OAI-SearchBot') || !robotsText.includes('Googlebot')) errors.push('robots.txt lacks explicit Googlebot or OAI-SearchBot access');

if (warnings.length) console.warn(`Warnings:\n- ${warnings.join('\n- ')}`);
if (errors.length) {
  console.error(`Site validation failed (${errors.length}):\n- ${errors.join('\n- ')}`);
  process.exit(1);
}
console.log(`Validated ${pages.length} HTML pages, ${cards.length} cards, ${sitemapUrls.size} sitemap URLs, canonicals, hreflang, JSON-LD, assets and internal links.`);
