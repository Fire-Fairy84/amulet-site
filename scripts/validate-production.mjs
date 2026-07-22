import fs from 'node:fs';
import path from 'node:path';

const canonicalOrigin = 'https://amulet.cards';
const base = new URL(process.argv[2] ?? canonicalOrigin);
const root = path.resolve(import.meta.dirname, '..');
const errors = [];

function matches(value, expression) { return [...value.matchAll(expression)]; }
function assert(condition, message) { if (!condition) errors.push(message); }
function target(pathname) { return new URL(pathname, base).href; }

async function get(pathname, options = {}) {
  try {
    return await fetch(target(pathname), { redirect: options.redirect ?? 'follow' });
  } catch (error) {
    errors.push(`${pathname}: request failed (${error.message})`);
    return null;
  }
}

async function text(pathname, contentType) {
  const response = await get(pathname);
  if (!response) return '';
  assert(response.status === 200, `${pathname}: expected 200, received ${response.status}`);
  if (contentType) assert(response.headers.get('content-type')?.includes(contentType), `${pathname}: unexpected content-type ${response.headers.get('content-type')}`);
  return response.text();
}

async function pool(items, worker, concurrency = 12) {
  let cursor = 0;
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, async () => {
    while (cursor < items.length) await worker(items[cursor++]);
  }));
}

const sitemapIndex = await text('/sitemap-index.xml', 'xml');
const sitemapChildren = matches(sitemapIndex, /<loc>([^<]+)<\/loc>/g).map((match) => match[1]);
assert(sitemapChildren.length === 1, `sitemap index: expected one child, found ${sitemapChildren.length}`);
assert(sitemapChildren[0] === `${canonicalOrigin}/sitemap-0.xml`, `sitemap index: unexpected child ${sitemapChildren[0]}`);
const sitemap = await text('/sitemap-0.xml', 'xml');
const urls = matches(sitemap, /<loc>([^<]+)<\/loc>/g).map((match) => match[1]);
assert(urls.length === 163, `sitemap: expected 163 URLs, found ${urls.length}`);
assert(new Set(urls).size === urls.length, 'sitemap: duplicate URLs found');
assert(urls.every((url) => url.startsWith(`${canonicalOrigin}/`)), 'sitemap: non-canonical origin found');
assert(urls.filter((url) => /^https:\/\/amulet\.cards\/en\/cards\/[^/]+\/$/.test(url)).length === 78, 'sitemap: expected 78 English card URLs');
assert(urls.filter((url) => /^https:\/\/amulet\.cards\/es\/cartas\/[^/]+\/$/.test(url)).length === 78, 'sitemap: expected 78 Spanish card URLs');

await pool(urls, async (url) => {
  const pathname = new URL(url).pathname;
  const html = await text(pathname, 'text/html');
  assert(html.includes(`<link rel="canonical" href="${url}">`), `${pathname}: missing self-referencing canonical`);
  assert(!/(?:vercel\.app|github\.io)/.test(html), `${pathname}: temporary hosting domain found in HTML`);
});

const robots = await text('/robots.txt', 'text/plain');
assert(robots.includes(`Sitemap: ${canonicalOrigin}/sitemap-index.xml`), 'robots.txt: incorrect sitemap URL');
for (const pathname of ['/en/guides/', '/es/guias/', '/proximamente/']) {
  const html = await text(pathname, 'text/html');
  assert(html.includes('<meta name="robots" content="noindex, follow">'), `${pathname}: missing noindex`);
}
const notFoundPage = await text('/404/', 'text/html');
assert(notFoundPage.includes('<meta name="robots" content="noindex, follow">'), '/404/: missing noindex');
const missingRoute = await get('/__amulet-production-validation-missing__/');
if (missingRoute) assert(missingRoute.status === 404, `missing route: expected 404, received ${missingRoute.status}`);

const cards = fs.readdirSync(path.join(root, 'src/content/cards'))
  .filter((name) => name.endsWith('.json'))
  .map((name) => JSON.parse(fs.readFileSync(path.join(root, 'src/content/cards', name), 'utf8')));
await pool(cards.flatMap((card) => [
  [`/tarot/${card.translations.es.slug}/`, `/es/cartas/${card.translations.es.slug}/`],
  [`/en/tarot/${card.translations.en.slug}/`, `/en/cards/${card.translations.en.slug}/`],
]), async ([source, destination]) => {
  const response = await get(source, { redirect: 'manual' });
  if (!response) return;
  assert(response.status === 308, `${source}: expected 308, received ${response.status}`);
  const location = response.headers.get('location');
  assert(location && new URL(location, base).pathname === destination, `${source}: unexpected Location ${location}`);
  const final = await get(destination);
  if (final) assert(final.status === 200, `${destination}: redirect target returned ${final.status}`);
});

const representative = await text('/en/cards/the-fool/', 'text/html');
for (const expected of [
  `<link rel="alternate" hreflang="en" href="${canonicalOrigin}/en/cards/the-fool/">`,
  `<link rel="alternate" hreflang="es" href="${canonicalOrigin}/es/cartas/el-loco/">`,
  `<link rel="alternate" hreflang="x-default" href="${canonicalOrigin}/">`,
  `<meta property="og:url" content="${canonicalOrigin}/en/cards/the-fool/">`,
  '<meta name="twitter:card" content="summary_large_image">',
  '<script type="application/ld+json">',
]) assert(representative.includes(expected), `/en/cards/the-fool/: missing ${expected}`);

const landing = await text('/', 'text/html');
const assetPaths = new Set(matches(`${landing}\n${representative}`, /(?:href|src)="(\/(?:assets|_astro)\/[^"]+)"/g).map((match) => match[1]));
await pool([...assetPaths], async (pathname) => {
  const response = await get(pathname);
  if (!response) return;
  assert(response.status === 200, `${pathname}: asset returned ${response.status}`);
  const contentType = response.headers.get('content-type') ?? '';
  if (pathname.endsWith('.css')) assert(contentType.includes('text/css'), `${pathname}: unexpected content-type ${contentType}`);
  if (pathname.endsWith('.svg')) assert(contentType.includes('image/svg+xml'), `${pathname}: unexpected content-type ${contentType}`);
  if (pathname.endsWith('.webp')) assert(contentType.includes('image/webp'), `${pathname}: unexpected content-type ${contentType}`);
  if (pathname.startsWith('/assets/')) {
    const cacheControl = response.headers.get('cache-control') ?? '';
    assert(cacheControl.includes('max-age=31536000') && cacheControl.includes('immutable'), `${pathname}: unexpected cache-control ${cacheControl}`);
  }
});

if (errors.length) {
  console.error(`Production validation failed (${errors.length}):\n- ${errors.join('\n- ')}`);
  process.exit(1);
}
console.log(`Validated ${base.origin}: ${urls.length} public URLs, ${cards.length * 2} historical redirects, robots, sitemap, noindex pages, metadata and representative assets.`);
