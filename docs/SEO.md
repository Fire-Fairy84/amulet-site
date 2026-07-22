# SEO de amulet.cards

## Canonical y hreflang

`SeoHead.astro` genera URLs absolutas. Cada página canónica apunta a sí misma. Las páginas de carta incluyen enlaces bidireccionales `en` y `es` a la misma carta usando sus slugs propios, además de `x-default` hacia `/`. Los índices y landings siguen el mismo principio.

No se usa canonical cruzado entre idiomas. La utilidad `src/lib/i18n.ts` concentra la construcción de rutas para impedir divergencias entre navegación, canonical y alternates.

La integración de sitemap no puede relacionar correctamente rutas con segmentos y slugs traducidos (`cards`/`cartas`, `the-fool`/`el-loco`). Por eso no se activa su opción i18n genérica: esa opción produciría alternates incorrectos. Las relaciones completas se publican en el HTML, mientras el sitemap contiene cada URL canónica una vez.

## Metadatos y datos estructurados

Todas las páginas indexables tienen title y description únicos, canonical absoluta, Open Graph, Twitter Card, favicon, Apple touch icon, theme color y robots. Las páginas de carta publican `Article` y `BreadcrumbList`; los índices publican `CollectionPage` con `ItemList`. Solo se incluyen organización, idioma, URL, imagen y texto verificables.

No se añaden autores humanos, ratings, precios, reseñas ni fechas inventadas. El contenido presenta el tarot como simbolismo, reflexión y exploración personal.

## Sitemap y robots

La build genera:

- `https://amulet.cards/sitemap-index.xml`
- `https://amulet.cards/sitemap-0.xml`

`robots.txt` apunta a `sitemap-index.xml` y permite explícitamente Googlebot y OAI-SearchBot. Se excluyen 404, `/proximamente/` y los índices vacíos de guías con `noindex`.

`npm run validate:site` compara las canonicals indexables con todas las URLs del sitemap, valida JSON-LD, alternates de cartas, assets, títulos, descriptions, h1 y enlaces internos.

## Google Search Console

Después del despliegue:

1. Añadir `amulet.cards` como propiedad de dominio.
2. Verificarla con el TXT DNS que proporcione Google.
3. Enviar `https://amulet.cards/sitemap-index.xml`.
4. Solicitar indexación solo de `/`, `/en/cards/`, `/es/cartas/` y unas pocas cartas representativas.
5. Dejar que Google descubra el resto mediante sitemap y enlaces internos; no solicitar cientos de URLs manualmente.

Antes de enviar el sitemap hay que confirmar que el dominio ya sirve el build de Vercel y que las antiguas rutas devuelven redirecciones permanentes.

## Cambios de slug

Un slug público no se elimina sin redirección. Añadir una entrada permanente en `vercel.json`, desplegar, comprobar el status y conservar la redirección mientras la URL antigua tenga enlaces o historial de indexación.

## Comprobaciones

```bash
npm run typecheck
npm run lint
npm run build
git diff --check
```

La build ejecuta automáticamente la validación de contenido antes de Astro y la auditoría HTML/sitemap después.
